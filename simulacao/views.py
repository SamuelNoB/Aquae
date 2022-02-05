from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.views.generic import TemplateView
from django.forms import inlineformset_factory, formset_factory
from numpy.lib.function_base import diff
from requests.api import get


from .forms import EdificacaoForm, DemandasForm, DemandaSimulacaoAAPForm, SimulacaoAAPForm, OfertasForm
from .models import DemandasDeAgua, Simulacao, OfertasDeAgua
from .base_de_dados.models import Equipamentos, IndicePluviometrico, CaixaDAgua, CapacidadeDeTratamento, TarifaDeAgua, Cidade
from .utils import get_dollar

from .controllers.dimensionamentoController import DimensionamentoController
from .controllers.demandaController import DemandaController
from .controllers.ofertaController import OfertaController
from .controllers.economiaDeAguaController import EconomiaDeAguaController
from .controllers.beneficioController import BeneficioController
from .controllers import simuladorController

import simulacao

from math import ceil
import numpy as np
import json
# Create your views here.


def edificacao(request):
    context = {}
    consumo_factory = inlineformset_factory(Simulacao,
                                            DemandasDeAgua,
                                            form=DemandasForm,
                                            can_delete=True,
                                            )
    novos_consumos = consumo_factory
    nova_edificacao = EdificacaoForm
    context['nova_edificacao'] = nova_edificacao


    if request.method == 'POST':
        nova_edificacao = nova_edificacao(request.POST)
        novos_consumos = novos_consumos(request.POST)
        if nova_edificacao.is_valid() and novos_consumos.is_valid():
            uma_edificacao = nova_edificacao.save()
            novos_consumos.instance = uma_edificacao
            novos_consumos.save()
            return redirect('simulacao:seleciona_simulacao', pk=uma_edificacao.pk)
        else:
            context['nova_edificacao'] = nova_edificacao
            return render(request, 'edificacao.html', context)


    return render(request, 'edificacao.html', context)


def seleciona_simulacao(request, pk):
    return render(request, 'seleciona_simulacao.html', {'pk': pk})


def RACform(request, pk):
    oferta_factory = inlineformset_factory(Simulacao,
                                           OfertasDeAgua,
                                           fields='__all__')
    try:
        simul_id = Simulacao.objects.get(id=pk)
    except simulacao.models.Simulacao.DoesNotExist:
        return redirect('simulacao:edificacao')
    
    ofertas_avancado = OfertasDeAgua.objects.filter(simulacao=pk)
    if ofertas_avancado:
        return redirect('simulacao:simulacao-rac', pk=pk)
   


    oferta_factory(instance=simul_id)
    if request.method == "POST":
        novas_ofertas = oferta_factory(request.POST, instance=simul_id)
        if novas_ofertas.is_valid():
            novas_ofertas.save()
            return redirect('simulacao:simulacao-rac', pk=pk)

    return render(request, 'RAC-form.html', {'pk': pk})


