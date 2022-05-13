from django.apps import AppConfig


class BaseDeDadosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "simulacao.base_de_dados"
    verbose_name = "Base de dados"
