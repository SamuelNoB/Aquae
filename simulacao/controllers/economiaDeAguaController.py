class EconomiaDeAguaController:
    def __init__(self, ofertas_mensais: [], demandas_mensais: (), intervalo_volume: int, demanda_anual):
        self.ofertas_mensais = ofertas_mensais
        self.demandas_mensais = demandas_mensais    # [0] demanda_seca [1] demanda_chuva
        self.demanda_anual = demanda_anual
        self.intervalo_volume = intervalo_volume

    # Q-D
    def oferta_menos_demanda(self, mes: int):
        if self.ofertas_mensais[mes] < 7:
            return self.ofertas_mensais[mes] - self.demandas_mensais[0]
        return self.ofertas_mensais[mes] - self.demandas_mensais[1]

    def saldo_cisterna(self, mes, volume_cisterna, saldo_ultimo_mes):
        diferenca_do_mes = self.oferta_menos_demanda(mes)
        if diferenca_do_mes >= volume_cisterna:
            return volume_cisterna
        if saldo_ultimo_mes <= 0:
            return diferenca_do_mes
        if saldo_ultimo_mes + diferenca_do_mes > volume_cisterna:
            return volume_cisterna

        return saldo_ultimo_mes + diferenca_do_mes

    def economia_de_agua(self, volume_cisterna):
        saldo_utlimo_mes = 0
        debito_agua = 0
        for mes in range(0,12):
            saldo_cisterna = self.saldo_cisterna(mes, volume_cisterna, saldo_utlimo_mes)
            saldo_utlimo_mes = saldo_cisterna
            if saldo_cisterna < 0:
                debito_agua += saldo_cisterna

        return self.demanda_anual + debito_agua

    def gera_grafico_data(self):
        result = {
            'volumes': [0],
            'economias': [0]
        }
        intervalo = self.intervalo_volume
        ultima_economia = 0
        economia = 1

        while economia != ultima_economia:
            ultima_economia = economia
            economia = self.economia_de_agua(intervalo)
            result['volumes'].append(intervalo)
            result['economias'].append(round(economia))
            intervalo += self.intervalo_volume

        return result


if __name__ == '__main__':
    ofertas_mensais = [81.5751,
                      64.35369000000001,
                      63.447300000000006,
                      36.55773000000001,
                      10.87668,
                      3.0213,
                      1.81278,
                      3.9276900000000006,
                      14.50224,
                      51.66423,
                      66.46860000000001,
                      78.25167]
    economia_de_agua = EconomiaDeAguaController(
        ofertas_mensais,
        (18.40992, 11.329920000000001),
        10,
        24.48,
    )
    economia_de_agua.economia_de_agua(10)