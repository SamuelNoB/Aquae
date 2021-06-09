from ..base_de_dados.models import AreaDeColeta
from django.db.models import Sum


class AreaController:
    def __init__(self, area_cobertura, demanda_anual, indices_pluviometricos, **kwargs):
        self.area_cobertura = area_cobertura
        self.demanda_anual = demanda_anual
        self.indices_pluviometricos = indices_pluviometricos
        try:
            self.coeficiente_escoamento = kwargs['coeficiente_escoamento']
            self.coeficiente_filtragem = kwargs['coeficiente_filtragem']
        except KeyError:
            self.coeficiente_escoamento = 0.9
            self.coeficiente_filtragem = 0.9

    def get_soma_indices_pluviometricos(self):
        result = self.indices_pluviometricos.aggregate(Sum('media_pluviometrica'))
        return result['media_pluviometrica__sum']

    def get_area_ideal(self) -> int:
        total_mm_chuva = self.get_soma_indices_pluviometricos()
        dividendo = total_mm_chuva * self.coeficiente_escoamento * self.coeficiente_filtragem
        area_ideal = (self.demanda_anual / dividendo) * 1000

        if area_ideal > self.area_cobertura*2:
            area_ideal = -1

        return round(area_ideal)

    def get_area_de_coleta(self, area_ideal) -> int:
        areas_coleta = AreaDeColeta.objects.all()
        for area_coleta in areas_coleta:
            if area_coleta.area_min <= area_ideal <= area_coleta.area_max:
                return area_coleta.area_max

        return -1

