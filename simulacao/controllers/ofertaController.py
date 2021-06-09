from functools import reduce

from .areaController import AreaController


class OfertaController(AreaController):
    def get_oferta_mensal(self, media_pluviometrica) ->float:
        media_x_area = media_pluviometrica * self.area_cobertura
        result = (media_x_area * self.coeficiente_filtragem * self.coeficiente_escoamento) / 1000
        return result

    def generate_ofertas_mensais(self) -> list:
        ofertas_mensais = []
        for indice_pluviometrico in self.indices_pluviometricos:
            ofertas_mensais.append(self.get_oferta_mensal(indice_pluviometrico.media_pluviometrica))

        return ofertas_mensais

    def get_oferta_anual(self) -> int:
        ofertas_mensais = self.generate_ofertas_mensais()
        result = reduce(lambda ofertax, ofertay: ofertax + ofertay, ofertas_mensais)

        return round(result)

