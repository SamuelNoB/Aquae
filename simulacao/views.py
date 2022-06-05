from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.views.generic import TemplateView, View
from django.http import JsonResponse
from django.forms import inlineformset_factory, formset_factory
from numpy.lib.function_base import diff
from requests.api import get


from .forms import (
    EdificacaoForm,
    UsosForm,
    DemandaSimulacaoAAPForm,
    SimulacaoAAPForm,
)
from .models import UsosDeAgua, Simulacao
from .base_de_dados.models import (
    Equipamentos,
    IndicePluviometrico,
    CaixaDAgua,
    CapacidadeDeTratamento,
    TarifaDeAgua,
    Cidade,
)
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


def usos_update(pk, escolhas, categoria):
    """
    Recebe a chave primária, o fomrulário que o usuário preencheu
    e a categoria para a qual preencheu e por fim atualiza essas
    escolhas na base de dados
    """
    usos = UsosDeAgua.objects.filter(simulacao=pk)
    for uso in usos:
        presenca = uso.nome in escolhas
        setattr(uso, categoria, presenca)
        uso.save()


# Create your views here.


def edificacao(request):
    context = {}
    consumo_factory = inlineformset_factory(
        Simulacao,
        UsosDeAgua,
        form=UsosForm,
        can_delete=True,
    )
    novos_consumos = consumo_factory
    nova_edificacao = EdificacaoForm
    context["nova_edificacao"] = nova_edificacao

    if request.is_ajax():
        uf = request.GET.get("uf")
        nomes = list(map(lambda cidade: cidade.nome, Cidade.objects.filter(uf=uf)))
        return JsonResponse({"cidades": nomes}, status=200)

    if request.method == "POST":
        nova_edificacao = nova_edificacao(request.POST)
        novos_consumos = novos_consumos(request.POST)
        if nova_edificacao.is_valid() and novos_consumos.is_valid():
            uma_edificacao = nova_edificacao.save()
            novos_consumos.instance = uma_edificacao
            novos_consumos.save()
            return redirect("simulacao:seleciona_demanda", pk=uma_edificacao.pk)
        else:
            context["nova_edificacao"] = nova_edificacao
            return render(request, "edificacao.html", context)

    return render(request, "edificacao.html", context)


def seleciona_demanda(request, pk):
    context = {"pk": pk}
    usos = UsosDeAgua.objects.filter(simulacao=pk)
    usos = [uso.nome for uso in usos]
    context["usos"] = usos
    if request.method == "POST":
        if len(request.POST) == 1 or len(request.POST) - 1 > len(usos):
            return render(request, "AAP-form.html", context)
        else:
            usos_update(pk=pk, escolhas=request.POST, categoria="demanda")
            return redirect("simulacao:seleciona_simulacao", pk=pk)
    return render(request, "AAP-form.html", context)


def seleciona_simulacao(request, pk):
    return render(request, "seleciona_simulacao.html", {"pk": pk})


def RACform(request, pk):
    oferta_factory = inlineformset_factory(Simulacao, OfertasDeAgua, fields="__all__")
    try:
        simul_id = Simulacao.objects.get(id=pk)
    except simulacao.models.Simulacao.DoesNotExist:
        return redirect("simulacao:edificacao")

    ofertas_avancado = OfertasDeAgua.objects.filter(simulacao=pk)
    if ofertas_avancado:
        return redirect("simulacao:simulacao-rac", pk=pk)

    oferta_factory(instance=simul_id)
    if request.method == "POST":
        novas_ofertas = oferta_factory(request.POST, instance=simul_id)
        if novas_ofertas.is_valid():
            novas_ofertas.save()
            return redirect("simulacao:simulacao-rac", pk=pk)

    return render(request, "RAC-form.html", {"pk": pk})


