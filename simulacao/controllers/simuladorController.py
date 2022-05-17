from simulacao.controllers.dimensionamentoController import DimensionamentoController
from simulacao.models import Simulacao, DemandasDeAgua, OfertasDeAgua
from simulacao.base_de_dados.models import CaixaDAgua, TarifaDeAgua
from math import ceil


def get_bomba_e_co(n_pavimentos):
    # Area de coleta faz-se desprezivel para o RAC
    Dimensionamento = DimensionamentoController(area_coleta=0, pavimentos=n_pavimentos)
    bomba = Dimensionamento.get_bomba_dagua()
    co = Dimensionamento.get_custo_operacional()
    return bomba, co


def get_simulacao(pk):
    # Filtrar uma oferta inexistente nao retorna erro, apenas um queryset vazio
    return {
        "simulacao": Simulacao.objects.get(pk=pk),
        "demandas_de_agua": DemandasDeAgua.objects.filter(simulacao=pk),
        "ofertas_de_agua": OfertasDeAgua.objects.filter(simulacao=pk),
    }


def calc_oferta_demanda(pk, interesse, **kwargs):
    """
    Calcula a oferta ou demanda de água convertendo para Litros/dia
    """
    # "ofertas" no caso do RAC
    # Analogamente, seria "demandas" no caso do AAP
    ofertas = get_simulacao(pk)[interesse]
    if not kwargs["apts"]:
        apts = 1
    else:
        apts = kwargs["apts"]

    residentes = kwargs["residentes"] * apts

    individual = {}

    for oferta in ofertas:
        agua = (oferta.indicador * oferta.frequencia_mensal) / 1000
        if oferta.unidade == DemandasDeAgua.PESSOA:
            agua = agua * residentes
        elif oferta.nome == "Irrigação de jardins":
            agua = agua * kwargs["area_irrigacao"]
        elif oferta.unidade == DemandasDeAgua.METROS_QUADRADOS:
            # DemandasDeAgua.METROS_QUADRADOS é apenas uma string para comparar a unidade de medida
            # Pode ser usada sem perda de generalidade pelo RAC
            agua = agua * kwargs["area_pisos"]

        agua = round(agua, 2)
        individual[oferta.nome] = agua

    # individual em m³/mes
    return individual


def soma_dem(demandas_dict, n_est):
    total = 0
    for nome, indicador in demandas_dict.items():
        if nome == "Irrigação de jardins":
            total += indicador / 12 * n_est
        else:
            total += indicador

    return total * 12


def get_caixa_dagua(demanda_diaria):
    todas = CaixaDAgua.objects.all()
    possiveis = list(todas.filter(volume__lt=demanda_diaria))

    if len(possiveis) < len(todas):
        possiveis.append(todas[len(possiveis)])

    caixas_dict = {caixa.volume: caixa.valor for caixa in possiveis}
    return list(caixas_dict.keys()), caixas_dict


def get_tarifa(consumo):
    """
    Arredonda o consumo para o teto e calcula a tarifa utilizando esse teto
    Acontece que as faixas de consumo não descrevem o consumo entre uma faixa e outra
    """
    consumo = ceil(consumo)
    tarifa = TarifaDeAgua.objects.filter(min__lte=consumo, max__gte=consumo)
    return list(tarifa)[0].tarifa