class SimulacaoAAP(TemplateView):
    template_name = 'simuladorAAP.html' 


    def get_pluviometria(self, cidade="Brasília"):
        local = Cidade.objects.get(nome=cidade)
        pluviometria = IndicePluviometrico.objects.filter(ano=2019, cidade=local)
        pluviometria = pluviometria.values_list('media_pluviometrica')
        pluviometria = list(map(lambda x:x[0], pluviometria))
        return pluviometria


    def get_equips(self, area_coleta):
        todas = Equipamentos.objects.all()

        possiveis = list(todas.filter(area_de_coleta__lt=area_coleta))
        if len(possiveis) < len(todas):
                possiveis.append(todas[len(possiveis)])
        
        equips_dict = {equip.area_de_coleta.area_max: {
                                                        'filtro': equip.filtro_dagua,
                                                        'freio': equip.freio_dagua,
                                                        'sifao': equip.sifao_ladrao,
                                                        'custo': equip.custo_implementacao
                                                        }  for equip in possiveis}
        
        return equips_dict


    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')

        try:
            simul = simuladorController.get_simulacao(pk=pk)['simulacao']
        except simulacao.models.Simulacao.DoesNotExist:
            return redirect('simulacao:edificacao')
        area_i = simul.area_irrigacao
        area_p = simul.area_pisos
        area_c = simul.area_cobertura
        consumo = simul.consumo_mensal
        esgoto = simul.tarifa_esgoto / 100
        pessoas = simul.n_pessoas
        n_pavimentos = simul.n_pavimentos
        coeficiente_esc = 0.9
        coeficiente_filt = 0.9


        individual_d, geral_demanda, irrigacao = simuladorController.calc_oferta_demanda(pk, 'demandas_de_agua',
                                                                                   residentes=pessoas,
                                                                                   area_irrigacao=area_i,
                                                                                   area_pisos=area_p)
        geral_demanda = round(geral_demanda, 2)
        irrigacao = round(irrigacao, 2)


        # TODO Versoes futuras devem especificar cidade
        pluviometria = np.array(self.get_pluviometria())
        pluviometria_total = pluviometria.sum()
        area_ideal = ceil(geral_demanda / (pluviometria_total * coeficiente_esc * coeficiente_filt) * 1000)
        area_coleta = min(area_ideal, area_c)
        
        oferta_mensal = pluviometria * area_coleta * coeficiente_esc * coeficiente_filt / 1000
        oferta_mensal = np.around(oferta_mensal, decimals=2)
        oferta_total = round(oferta_mensal.sum(), 2)

        demanda_sest = round((geral_demanda - irrigacao*5)/12, 2) # periodo sem estiagem
        demanda_est = demanda_sest + irrigacao # periodo de estiagem
        demanda_mensal = np.array([demanda_sest for i in range(12)])
        meses_est = np.where(pluviometria < 50)
        demanda_mensal[meses_est] = demanda_est

        # JS nao recebe np arrray
        demanda_mensal = list(demanda_mensal)
        oferta_mensal = list(oferta_mensal)
        meses_est = list(meses_est[0])
        pluviometria = list(pluviometria)

        dolar = get_dollar()
        bomba, co = simuladorController.get_bomba_e_co(n_pavimentos)
        equips = self.get_equips(area_coleta)
        # m³ para litros / dia
        demanda_g_ld = demanda_est * 1000 / 30
        volumes_caixa, financeiro_caixa = simuladorController.get_caixa_dagua(demanda_g_ld, dolar)
        
        tarifa = simuladorController.get_tarifa(consumo)* (1 + esgoto)
        

        context = {
            'pk' : pk,
            'individual_d' : individual_d,
            'geral_demanda' : [geral_demanda],
            'oferta_total': [oferta_total],
            'demanda_mensal': demanda_mensal,
            'oferta_mensal': oferta_mensal,
            'meses_estiagem': meses_est,
            'area_disponivel': [area_c],
            'area_coleta': area_coleta,
            'pluviometria_mensal': pluviometria,
            'pluviometria_total': pluviometria_total,
            'equipamentos': json.dumps(equips),
            'bomba': {
                'dimensoes': bomba,
                'custo_op': co,
                'preco': bomba.preco/3.77
            },
            'caixa': {
                'volumes': volumes_caixa,
                'financeiro': financeiro_caixa
            },
            'tarifa': tarifa,
            'dolar': dolar
        }

        return render(request, self.template_name, context)


