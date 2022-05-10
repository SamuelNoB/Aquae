from .models import (
    Cidade,
    IndicePluviometrico,
    AreaDeColeta,
    Equipamentos,
    BombaDeAgua,
    CaixaDAgua,
    TarifaDeAgua,
    CapacidadeDeTratamento,
)
import json
import django
from ..utils import get_tarifa_caesb, get_ni_ipca

indice_pluviometrico_mock = {
    "Brasília": {
        "2019": [270, 213, 210, 121, 36, 10, 6, 13, 48, 171, 220, 259],
    }
}

areas_de_coleta = [
    (0, 150),
    (151, 200),
    (201, 500),
    (501, 700),
    (701, 1000),
    (1001, 1500),
    (1501, 2000),
    (2001, 3000),
]

# TODO adicionar comentario com o ano de coleta dos custos
# Temporariamente utilizando 06/2019
IPCA_o = 5214.27
equipamentos = {
    "150": {
        "filtro_dagua": 150,
        "sifao_ladrao": 100,
        "freio_dagua": 100,
        "custo_implementacao": 1547.0,
    },
    "200": {
        "filtro_dagua": 200,
        "sifao_ladrao": 100,
        "freio_dagua": 100,
        "custo_implementacao": 2408.0,
    },
    "500": {
        "filtro_dagua": 500,
        "sifao_ladrao": 100,
        "freio_dagua": 100,
        "custo_implementacao": 3796.0,
    },
    "700": {
        "filtro_dagua": 700,
        "sifao_ladrao": 150,
        "freio_dagua": 150,
        "custo_implementacao": 5875.0,
    },
    "1000": {
        "filtro_dagua": 1000,
        "sifao_ladrao": 150,
        "freio_dagua": 150,
        "custo_implementacao": 6635.0,
    },
    "1500": {
        "filtro_dagua": 1500,
        "sifao_ladrao": 200,
        "freio_dagua": 200,
        "custo_implementacao": 11623.4,
    },
    "2000": {
        "filtro_dagua": 2000,
        "sifao_ladrao": 200,
        "freio_dagua": 200,
        "custo_implementacao": 14096.4,
    },
    "3000": {
        "filtro_dagua": 3000,
        "sifao_ladrao": 200,
        "freio_dagua": 200,
        "custo_implementacao": 25087.6,
    },
}

bombas_dagua = [
    {
        "pavimentos_min": 0,
        "pavimentos_max": 3,
        "potencia": 1 / 4,
        "consumo": 0.26,
        "tarifa": 0.7,
        "succao": 32,
        "recalque": 25,
        "preco": 500,
        "horas_uso": 62,
    },
    {
        "pavimentos_min": 4,
        "pavimentos_max": 7,
        "potencia": 1 / 2,
        "consumo": 0.99,
        "tarifa": 0.7,
        "succao": 32,
        "recalque": 25,
        "preco": 600,
        "horas_uso": 182,
    },
    {
        "pavimentos_min": 8,
        "pavimentos_max": 10,
        "potencia": 1,
        "consumo": 1.38,
        "tarifa": 0.7,
        "succao": 40,
        "recalque": 32,
        "preco": 750,
        "horas_uso": 182,
    },
    {
        "pavimentos_min": 11,
        "pavimentos_max": 17,
        "potencia": 2,
        "consumo": 2.76,
        "tarifa": 0.7,
        "succao": 40,
        "recalque": 32,
        "preco": 1130,
        "horas_uso": 182,
    },
]

caixas_dagua = [
    {"min": 0, "max": 500, "volume": 500, "valor": 200.0},
    {"min": 501, "max": 1000, "volume": 1000, "valor": 300.0},
    {"min": 1001, "max": 1500, "volume": 1500, "valor": 550.0},
    {"min": 1501, "max": 2000, "volume": 2000, "valor": 770.0},
    {"min": 2001, "max": 3000, "volume": 3000, "valor": 1300.0},
    {"min": 3001, "max": 5000, "volume": 5000, "valor": 1750.0},
    {"min": 5001, "max": 10000, "volume": 10000, "valor": 4150.0},
    {"min": 10001, "max": 15000, "volume": 15000, "valor": 6780.0},
]

