from django.db import models
from .utils import ESTADOS_BR
from .base_de_dados.models import Cidade


# Create your models here.


class UsosDeAgua(models.Model):
    nome = models.CharField(verbose_name="Nome do consumo", max_length=100)
    frequencia_mensal = models.IntegerField(
        verbose_name="Frequencia mensal de uso")

    indicador = models.FloatField(
        verbose_name="Indicador de uso final", blank=True)
    METROS_QUADRADOS = "Litros/m²/dia"
    PESSOA = "Litros/pessoa/dia"
    UNIDADE_CHOICES = [
        (METROS_QUADRADOS, "Litros/m²/dia"),
        (PESSOA, "Litros/pessoa/dia"),
    ]
    unidade = models.CharField(
        max_length=17,
        choices=UNIDADE_CHOICES,
        verbose_name="Unidade de medida do indicador de uso final",
        default=PESSOA,
    )

    demanda = models.BooleanField(
        verbose_name="Utilizado como demanda", blank=True)
    oferta = models.BooleanField(
        verbose_name="Utilizado como oferta", blank=True)

    simulacao = models.ForeignKey(
        "simulacao",
        verbose_name="Simulacao pertencente",
        related_name="usos",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.nome} {str(self.simulacao)}"

    class Meta:
        verbose_name = "Demanda de Água"
        verbose_name_plural = "Demandas de Água"
        ordering = ["nome"]
        constraints = [
            models.UniqueConstraint(
                fields=["simulacao", "nome"], name="simulação única"
            )
        ]


class Simulacao(models.Model):

    RESIDENCIA_CHOICES = ((0, "casa"), (1, "apartamento"))
    ESTADO_CHOICES = ESTADOS_BR
    CIDADES_NOME = list(map(lambda cidade: cidade.nome, Cidade.objects.all()))
    CIDADE_CHOICES = zip(CIDADES_NOME, CIDADES_NOME)

    estado = models.CharField(
        verbose_name="Estado (UF)",
        max_length=24,
        choices=ESTADO_CHOICES,
        default="DF",
    )
    cidade = models.CharField(
        verbose_name="Cidade",
        max_length=50,
        choices=CIDADE_CHOICES,
        default="BRASILIA",
    )
    tipo_residencia = models.IntegerField(
        verbose_name="Tipo da residencia", choices=RESIDENCIA_CHOICES
    )
    n_apts = models.IntegerField(
        verbose_name="Número de apartamentos", blank=True, null=True
    )
    n_pavimentos = models.IntegerField(
        verbose_name="Número de pavimentos", default=1)
    n_pessoas = models.IntegerField(
        verbose_name="Número de residentes", null=False)
    tarifa_esgoto = models.FloatField(
        verbose_name="Porcentagem da tarifa de esgoto")
    consumo_mensal = models.FloatField(verbose_name="Consumo mensal de água")
    area_cobertura = models.FloatField(verbose_name="Área de cobertura")
    area_pisos = models.FloatField(verbose_name="Área de pisos")
    area_irrigacao = models.FloatField(verbose_name="Área de irrigação")

    jan = models.BooleanField(
        verbose_name="Estiagem em janeiro", default=False)
    fev = models.BooleanField(
        verbose_name="Estiagem em fevereiro", default=False)
    mar = models.BooleanField(verbose_name="Estiagem em março", default=False)
    abr = models.BooleanField(verbose_name="Estiagem em abril", default=False)
    mai = models.BooleanField(verbose_name="Estiagem em maio", default=True)
    jun = models.BooleanField(verbose_name="Estiagem em junho", default=True)
    jul = models.BooleanField(verbose_name="Estiagem em julho", default=True)
    ago = models.BooleanField(verbose_name="Estiagem em agosto", default=True)
    set = models.BooleanField(
        verbose_name="Estiagem em setembro", default=True)
    out = models.BooleanField(
        verbose_name="Estiagem em outubro", default=False)
    nov = models.BooleanField(
        verbose_name="Estiagem em novembro", default=False)
    dez = models.BooleanField(
        verbose_name="Estiagem em dezembro", default=False)

    def __str__(self):
        return f"Simulação {self.id}"

    class Meta:
        verbose_name = "Simulação"
        verbose_name_plural = "Simulações"
