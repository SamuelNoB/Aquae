from django.urls import path
from .views import preenche_base_de_dados

app_name = 'base-de-dados'

urlpatterns = [
    path('insere-equipamentos/', preenche_base_de_dados, name='cria equipamentos')
]