# RAC
capacidades_de_tratamento = [
    {"min": 0, "max": 3000, "volume": 3000, "valor": 25000.0, "custo_o": 1.5},
    {"min": 3001, "max": 6000, "volume": 6000, "valor": 30500.0, "custo_o": 3.0},
    {"min": 6001, "max": 10000, "volume": 10000, "valor": 41500.0, "custo_o": 5.0},
    {"min": 10001, "max": 15000, "volume": 15000, "valor": 50300.0, "custo_o": 7.5},
    {"min": 15001, "max": 20000, "volume": 20000, "valor": 52500.0, "custo_o": 10.0},
    {"min": 20001, "max": 30000, "volume": 30000, "valor": 65000.0, "custo_o": 15.0},
    {"min": 30001, "max": 50000, "volume": 50000, "valor": 87000.0, "custo_o": 25.0},
    {"min": 50001, "max": 80000, "volume": 80000, "valor": 100900.0, "custo_o": 40.0},
]


def create_indices_pluviometricos():
    for cidade, anos in indice_pluviometrico_mock.items():
        # Se a cidade ja existir recria-se a mesma
        try:
            nova_cidade = Cidade.objects.create(nome=cidade)
        except django.db.utils.IntegrityError:
            nova_cidade = Cidade.objects.get(nome=cidade).delete()
            nova_cidade = Cidade.objects.create(nome=cidade)

        for ano, valores in anos.items():
            indices = map(
                lambda valor: IndicePluviometrico.objects.create(
                    cidade=nova_cidade,
                    ano=int(ano),
                    mes=valores.index(valor),
                    media_pluviometrica=valor,
                ),
                valores,
            )
        nova_cidade.save()
        for indice in indices:
            indice.save()


# TODO reorganizar funcoes semelhantes para evitar multiplos requests do IPCA
def create_tarifas():
    data = {"Brasília": get_tarifa_caesb()}
    with open("./simulacao/base_de_dados/tarifas.json", "w") as outfile:
        json.dump(data, outfile)
    for cidade, tarifas in data.items():
        cidade_obj = Cidade.objects.get(nome=cidade)

        for tarifa in tarifas:
            nova_tarifa = TarifaDeAgua.objects.create(
                cidade=cidade_obj,
                min=tarifa["min"],
                max=tarifa["max"],
                tarifa=tarifa["tarifa"],
            )
            nova_tarifa.save()


def create_areas_coleta():
    AreaDeColeta.objects.all().delete()
    for area_coleta in areas_de_coleta:
        novo_objeto = AreaDeColeta.objects.create(
            area_min=area_coleta[0], area_max=area_coleta[1]
        )
        novo_objeto.save()


def create_equipamentos():
    IPCA = get_ni_ipca() / IPCA_o
    Equipamentos.objects.all().delete()
    for area_de_coleta, equipamento in equipamentos.items():
        uma_area = AreaDeColeta.objects.get(area_max=int(area_de_coleta))
        novo_equipamento = Equipamentos.objects.create(
            filtro_dagua=equipamento["filtro_dagua"],
            sifao_ladrao=equipamento["sifao_ladrao"],
            freio_dagua=equipamento["freio_dagua"],
            custo_implementacao=equipamento["custo_implementacao"] * IPCA,
            area_de_coleta=uma_area,
        )
        novo_equipamento.save()


def create_bombas_dagua():
    BombaDeAgua.objects.all().delete()
    for bomba in bombas_dagua:
        nova_bomba = BombaDeAgua.objects.create(
            pavimentos_min=bomba["pavimentos_min"],
            pavimentos_max=bomba["pavimentos_max"],
            potencia=bomba["potencia"],
            consumo=bomba["consumo"],
            tarifa=bomba["tarifa"],
            succao=bomba["succao"],
            recalque=bomba["recalque"],
            preco=bomba["preco"],
            horas_uso=bomba["horas_uso"],
        )
        nova_bomba.save()


def create_caixas_dagua():
    IPCA = get_ni_ipca() / IPCA_o
    CaixaDAgua.objects.all().delete()
    for caixa in caixas_dagua:
        nova_caixa = CaixaDAgua.objects.create(
            min=caixa["min"],
            max=caixa["max"],
            volume=caixa["volume"],
            valor=caixa["valor"] * IPCA,
        )
        nova_caixa.save()


def create_capacidades_de_tratamento():
    IPCA = get_ni_ipca() / IPCA_o
    CapacidadeDeTratamento.objects.all().delete()
    for capacidade in capacidades_de_tratamento:
        nova_capacidade = CapacidadeDeTratamento.objects.create(
            min=capacidade["min"],
            max=capacidade["max"],
            volume=capacidade["volume"],
            valor=capacidade["valor"] * IPCA,
            custo_operacional=capacidade["custo_o"],
        )
        nova_capacidade.save()
