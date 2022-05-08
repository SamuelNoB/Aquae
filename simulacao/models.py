from django.db import models

# Create your models here.


class DemandasDeAgua(models.Model):

    nome = models.CharField(verbose_name="Nome do consumo", max_length=100)
    frequencia_mensal = models.IntegerField(verbose_name="Frequencia mensal de uso")

    indicador = models.FloatField(verbose_name="Indicador de uso final", blank=True)
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

    simulacao = models.ForeignKey(
        "simulacao",
        verbose_name="Simulacao pertencente",
        related_name="demandas",
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
    ESTADO_CHOICES = (
        ("Acre (AC)", "AC"),
        ("Alagoas (AL)", "AL"),
        ("Amapá (AP)", "AP"),
        ("Amazonas (AM)", "AM"),
        ("Bahia (BA)", "BA"),
        ("Ceará (CE)", "CE"),
        ("Distrito Federal (DF)", "DF"),
        ("Espírito Santo (ES)", "ES"),
        ("Goiás (GO)", "GO"),
        ("Maranhão (MA)", "MA"),
        ("Mato Grosso (MT)", "MT"),
        ("Mato Grosso do Sul (MS)", "MS"),
        ("Minas Gerais (MG)", "MG"),
        ("Pará (PA)", "PA"),
        ("Paraíba (PB)", "PB"),
        ("Paraná (PR)", "PR"),
        ("Pernambuco (PE)", "PE"),
        ("Piauí (PI)", "PI"),
        ("Rio de Janeiro (RJ)", "RJ"),
        ("Rio Grande do Norte (RN)", "RN"),
        ("Rio Grande do Sul (RS)", "RS"),
        ("Rondônia (RO) ", "RO"),
        ("Roraima (RR)", "RR"),
        ("Santa Catarina (SC)", "SC"),
        ("São Paulo (SP)", "SP"),
        ("Sergipe (SE)", "SE"),
        ("Tocantins (TO)", "TO"),
    )

    estado = models.CharField(
        verbose_name="Estado (UF)",
        max_length=24,
        choices=ESTADO_CHOICES,
        default="Distrito Federal (DF)",
    )
    tipo_residencia = models.IntegerField(
        verbose_name="Tipo da residencia", choices=RESIDENCIA_CHOICES
    )
    n_apts = models.IntegerField(
        verbose_name="Número de apartamentos", blank=True, null=True
    )
    n_pavimentos = models.IntegerField(verbose_name="Número de pavimentos", default=1)
    n_pessoas = models.IntegerField(verbose_name="Número de residentes", null=False)
    tarifa_esgoto = models.FloatField(verbose_name="Porcentagem da tarifa de esgoto")
    consumo_mensal = models.FloatField(verbose_name="Consumo mensal de água")
    area_cobertura = models.FloatField(verbose_name="Área de cobertura")
    area_pisos = models.FloatField(verbose_name="Área de pisos")
    area_irrigacao = models.FloatField(verbose_name="Área de irrigação")

    def __str__(self):
        return f"Simulação {self.id}"

    class Meta:
        verbose_name = "Simulação"
        verbose_name_plural = "Simulações"


class OfertasDeAgua(models.Model):
    def __str__(self):
        return f"{self.nome} {str(self.simulacao)}"

    nome = models.CharField(verbose_name="Nome da oferta", max_length=100)
    frequencia_mensal = models.IntegerField(verbose_name="Frequencia mensal de uso")

    indicador = models.FloatField(verbose_name="Indicador de uso final", blank=True)
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

    simulacao = models.ForeignKey(
        Simulacao,
        verbose_name="Simulacao pertencente",
        related_name="ofertas",
        on_delete=models.CASCADE,
    )
