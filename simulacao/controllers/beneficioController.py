from ..base_de_dados.models import TarifaDeAgua

class BeneficioController:
    def __init__(self, economias: list, tarifa_esgoto=100.0):
        self.economias = economias
        self.tarifa_esgoto = tarifa_esgoto/100

    def get_tarifas_cidade(self, cidade='Brasília'):
        return TarifaDeAgua.objects.filter(cidade__nome=cidade)

    def calcula_tarifa_agua(self, economia, faixas_de_consumo):
        total = 8

        for i in range(1,economia+1):
            for faixa_de_consumo in faixas_de_consumo:
                if faixa_de_consumo.min <= i <= faixa_de_consumo.max:
                    total += faixa_de_consumo.tarifa
                    break
        return round(total+(total*self.tarifa_esgoto), 2)

    def itera_economias(self):
        beneficios = []
        faixas_de_consumo = self.get_tarifas_cidade()
        for economia in self.economias[1:]:
            beneficios.append(self.calcula_tarifa_agua(economia, faixas_de_consumo))
        return beneficios