class SimulacaoAAP(TemplateView):
    template_name = "simuladorAAP.html"

    def get_pluviometria(self, cidade="BRASILIA"):
        local = Cidade.objects.get(nome=cidade)
        pluviometria = IndicePluviometrico.objects.filter(ano=2019, cidade=local)
        pluviometria = pluviometria.values_list("media_pluviometrica")
        pluviometria = list(map(lambda x: x[0], pluviometria))
        return pluviometria

    def get_equips(self, area_coleta):
        todas = Equipamentos.objects.all()

        possiveis = list(todas.filter(area_de_coleta__lt=area_coleta))
        if len(possiveis) < len(todas):
            possiveis.append(todas[len(possiveis)])

        equips_dict = {
            equip.area_de_coleta.area_max: {
                "filtro": equip.filtro_dagua,
                "freio": equip.freio_dagua,
                "sifao": equip.sifao_ladrao,
                "custo": equip.custo_implementacao,
            }
            for equip in possiveis
        }

        return equips_dict

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")

        try:
            simul = simuladorController.get_simulacao(pk=pk)["simulacao"]
        except simulacao.models.Simulacao.DoesNotExist:
            return redirect("simulacao:edificacao")

        area_i = simul.area_irrigacao
        area_p = simul.area_pisos
        area_c = simul.area_cobertura
        consumo = simul.consumo_mensal
        esgoto = simul.tarifa_esgoto / 100
        pessoas = simul.n_pessoas
        n_apts = simul.n_apts
        n_pavimentos = simul.n_pavimentos
        coeficiente_esc = 0.9
        coeficiente_filt = 0.9

        individual_d = simuladorController.calc_oferta_demanda(
            pk,
            "demandas_de_agua",
            apts=n_apts,
            residentes=pessoas,
            area_irrigacao=area_i,
            area_pisos=area_p,
        )
        if "Irrigação de jardins" in individual_d:
            irrigacao = round(individual_d["Irrigação de jardins"], 2)
        else:
            irrigacao = 0

        # TODO Versoes futuras devem especificar cidade
        pluviometria = np.array(self.get_pluviometria())
        meses_est = np.where(pluviometria < 50)
        n_meses_est = len(meses_est[0])
        pluviometria_total = pluviometria.sum()
        geral_demanda = round(
            simuladorController.soma_dem(individual_d, n_meses_est), 2
        )
        area_ideal = ceil(
            geral_demanda
            / (pluviometria_total * coeficiente_esc * coeficiente_filt)
            * 1000
        )
        area_coleta = min(area_ideal, area_c)

        oferta_mensal = (
            pluviometria * area_coleta * coeficiente_esc * coeficiente_filt / 1000
        )
        oferta_mensal = np.around(oferta_mensal, decimals=2)
        oferta_total = round(oferta_mensal.sum(), 2)

        demanda_sest = round(
            (geral_demanda - irrigacao * n_meses_est) / 12, 2
        )  # periodo sem estiagem
        demanda_est = demanda_sest + irrigacao  # periodo de estiagem
        demanda_mensal = np.array([demanda_sest for i in range(12)])
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
        volumes_caixa, financeiro_caixa = simuladorController.get_caixa_dagua(
            demanda_g_ld
        )

        tarifa = simuladorController.get_tarifa(consumo) * (1 + esgoto)

        context = {
            "pk": pk,
            "individual_d": individual_d,
            "geral_demanda": geral_demanda,
            "oferta_total": oferta_total,
            "demanda_mensal": demanda_mensal,
            "oferta_mensal": oferta_mensal,
            "meses_estiagem": meses_est,
            "area_disponivel": area_c,
            "area_coleta": area_coleta,
            "pluviometria_mensal": pluviometria,
            "pluviometria_total": pluviometria_total,
            "equipamentos": json.dumps(equips),
            "bomba": {"dimensoes": bomba, "custo_op": co, "preco": bomba.preco / 3.77},
            "caixa": {"volumes": volumes_caixa, "financeiro": financeiro_caixa},
            "tarifa": tarifa,
            "dolar": dolar,
        }

        return render(request, self.template_name, context)


class SimulacaoRAC(TemplateView):
    template_name = "simuladorRAC.html"

    def get_capacidade(self, demanda):
        todas = CapacidadeDeTratamento.objects.all()

        # Capacidades suficientes para uma demanda menor que a especificada no formulario
        possiveis = list(todas.filter(volume__lt=demanda))

        if len(possiveis) < len(todas):
            # Capacidade suficiente para a demanda especificada no formulario
            possiveis.append(todas[len(possiveis)])

        capacidade_dict = {
            capacidade.volume: [capacidade.valor, capacidade.custo_operacional]
            for capacidade in possiveis
        }

        return list(capacidade_dict.keys()), capacidade_dict

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")

        try:
            simul = simuladorController.get_simulacao(pk=pk)["simulacao"]
        except simulacao.models.Simulacao.DoesNotExist:
            return redirect("simulacao:edificacao")
        area_i = simul.area_irrigacao
        area_p = simul.area_pisos
        consumo = simul.consumo_mensal
        esgoto = simul.tarifa_esgoto / 100
        pessoas = simul.n_pessoas
        n_apts = simul.n_apts

        # Se a simulacao foi encontrada, entao o form da demanda foi preenchido
        individual_demanda = simuladorController.calc_oferta_demanda(
            pk,
            "demandas_de_agua",
            apts=n_apts,
            area_irrigacao=area_i,
            area_pisos=area_p,
            residentes=pessoas,
        )

        # Buscar uma oferta em uma simulacao existente nao retorna erro
        individual_oferta = simuladorController.calc_oferta_demanda(
            pk,
            "ofertas_de_agua",
            apts=n_apts,
            area_irrigacao=area_i,
            area_pisos=area_p,
            residentes=pessoas,
        )
        if not individual_oferta:
            return redirect("simulacao:formulario-rac", pk=pk)

        n_pavimentos = simul.n_pavimentos
        bomba, custo_op = simuladorController.get_bomba_e_co(n_pavimentos)

        # m³ para litros / dia
        # demanda no mes de estiagem
        demanda_g_ld = sum(list(individual_demanda.values())) * 1000 / 30
        volumes_cap, financeiro_cap = self.get_capacidade(demanda_g_ld)
        volumes_caixa, financeiro_caixa = simuladorController.get_caixa_dagua(
            demanda_g_ld
        )

        tarifa = simuladorController.get_tarifa(consumo) * (1 + esgoto)

        context = {
            "pk": pk,
            "individual_o": individual_oferta,
            "individual_d": individual_demanda,
            "tratamento": {"Volumes": volumes_cap, "Financeiro": financeiro_cap},
            "bomba": {"Dimensoes": bomba, "Custo_op": custo_op, "Custo": bomba.preco},
            "caixa": {"Volumes": volumes_caixa, "Financeiro": financeiro_caixa},
            "tarifa": tarifa,
        }

        return render(request, self.template_name, context)
