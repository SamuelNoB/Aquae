from .models import (Cidade,
                     IndicePluviometrico,
                     AreaDeColeta,
                     Equipamentos,
                     BombaDeAgua,
                     CaixaDAgua,
                     TarifaDeAgua,
                     CapacidadeDeTratamento
                     )

indice_pluviometrico_mock = {
    'Brasília': {
        '2019': [270, 213, 210, 121, 36, 10, 6, 13, 48, 171, 220, 259],
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
    (2001, 3000)
]

equipamentos = {

    '150': {
        'filtro_dagua': 150,
        'sifao_ladrao': 100,
        'freio_dagua': 100,
        'custo_implementacao': 410.34
    },
    '200': {
            'filtro_dagua': 200,
            'sifao_ladrao': 100,
            'freio_dagua': 100,
            'custo_implementacao': 638.73
        },
    '500': {
            'filtro_dagua': 500,
            'sifao_ladrao': 100,
            'freio_dagua': 100,
            'custo_implementacao': 1006.90
        },
    '700': {
            'filtro_dagua': 700,
            'sifao_ladrao': 150,
            'freio_dagua': 150,
            'custo_implementacao': 1558.36
        },
    '1000': {
            'filtro_dagua': 1000,
            'sifao_ladrao': 150,
            'freio_dagua': 150,
            'custo_implementacao': 1759.95
        },
    '1500': {
            'filtro_dagua': 1500,
            'sifao_ladrao': 200,
            'freio_dagua': 200,
            'custo_implementacao': 3083.13
        },
    '2000': {
            'filtro_dagua': 2000,
            'sifao_ladrao': 200,
            'freio_dagua': 200,
            'custo_implementacao': 3739.10
        },
    '3000': {
            'filtro_dagua': 3000,
            'sifao_ladrao': 200,
            'freio_dagua': 200,
            'custo_implementacao': 6654.54
        },
}

bombas_dagua = [
    {
        "pavimentos_min": 0,
        "pavimentos_max": 3,
        "potencia": 1/4,
        "consumo": 0.26,
        "tarifa": 0.7,
        "succao": 32,
        "recalque": 25,
        "preco": 500,
        "horas_uso": 62,
    },
    {
        "pavimentos_min":4,
        "pavimentos_max":7,
        "potencia":1/2,
        "consumo":0.99,
        "tarifa":0.7,
        "succao":32,
        "recalque":25,
        "preco":600,
        "horas_uso":182,
    },
    {
        "pavimentos_min":8,
        "pavimentos_max":10,
        "potencia":1,
        "consumo":1.38,
        "tarifa":0.7,
        "succao":40,
        "recalque":32,
        "preco":750,
        "horas_uso":182,
    },
    {
        "pavimentos_min":11,
        "pavimentos_max":17,
        "potencia":2,
        "consumo":2.76,
        "tarifa":0.7,
        "succao":40,
        "recalque":32,
        "preco":1130,
        "horas_uso":182,
    }
]

caixas_dagua = [
    {
        "min": 0,
        "max": 500,
        "volume": 500,
        "valor": 53.05
    },
    {
        "min": 501,
        "max": 1000,
        "volume": 1000,
        "valor": 79.58
    },
    {
        "min": 1001,
        "max": 1500,
        "volume": 1500,
        "valor": 145.89
    },
    {
        "min": 1501,
        "max": 2000,
        "volume": 2000,
        "valor": 204.24
    },
    {
        "min": 2001,
        "max": 3000,
        "volume": 3000,
        "valor": 344.83
    },
    {
        "min": 3001,
        "max": 5000,
        "volume": 5000,
        "valor": 464.19
    },
    {
        "min": 5001,
        "max": 10000,
        "volume": 10000,
        "valor": 1100.8
    },
    {
        "min": 10001,
        "max": 15000,
        "volume": 15000,
        "valor": 1789.41
    },
]

tarifas_mock = {
    "Brasília":
        [
            {'min': 0,
             'max': 7,
             'tarifa': 2.99
             },
            {'min': 8,
             'max': 13,
             'tarifa': 3.59
             },
            {'min': 14,
             'max': 20,
             'tarifa': 7.1
             },
            {'min': 21,
             'max': 30,
             'tarifa': 10.66
             },
            {'min': 31,
             'max': 45,
             'tarifa': 17.05
             },
            {'min': 46,
             'max': 99999999,
             'tarifa': 23.87
             },
        ]
}

# RAC
capacidades_de_tratamento = [
    {
        "min": 0,
        "max": 3000,
        "volume": 3000,
        "valor": 6631,
        "custo_o": 0.4
    },
    {
        "min": 3001,
        "max": 6000,
        "volume": 6000,
        "valor": 8090,
        "custo_o": 0.8
    },
    {
        "min": 6001,
        "max": 10000,
        "volume": 10000,
        "valor": 11008,
        "custo_o": 1.33
    },
    {
        "min": 10001,
        "max": 15000,
        "volume": 15000,
        "valor": 13342,
        "custo_o": 1.99
    },
    {
        "min": 15001,
        "max": 20000,
        "volume": 20000,
        "valor": 13926,
        "custo_o": 2.65
    },
    {
        "min": 20001,
        "max": 30000,
        "volume": 30000,
        "valor": 17242,
        "custo_o": 3.98
    },
    {
        "min": 30001,
        "max": 50000,
        "volume": 50000,
        "valor": 23077,
        "custo_o": 6.63
    },
    {
        "min": 50001,
        "max": 80000,
        "volume": 80000,
        "valor": 26764,
        "custo_o": 10.61
    }
]

def create_indices_pluviometricos():
    for cidade, anos in indice_pluviometrico_mock.items():
        nova_cidade = Cidade.objects.create(nome=cidade)
        for ano, valores in anos.items():
            indices = map(lambda valor: IndicePluviometrico.objects.create(
                cidade=nova_cidade,
                ano=int(ano),
                mes=valores.index(valor),
                media_pluviometrica=valor
                ),
                valores
                )
        nova_cidade.save()
        for indice in indices:
            indice.save()


def create_areas_coleta():
    for area_coleta in areas_de_coleta:
        novo_objeto = AreaDeColeta.objects.create(area_min=area_coleta[0], area_max=area_coleta[1])
        novo_objeto.save()


def create_equipamentos():
    for area_de_coleta, equipamento in equipamentos.items():
        uma_area = AreaDeColeta.objects.get(area_max=int(area_de_coleta))
        novo_equipamento = Equipamentos.objects.create(
            filtro_dagua=equipamento['filtro_dagua'],
            sifao_ladrao=equipamento['sifao_ladrao'],
            freio_dagua=equipamento['freio_dagua'],
            custo_implementacao=equipamento['custo_implementacao'],
            area_de_coleta=uma_area
        )
        novo_equipamento.save()


def create_bombas_dagua():
    for bomba in bombas_dagua:
        nova_bomba = BombaDeAgua\
            .objects.create(pavimentos_min=bomba['pavimentos_min'],
                            pavimentos_max=bomba['pavimentos_max'],
                            potencia=bomba['potencia'],
                            consumo=bomba['consumo'],
                            tarifa=bomba['tarifa'],
                            succao=bomba['succao'],
                            recalque=bomba['recalque'],
                            preco=bomba['preco'],
                            horas_uso=bomba['horas_uso'],
                            )
        nova_bomba.save()


def create_caixas_dagua():
    for caixa in caixas_dagua:
        nova_caixa = CaixaDAgua\
            .objects.create(min=caixa['min'],
                            max=caixa['max'],
                            volume=caixa['volume'],
                            valor=caixa['valor']
                            )
        nova_caixa.save()


def create_tarifas():
    for cidade_tarifa in tarifas_mock.items():
        cidade = Cidade.objects.get(nome=cidade_tarifa[0])
        for tarifas in cidade_tarifa[1]:
            nova_tarifa = TarifaDeAgua \
                .objects.create(cidade=cidade,
                                min=tarifas['min'],
                                max=tarifas['max'],
                                tarifa=tarifas['tarifa']
                                )
            nova_tarifa.save()


def create_capacidades_de_tratamento():
    for capacidade in capacidades_de_tratamento:
        nova_capacidade = CapacidadeDeTratamento\
            .objects.create(min=capacidade['min'],
                            max=capacidade['max'],
                            volume=capacidade['volume'],
                            valor=capacidade['valor'],
                            custo_operacional=capacidade['custo_o']
                            )
        nova_capacidade.save()