from django.test import TestCase

from .models import Simulacao, DemandasDeAgua
from .base_de_dados.mocks import AreaDeColeta, IndicePluviometrico, Cidade
from .base_de_dados.mocks import create_indices_pluviometricos, create_areas_coleta
from .controllers.demandaController import DemandaController
from .controllers.areaController import AreaController


def create_base_de_dados():
    create_indices_pluviometricos()


def create_simulacao_object():
    simu_1 = Simulacao.objects.create(
        tipo_residencia=0,
        n_pessoas=5,
        tarifa_esgoto=1.0,
        consumo_mensal=20,
        area_cobertura=373,
        area_pisos=86,
        area_irrigacao=118
    )
    return simu_1


def create_demandas():
    demandas = [
        {
            'nome': 'Irrigação de jardins',
            'frequencia': 30,
            'indicador': 2
        },
        {
            'nome': 'Lavagem de pisos',
            'frequencia': 4,
            'indicador': 2
        },
        {
            'nome': 'Lavagem de roupas',
            'frequencia': 12,
            'indicador': 34.4386479591837
        },
        {
            'nome': 'Descarga sanitária',
            'frequencia': 30,
            'indicador': 42.1712281341108
        },
        {
            'nome': 'Tanque',
            'frequencia': 20,
            'indicador': 23.0970692245459
        }
    ]

    simulacao = create_simulacao_object()
    demandas_objects = []
    for demanda in demandas:
        uma_demanda = DemandasDeAgua.objects.create(
            simulacao=simulacao,
            nome=demanda['nome'],
            frequencia_mensal=demanda['frequencia'],
            indicador=demanda['indicador']
        )
        demandas_objects.append(uma_demanda)
    return demandas_objects, simulacao




# Create your tests here.
class DemandaTests(TestCase):
    """
    Testa se a demanda Anual funciona corretamente
    """
    def test_demanda_anual(self):
        demandas, simulacao = create_demandas()
        simulacao_demanda = DemandaController(demandas, simulacao)
        result = simulacao_demanda.sum_demandas_anuais()
        self.assertEqual(result, 172)


class AreaTests(TestCase):

    def test_area_ideal(self):
        self.demandas, self.simulacao = create_demandas()
        create_indices_pluviometricos()
        indices_pluviometricos = IndicePluviometrico.objects.filter(ano=2019)
        self.demandacontroller = DemandaController(demandas=self.demandas,
                                                   simulacao=self.simulacao)

        area_test = AreaController(self.simulacao.area_cobertura,
                                   self.demandacontroller.sum_demandas_anuais(),
                                   indices_pluviometricos=indices_pluviometricos).get_area_ideal()

        self.assertEqual(area_test, 135)

    def test_area_coleta(self):
        self.demandas, self.simulacao = create_demandas()
        create_indices_pluviometricos()
        create_areas_coleta()
        indices_pluviometricos = IndicePluviometrico.objects.filter(ano=2019)
        self.demandacontroller = DemandaController(demandas=self.demandas,
                                                   simulacao=self.simulacao)

        controller = AreaController(self.simulacao.area_cobertura,
                                   self.demandacontroller.sum_demandas_anuais(),
                                   indices_pluviometricos=indices_pluviometricos)

        area_ideal = controller.get_area_ideal()
        area_coleta = controller.get_area_de_coleta(area_ideal)
        self.assertEqual(area_coleta, 150)
