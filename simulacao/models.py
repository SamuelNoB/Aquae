from django.db import models

# Create your models here.


class DemandasDeAgua(models.Model):

    nome = models.CharField(verbose_name='Nome do consumo', max_length=100)
    frequencia_mensal = models.IntegerField(verbose_name='Frequencia mensal de uso')
    indicador = models.FloatField(verbose_name='Indicador de uso final', blank=True)

    simulacao = models.ForeignKey(
        'simulacao',
        verbose_name='Simulacao pertencente',
        related_name='demandas',
        on_delete=models.CASCADE
    )


    def __str__(self):
        return f"{self.nome} {str(self.simulacao)}"

    class Meta:
        verbose_name = 'Demanda de Água'
        verbose_name_plural = 'Demandas de Água'
        ordering = ['nome']
        constraints = [
            models.UniqueConstraint(fields=['simulacao', 'nome'], name='simulação única')
        ]


class Simulacao(models.Model):

    RESIDENCIA_CHOICES = (
        (0, 'casa'),
        (1, 'apartamento')
    )

    tipo_residencia = models.IntegerField(verbose_name='Tipo da residencia', choices=RESIDENCIA_CHOICES)
    n_apts = models.IntegerField(verbose_name='Número de apartamentos', blank=True, null=True)
    n_pavimentos = models.IntegerField(verbose_name='Número de pavimentos', default=1)
    n_pessoas = models.IntegerField(verbose_name='Número de residentes', null=False)
    tarifa_esgoto = models.FloatField(verbose_name='Porcentagem da tarifa de esgoto')
    consumo_mensal = models.FloatField(verbose_name='Consumo mensal de água')
    area_cobertura = models.FloatField(verbose_name='Área de cobertura')
    area_pisos = models.FloatField(verbose_name='Área de pisos')
    area_irrigacao = models.FloatField(verbose_name='Área de irrigação')

    def __str__(self):
        return f'Simulação {self.id}'

    class Meta:
        verbose_name = 'Simulação'
        verbose_name_plural = 'Simulações'


class OfertasDeAgua(models.Model):

    def __str__(self):
        return f"{self.nome} {str(self.simulacao)}"

    nome = models.CharField(verbose_name="Nome da oferta", max_length=100)
    frequencia_mensal = models.IntegerField(verbose_name='Frequencia mensal de uso')
    indicador = models.FloatField(verbose_name='Indicador de uso final', blank=True)

    simulacao = models.ForeignKey(
        Simulacao,
        verbose_name='Simulacao pertencente',
        related_name='ofertas',
        on_delete=models.CASCADE
    )
