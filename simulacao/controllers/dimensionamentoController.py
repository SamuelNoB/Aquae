from ..base_de_dados.models import Equipamentos, BombaDeAgua

class DimensionamentoController:
    def __init__(self, area_coleta, pavimentos):
        self.area_coleta = area_coleta
        self.pavimentos = pavimentos

    def get_dimensionamentos(self):
        return Equipamentos.objects.get(area_de_coleta__area_max__gte=self.area_coleta,
                                        area_de_coleta__area_min__lte=self.area_coleta)

    def get_bomba_dagua(self):
        """
        Obtem uma bomba d'agua com base no numero de pavimentos
        :return: BombaDeAgua
        """
        return BombaDeAgua.objects\
            .get(pavimentos_min__lte=self.pavimentos, pavimentos_max__gte=self.pavimentos)

    def get_custo_operacional(self):
        """
        calcula o custo operacional anual
        :return: float
        """
        bomba_dagua = self.get_bomba_dagua()
        result = bomba_dagua.consumo * bomba_dagua.tarifa * bomba_dagua.horas_uso
        return round(result, 2)
