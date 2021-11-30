from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.views.generic import TemplateView
from django.forms import inlineformset_factory, formset_factory
from requests.api import get


from .forms import EdificacaoForm, DemandasForm, DemandaSimulacaoAAPForm, SimulacaoAAPForm, OfertasForm
from .models import DemandasDeAgua, Simulacao, OfertasDeAgua
from .base_de_dados.models import IndicePluviometrico, CaixaDAgua, CapacidadeDeTratamento, TarifaDeAgua
from .utils import get_dollar

from .controllers.dimensionamentoController import DimensionamentoController
from .controllers.demandaController import DemandaController
from .controllers.ofertaController import OfertaController
from .controllers.economiaDeAguaController import EconomiaDeAguaController
from .controllers.beneficioController import BeneficioController


import simulacao
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

    def calcula_vpl(self, c_capital, c_operacional, beneficio, juros=0):
        resultado = 0
        somatorio = 0
        for i in range(1, 31):
            somatorio += (c_operacional - beneficio) / (1 + juros) ** i
        return round(abs(c_capital + somatorio), 2)

    def demandas_to_dict(self, demandas_da_simulacao):
        demandas = []
        for demanda in demandas_da_simulacao:
            demandas.append({"ativo": True, "demanda_mensal": demanda.demanda_mensal, "nome_consumo": demanda.nome})
        return demandas

    def get_simulacao_e_demanda(self, pk):
        return {
            'simulacao': Simulacao.objects.get(pk=pk),
            'demandas_de_agua': DemandasDeAgua.objects.filter(simulacao=pk)
        }

    def calcula_demandas_mensais(self, uma_simulacao):
        calcula_demandas = DemandaController(uma_simulacao['demandas_de_agua'], uma_simulacao['simulacao'])
        for demanda in uma_simulacao['demandas_de_agua']:
            indicador_equivalente = calcula_demandas.get_indicador_equivalente(demanda)
            demanda.demanda_mensal = calcula_demandas \
                .calcula_demanda_mensal(indicador_equivalente, demanda.frequencia_mensal)

        return calcula_demandas

    def get_demanda_anual(self, uma_simulacao):
        calcula_demandas = self.calcula_demandas_mensais(uma_simulacao)
        return calcula_demandas.sum_demandas_anuais()

    def make_calculadora_oferta(self, uma_simulacao, demanda_anual):
        indices_pluviometricos = IndicePluviometrico.objects.filter(ano=2019)
        calculador = OfertaController(
            area_cobertura=uma_simulacao['simulacao'].area_cobertura,
            demanda_anual=demanda_anual,
            indices_pluviometricos=indices_pluviometricos
        )

        return calculador

    def generate_dimensionamento(self, area_cobertura, uma_simulacao):
        dimensionamento = DimensionamentoController(area_coleta=area_cobertura, pavimentos=uma_simulacao['simulacao'].n_pavimentos)
        dimensionamento_basico = dimensionamento.get_dimensionamentos()
        return dimensionamento, dimensionamento_basico

    def get(self, request, *args, **kwargs):
        pk = kwargs.pop('pk')

        uma_simulacao = self.get_simulacao_e_demanda(pk)
        demanda_anual = self.get_demanda_anual(uma_simulacao)

        demanda_control = DemandaController(uma_simulacao['demandas_de_agua'], uma_simulacao['simulacao'])
        demandas_seca_chuva = demanda_control.mock_demandas_mensais()

        calculador = self.make_calculadora_oferta(uma_simulacao, demanda_anual)
        area_cobertura = calculador.area_cobertura
        oferta_anual = calculador.get_oferta_anual()



        dimensionamento, dimensionamento_basico = self.generate_dimensionamento(area_cobertura,
                                                                                uma_simulacao)
        bomba_de_agua = dimensionamento.get_bomba_dagua()
        bomba_de_agua.custo_operacional = dimensionamento.get_custo_operacional()

        consumo_factory = formset_factory(form=DemandaSimulacaoAAPForm, extra=0)
        demandas_para_mostrar = consumo_factory(initial=self.demandas_to_dict(uma_simulacao['demandas_de_agua']))
        simulacaoForm = SimulacaoAAPForm()
        economia_de_agua = EconomiaDeAguaController(calculador.generate_ofertas_mensais(),
                                                    demandas_seca_chuva,
                                                    5,
                                                    demanda_anual
                                                    )
        grafico_data = economia_de_agua.gera_grafico_data()
        beneficio_controller = BeneficioController(grafico_data['economias'],
                                                   tarifa_esgoto=uma_simulacao['simulacao'].tarifa_esgoto
                                                   )

        volume_min_reservatorio = (demanda_anual / 365) * 1000
        reservatorio = CaixaDAgua.objects.get(min__lte=volume_min_reservatorio,
                                              max__gte=volume_min_reservatorio)
        preco_base = reservatorio.valor + dimensionamento_basico.custo_implementacao + bomba_de_agua.preco
        preco_cisterna_por_m3 = 324.95
        custos = []
        dollar = get_dollar()
        for volume in grafico_data['volumes'][1:]:
            preco_total = round(preco_base + (preco_cisterna_por_m3 * volume) * dollar, 2)
            custos.append(preco_total )

        beneficios = beneficio_controller.itera_economias()

        paybacks = []
        for i in range(0,len(custos)):
            payback = round(custos[i] / beneficios[i])
            paybacks.append(payback)

        vpls = []
        for custo, beneficio in zip(custos, beneficios):
            vpl = self.calcula_vpl(custo, bomba_de_agua.custo_operacional, beneficio, 0.03)
            vpls.append(vpl)

        tabela_data = zip(grafico_data['volumes'][1:], beneficios, custos, paybacks, vpls)

        demanda_anual = round(demanda_anual, 2)




        context = {
            'pk': pk,
            'simulacaoForm': simulacaoForm,
            'demandas_de_agua': demandas_para_mostrar,
            'grafico_data': {
                'volumes': grafico_data['volumes'],
                'economias': grafico_data['economias'],
                'beneficios': beneficios,
            },
            'tabela_data': tabela_data,
            'geral_data': {
                'demanda_total': demanda_anual,
                'area_cobertura': area_cobertura,
                'oferta_anual': oferta_anual,
                'custo_operacional': bomba_de_agua.custo_operacional
            },
            'dimensionamento': {
                "filtro_dagua": dimensionamento_basico.filtro_dagua,
                "sifao_ladrao": dimensionamento_basico.sifao_ladrao,
                "freio_dagua": dimensionamento_basico.freio_dagua,
                "succao": bomba_de_agua.succao,
                "recalque": bomba_de_agua.recalque,
                "potencia": bomba_de_agua.potencia,
                "reservatorio": reservatorio.volume
            }
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        pk = kwargs.pop('pk')
        uma_simulacao = self.get_simulacao_e_demanda(pk)

        consumo_factory = formset_factory(form=DemandaSimulacaoAAPForm, extra=0)
        demandas_para_mostrar = consumo_factory(request.POST)
        simulacaoForm = SimulacaoAAPForm(request.POST)

        demanda_anual = 0
        copy_demandas = uma_simulacao['demandas_de_agua']

        if demandas_para_mostrar.is_valid() and simulacaoForm.is_valid():
            demandas_validadas = demandas_para_mostrar.cleaned_data
            for demanda in demandas_validadas:
                if demanda['ativo']:
                    if demanda['nome_consumo'] == 'Irrigação de jardins':
                        demanda_anual += demanda['demanda_mensal'] * 5
                    else:
                        demanda_anual += demanda['demanda_mensal'] * 12
                else:
                    copy_demandas = copy_demandas.exclude(nome=demanda['nome_consumo'])

        calculador = self.make_calculadora_oferta(uma_simulacao, demanda_anual)
        area_cobertura = calculador.area_cobertura
        oferta_anual = calculador.get_oferta_anual()
        dimensionamento, dimensionamento_basico = self.generate_dimensionamento(area_cobertura,
                                                                                uma_simulacao)

        demanda_control = DemandaController(copy_demandas, uma_simulacao['simulacao'])
        demandas_seca_chuva = demanda_control.mock_demandas_mensais()

        bomba_de_agua = dimensionamento.get_bomba_dagua()
        bomba_de_agua.custo_operacional = dimensionamento.get_custo_operacional()
        economia_de_agua = EconomiaDeAguaController(calculador.generate_ofertas_mensais(),
                                                    demandas_seca_chuva,
                                                    simulacaoForm.cleaned_data['intervalos_de_cisterna'],
                                                    demanda_anual
                                                    )
        grafico_data = economia_de_agua.gera_grafico_data()
        beneficio_controller = BeneficioController(grafico_data['economias'],
                                                   tarifa_esgoto=uma_simulacao['simulacao'].tarifa_esgoto
                                                   )

        volume_min_reservatorio = (demanda_anual / 365) * 1000
        reservatorio = CaixaDAgua.objects.get(min__lte=volume_min_reservatorio,
                                              max__gte=volume_min_reservatorio)
        preco_base = reservatorio.valor + dimensionamento_basico.custo_implementacao + bomba_de_agua.preco
        preco_cisterna_por_m3 = 324.95
        custos = []
        dollar = get_dollar()
        for volume in grafico_data['volumes'][1:]:
            preco_total = round(preco_base + (preco_cisterna_por_m3 * volume) * dollar, 2)
            custos.append(preco_total)
        beneficios = beneficio_controller.itera_economias()

        paybacks = []
        for i in range(0, len(custos)):
            payback = round(custos[i] / beneficios[i])
            paybacks.append(payback)

        vpls = []
        juros = simulacaoForm.cleaned_data['taxa_de_juros']/100
        for custo, beneficio in zip(custos, beneficios):
            vpl = self.calcula_vpl(custo, bomba_de_agua.custo_operacional, beneficio, juros)
            vpls.append(vpl)

        tabela_data = zip(grafico_data['volumes'][1:], beneficios, custos, paybacks, vpls)


        context = {
            'pk': pk,
            'simulacaoForm': simulacaoForm,
            'demandas_de_agua': demandas_para_mostrar,
            'grafico_data': {
                'volumes': grafico_data['volumes'],
                'economias': grafico_data['economias'],
                'beneficios': beneficios,
            },
            'tabela_data': tabela_data,
            'geral_data': {
                'demanda_total': round(demanda_anual, 2),
                'area_cobertura': area_cobertura,
                'oferta_anual': oferta_anual,
                'custo_operacional': bomba_de_agua.custo_operacional
            },
            'dimensionamento': {
                "filtro_dagua": dimensionamento_basico.filtro_dagua,
                "sifao_ladrao": dimensionamento_basico.sifao_ladrao,
                "freio_dagua": dimensionamento_basico.freio_dagua,
                "succao": bomba_de_agua.succao,
                "recalque": bomba_de_agua.recalque,
                "potencia": bomba_de_agua.potencia,
                "reservatorio": reservatorio.volume
            }
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

        # Gambiarra para nao alterar o resultado da demanda
        if interesse == "demandas_de_agua":
            kwargs["residentes"] = 1


        for oferta in ofertas:
            agua = (oferta.indicador * oferta.frequencia_mensal)/1000 * kwargs['residentes']
            if oferta.nome == "Irrigação de jardins":
                agua = agua / 12 * 5 * kwargs['area_irrigacao']
            elif oferta.nome == "Lavagem de pisos":
                agua = agua * kwargs['area_pisos'] 
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
                                                                     area_pisos=area_p)

        # Buscar uma oferta em uma simulacao existente nao retorna erro
        individual_oferta, geral_oferta = self.calc_oferta_demanda(pk, 'ofertas_de_agua', 
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
            'geral_o' : round(geral_oferta, 3),
            'individual_d' : individual_demanda,
            'geral_d' : round(geral_demanda, 3),
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