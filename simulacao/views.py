from django.shortcuts import render, redirect, reverse, HttpResponse
from django.views.generic import TemplateView
from django.forms import inlineformset_factory, formset_factory


from .forms import EdificacaoForm, DemandasForm, DemandaSimulacaoAAPForm, SimulacaoAAPForm
from .models import DemandasDeAgua, Simulacao
from .base_de_dados.models import IndicePluviometrico, CaixaDAgua
from .utils import get_dollar

from .controllers.dimensionamentoController import DimensionamentoController
from .controllers.demandaController import DemandaController
from .controllers.ofertaController import OfertaController
from .controllers.economiaDeAguaController import EconomiaDeAguaController
from .controllers.beneficioController import BeneficioController

# Create your views here.


def initial_values():
    return [
        {
            'nome': 'Irrigação de jardins',
            'frequencia': 1,
            'indicador': 1
        },
        {
            'nome': 'Lavagem de pisos',
            'frequencia': 1,
            'indicador': 1
        },
        {
            'nome': 'Descarga sanitária',
            'frequencia': 30,
            'indicador': 32
        },
        {
            'nome': 'Lavagem de roupas',
            'frequencia': 1,
            'indicador': 31
        },
        {
            'nome': 'Tanque',
            'frequencia': 1,
            'indicador': 19
        },

    ]


def fill_novos_consumos(novos_consumos, initial_values):
    for subform, data in zip(novos_consumos.forms, initial_values()):
        subform.initial = data


def edificacao(request):
    context = {}
    consumo_factory = inlineformset_factory(Simulacao,
                                            DemandasDeAgua,
                                            form=DemandasForm,
                                            can_delete=True,
                                            extra=len(initial_values())
                                            )
    novos_consumos = consumo_factory
    nova_edificacao = EdificacaoForm
    if request.method == "GET":
        nova_edificacao = nova_edificacao()
        novos_consumos = novos_consumos()
        fill_novos_consumos(novos_consumos, initial_values)
        context['nova_edificacao'] = nova_edificacao
        context['novos_consumos'] = novos_consumos

        return render(request, 'edificacao.html', context)

    elif request.method == 'POST':
        nova_edificacao = nova_edificacao(request.POST)
        novos_consumos = novos_consumos(request.POST)
        if nova_edificacao.is_valid() and novos_consumos.is_valid():
            uma_edificacao = nova_edificacao.save()
            novos_consumos.instance = uma_edificacao
            novos_consumos.save()

            context['nova_edificacao'] = nova_edificacao
            context['novos_consumos'] = novos_consumos
            return redirect('simulacao:seleciona_simulacao', pk=uma_edificacao.pk)
        else:
            context['nova_edificacao'] = nova_edificacao
            context['novos_consumos'] = novos_consumos

            return render(request, 'edificacao.html', context)


def seleciona_simulacao(request, pk):
    return render(request, 'seleciona_simulacao.html', {'pk': pk})


def RACform(request, pk):
    if request.method == "GET":
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

