from django.urls import path
from .views import preenche_db_cidade, preenche_db_equips

app_name = 'base-de-dados'

urlpatterns = [
    path('insere-equipamentos/', preenche_db_equips, name='cria equipamentos'),
    path('insere-cidades/', preenche_db_cidade, name='cria cidades')
]