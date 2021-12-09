from simulacao.controllers.dimensionamentoController import DimensionamentoController
from simulacao.models import Simulacao, DemandasDeAgua, OfertasDeAgua
from simulacao.base_de_dados.models import CaixaDAgua


def get_bomba_e_co(n_pavimentos):
    # Area de coleta faz-se desprezivel para o RAC
    Dimensionamento = DimensionamentoController(area_coleta=0, pavimentos=n_pavimentos)
    bomba = Dimensionamento.get_bomba_dagua()
    co = Dimensionamento.get_custo_operacional()
    return bomba, co


def get_simulacao(pk):
    # Filtrar uma oferta inexistente nao retorna erro, apenas um queryset vazio
    return {
        'simulacao': Simulacao.objects.get(pk=pk),
        'demandas_de_agua': DemandasDeAgua.objects.filter(simulacao=pk),
        'ofertas_de_agua': OfertasDeAgua.objects.filter(simulacao=pk)
    }


def calc_oferta_demanda(pk, interesse, **kwargs):
    ofertas = get_simulacao(pk)[interesse]

    individual = {}
    geral = 0
    irrigacao = 0

    for oferta in ofertas:
        agua = (oferta.indicador * oferta.frequencia_mensal)/1000
        if oferta.nome == "Irrigação de jardins":
            agua = agua / 12 * 5 * kwargs['area_irrigacao']
            irrigacao = agua * 12 / 5
        elif oferta.nome == "Lavagem de pisos":
            agua = agua * kwargs['area_pisos'] 
        else:
            agua = agua * kwargs['residentes']
        agua = round(agua, 2)
        geral += agua 
        individual[oferta.nome] = agua

    if "Irrigação de jardins" in individual:
        individual["Irrigação de jardins"] = irrigacao
    geral = geral*12 # m³/ano
    # individual em m³/mes
    return individual, geral, irrigacao


def get_caixa_dagua(demanda_diaria, dolar):
        todas = CaixaDAgua.objects.all()
        possiveis = list(todas.filter(volume__lt=demanda_diaria))
        
        if len(possiveis) < len(todas):
            possiveis.append(todas[len(possiveis)])
        
        caixas_dict = {caixa.volume: caixa.valor * dolar for caixa in possiveis}
        return list(caixas_dict.keys()), caixas_dict