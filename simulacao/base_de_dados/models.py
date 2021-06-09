from django.db import models

# Create your models here.


class Cidade(models.Model):
    nome = models.CharField('Nome da cidade', max_length=100, unique=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Cidade'
        verbose_name_plural = 'Cidades'

class TarifaDeAgua(models.Model):
    min = models.IntegerField('Faixa de consumo mínima',default=0)
    max = models.IntegerField('Faixa de consumo máxima', null=True)
    tarifa = models.FloatField('tarifa', default=0)

    cidade = models.ForeignKey(Cidade,
                               on_delete=models.CASCADE,
                               verbose_name='Cidade pertencente',
                               related_name='tarifas'
                               )

    def __str__(self):
        return f'{self.cidade}: {self.min}\t{self.max}\tTarifa:{self.tarifa}'

    class Meta:
        verbose_name = 'Tarifa de água'
        verbose_name_plural = 'Tarifas de água'

class IndicePluviometrico(models.Model):
    MESES_CHOICES = (
        (0, 'Janeiro'),
        (1, 'Fevereiro'),
        (2, 'Março'),
        (3, 'Abril'),
        (4, 'Maio'),
        (5, 'Junho'),
        (6, 'Julho'),
        (7, 'Agosto'),
        (8, 'Setembro'),
        (9, 'Outubro'),
        (10, 'Novembro'),
        (11, 'Dezembro'),
    )

    ano = models.IntegerField('Ano')
    mes = models.IntegerField('Mês', choices=MESES_CHOICES)
    media_pluviometrica = models.IntegerField('Média pluviométrica em mm')

    cidade = models.ForeignKey(
        Cidade,
        on_delete=models.CASCADE,
        verbose_name='Cidade pertencente',
        related_name='indices'
    )

    def __str__(self):
        return f'{self.ano} {self.mes}'

    class Meta:
        verbose_name = 'Índice pluviométrico'
        verbose_name_plural = 'Índices pluviométricos'
        ordering = ['ano']
        constraints = [
            models.UniqueConstraint(fields=['cidade', 'mes', 'ano'], name='índice pluviométrico único')
        ]


class AreaDeColeta(models.Model):
    area_min = models.IntegerField(verbose_name='Área minima')
    area_max = models.IntegerField(verbose_name='Área maxima')

    def __str__(self):
        return f'Intervalo de {self.area_min} a {self.area_max}'

    class Meta:
        verbose_name = 'Area de coleta'
        verbose_name_plural = 'Areas de coleta'
        ordering = ['area_min']


class Equipamentos(models.Model):
    filtro_dagua = models.IntegerField(verbose_name="filtro d'água")
    sifao_ladrao = models.IntegerField(verbose_name='Sifão ladrão')
    freio_dagua = models.IntegerField(verbose_name="Freio d'água")
    custo_implementacao = models.FloatField(verbose_name="custo de implementação em Dólares", default=0)

    area_de_coleta = models.ForeignKey(
        AreaDeColeta,
        on_delete=models.CASCADE,
        verbose_name='Area de coleta relacionada',
        related_name='equipamentos'
    )

    def __str__(self):
        return f"Filtro d'água:{self.filtro_dagua}m²\tSifão ladrão:{self.sifao_ladrao}mm\tFreio D'água:{self.freio_dagua}mm"

    class Meta:
        verbose_name = "Equipamento para dimensionamento"
        verbose_name_plural = "Equipamentos para dimensionamento"
        ordering = ['area_de_coleta']


class BombaDeAgua(models.Model):
    pavimentos_min = models.IntegerField(verbose_name="Mínimo de pavimentos")
    pavimentos_max = models.IntegerField(verbose_name='Máximo de pavimentos')
    potencia = models.FloatField('Cavalos de potência')
    consumo = models.FloatField("Consumo de enegia em Kilowatts/hora")
    tarifa = models.FloatField('Tarifa em Kilowatts/hora')
    succao = models.IntegerField('Sucção da bomba')
    recalque = models.IntegerField('Recalque da bomba')
    preco = models.FloatField('Preço de compra da bomba')
    horas_uso = models.IntegerField("Total horas de uso por ano")

    def __str__(self):
        return f"Bomba d'agua de {self.potencia} cavalos"
    class Meta:
        verbose_name = "Bomba d'água"
        verbose_name_plural = "Bombas d'água"
        ordering = ['potencia']


class CaixaDAgua(models.Model):
    min = models.IntegerField(verbose_name='Mínimo', default=0)
    max = models.IntegerField(verbose_name='Máximo', default=500)
    volume = models.IntegerField(verbose_name='Volume', default=500)
    valor = models.FloatField(verbose_name='Valor em dólares', default=53.05)

    def __str__(self):
        return f"Caixa d'água\t{self.volume}l\tUSD: {self.valor}"

    class Meta:
        verbose_name = "Caixa D'água"
        verbose_name_plural = "Caixas D'água"
        ordering = ['min']