class SimulacaoRAC(TemplateView):
    template_name = 'simuladorRAC.html'
    

    def get_simulacao(self, pk):
        return {
            'simulacao': Simulacao.objects.get(pk=pk),
            'demandas_de_agua': DemandasDeAgua.objects.filter(simulacao=pk),
            'ofertas_de_agua': OfertasDeAgua.objects.filter(simulacao=pk)
        }

    
    def calc_oferta_demanda(self, pk, interesse, **kwargs):
        ofertas = self.get_simulacao(pk)[interesse]

        individual = {}
        geral = 0


        for oferta in ofertas:
            agua = (oferta.indicador * oferta.frequencia_mensal)/1000 * kwargs['residentes']
            if oferta.nome == "Irrigação de jardins":
                agua = agua / 12 * 5 * kwargs['area_irrigacao']
            elif oferta.nome == "Lavagem de pisos":
                agua = agua * kwargs['area_pisos'] 
            agua = round(agua, 2)
            geral += agua 
            individual[oferta.nome] = agua

        geral = geral*12 # m³/ano
        # individual em m³/mes
        return individual, geral
    

    def get_capacidade(self, demanda, dolar):
        todas = CapacidadeDeTratamento.objects.all()
        
        # Capacidades suficientes para uma demanda menor que a especificada no formulario
        possiveis = list(todas.filter(volume__lt = demanda))

        if len(possiveis) < len(todas):
            # Capacidade suficiente para a demanda especificada no formulario
            possiveis.append(todas[len(possiveis)])

        capacidade_dict = {capacidade.volume: [capacidade.valor * dolar, capacidade.custo_operacional * dolar] for capacidade in possiveis}

        return list(capacidade_dict.keys()), capacidade_dict


    def get_bomba_e_co(self, n_pavimentos):
        # Area de coleta faz-se desprezivel para o RAC
        Dimensionamento = DimensionamentoController(area_coleta=0, pavimentos=n_pavimentos)
        bomba = Dimensionamento.get_bomba_dagua()
        co = Dimensionamento.get_custo_operacional()
        return bomba, co


    def get_caixa_dagua(self, demanda_diaria, dolar):
        todas = CaixaDAgua.objects.all()
        possiveis = list(todas.filter(volume__lt=demanda_diaria))
        
        if len(possiveis) < len(todas):
            possiveis.append(todas[len(possiveis)])
        
        caixas_dict = {caixa.volume: caixa.valor * dolar for caixa in possiveis}
        return list(caixas_dict.keys()), caixas_dict


    def get_tarifa(self, consumo):
        tarifa = TarifaDeAgua.objects.filter(min__lte=consumo,
                                             max__gte=consumo)
        return list(tarifa)[0].tarifa


    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk') 

        try:
            simul = self.get_simulacao(pk=pk)['simulacao']
        except simulacao.models.Simulacao.DoesNotExist:
            return redirect('simulacao:edificacao')
        area_i = simul.area_irrigacao
        area_p = simul.area_pisos
        consumo = simul.consumo_mensal
        esgoto = simul.tarifa_esgoto / 100
        pessoas = simul.n_pessoas

        # Se a simulacao foi encontrada, entao o form da demanda foi preenchido
        individual_demanda, geral_demanda = self.calc_oferta_demanda(pk, 'demandas_de_agua', 
                                                                     area_irrigacao=area_i,
                                                                     area_pisos=area_p,
                                                                     residentes=pessoas)

        # Buscar uma oferta em uma simulacao existente nao retorna erro
        individual_oferta, geral_oferta = self.calc_oferta_demanda(pk, 'ofertas_de_agua', 
                                                                   area_irrigacao=area_i,
                                                                   area_pisos=area_p,
                                                                   residentes=pessoas)
        if not individual_oferta:
            return redirect('simulacao:formulario-rac', pk=pk)

        dolar = get_dollar()

        n_pavimentos = simul.n_pavimentos
        bomba, custo_op = self.get_bomba_e_co(n_pavimentos=n_pavimentos)
   

        # m³ para litros / dia
        demanda_g_ld = geral_demanda * 1000 / (12 * 30)
        volumes_cap, financeiro_cap = self.get_capacidade(demanda_g_ld, dolar=dolar)
        volumes_caixa, financeiro_caixa = self.get_caixa_dagua(demanda_g_ld, dolar=dolar)
        
        tarifa = self.get_tarifa(consumo) * (1 + esgoto)


        context = {
            'pk': self.kwargs.get("pk"),
            'individual_o' : individual_oferta,
            'geral_o' : round(geral_oferta, 2),
            'individual_d' : individual_demanda,
            'geral_d' : round(geral_demanda, 2),
            'tratamento': {
                'Volumes': volumes_cap,
                'Financeiro': financeiro_cap},
            'bomba': {
                'Dimensoes': bomba,
                'Custo_op': [custo_op],
                'Custo': [bomba.preco]
            },
            'caixa': {
                'Volumes': volumes_caixa,
                'Financeiro': financeiro_caixa
            },
            'tarifa': [tarifa]
        }

        return render(request, self.template_name, context)