from django.shortcuts import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required

from .mocks import *

# Create your views here.


@staff_member_required
def preenche_base_de_dados(request):
    create_indices_pluviometricos()
    create_areas_coleta()
    create_equipamentos()
    create_bombas_dagua()
    create_caixas_dagua()
    return HttpResponse("equipamentos inseridos")
