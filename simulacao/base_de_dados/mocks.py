from .models import (Cidade,
                     IndicePluviometrico,
                     AreaDeColeta,
                     Equipamentos,
                     BombaDeAgua
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
        'freio_dagua': 100
    },
    '200': {
            'filtro_dagua': 200,
            'sifao_ladrao': 100,
            'freio_dagua': 100
        },
    '500': {
            'filtro_dagua': 500,
            'sifao_ladrao': 100,
            'freio_dagua': 100
        },
    '700': {
            'filtro_dagua': 700,
            'sifao_ladrao': 150,
            'freio_dagua': 150
        },
    '1000': {
            'filtro_dagua': 1000,
            'sifao_ladrao': 150,
            'freio_dagua': 150
        },
    '1500': {
            'filtro_dagua': 1500,
            'sifao_ladrao': 200,
            'freio_dagua': 200
        },
    '2000': {
            'filtro_dagua': 2000,
            'sifao_ladrao': 200,
            'freio_dagua': 200
        },
    '3000': {
            'filtro_dagua': 3000,
            'sifao_ladrao': 200,
            'freio_dagua': 200
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
