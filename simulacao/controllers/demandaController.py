from ..models import Simulacao


class DemandaController:
    def __init__(self, demandas: list, simulacao: Simulacao):
        self.demandas = demandas
        self.simulacao = simulacao
        self.meses = 12

    @staticmethod
    def return_default_demandas():
        return [
            'Irrigação de jardins',
            'Lavagem de pisos',
            'Lavagem de roupas',
            'Descarga sanitária',
            'Torneira de cozinha',
            'Torneira de banheiro',
            'Máquina lava louça',
            'Tanque',
        ]

    def calcula_demanda_diaria(self, indic_equival:tuple):
        result = indic_equival[0] * indic_equival[1]
        return result

    def calcula_demanda_mensal(self, indic_equival:tuple, frequencia):
        return self.calcula_demanda_diaria(indic_equival) * frequencia / 1000

    @staticmethod
    def calcula_demanda_anual(demanda_mensal, meses):
        return demanda_mensal * meses

    def get_indicador_equivalente(self, demanda):
        if demanda.nome == self.return_default_demandas()[0]:
            indicador_equivalente = (demanda.indicador, self.simulacao.area_irrigacao)
            self.meses = 5
        elif demanda.nome == self.return_default_demandas()[1]:
            indicador_equivalente = (demanda.indicador, self.simulacao.area_pisos)
        elif demanda.nome not in self.return_default_demandas():
            indicador_equivalente = (demanda.indicador, 1)
        else:
            indicador_equivalente = (demanda.indicador, self.simulacao.n_pessoas)
        return indicador_equivalente

    def mock_demandas_mensais(self):
        demanda_seca = 0
        demanda_chuva = 0
        for demanda in self.demandas:
            indicador_equivalente = self.get_indicador_equivalente(demanda)
            demanda_mensal = self.calcula_demanda_mensal(indicador_equivalente, demanda.frequencia_mensal)
            demanda_seca += demanda_mensal
            if demanda.nome != self.return_default_demandas()[0]:
                demanda_chuva += demanda_mensal

        return tuple([demanda_seca, demanda_chuva])

    def sum_demandas_anuais(self):

        result = 0
        for demanda in self.demandas:
            self.meses = 12
            indicador_equivalente = self.get_indicador_equivalente(demanda)

            demanda_mensal = self.calcula_demanda_mensal(indicador_equivalente, demanda.frequencia_mensal)
            demanda_anual = self.calcula_demanda_anual(demanda_mensal, self.meses)
            result += demanda_anual

        return round(result, 2)
