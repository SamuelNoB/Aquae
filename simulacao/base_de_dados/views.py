from django.shortcuts import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required

from .mocks import *

# Create your views here.


@staff_member_required
def preenche_db_cidade(request):
    create_indices_pluviometricos()
    create_tarifas()
    return HttpResponse("Cidades inseridas")

@staff_member_required
def preenche_db_equips(request):
    create_areas_coleta()
    create_equipamentos()
    create_bombas_dagua()
    create_caixas_dagua()
    create_capacidades_de_tratamento()
    return HttpResponse("Equipamentos inseridos")
