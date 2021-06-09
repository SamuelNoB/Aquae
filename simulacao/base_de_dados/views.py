from django.shortcuts import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required

from .mocks import *

# Create your views here.


@staff_member_required
def preenche_base_de_dados(request):
    create_bombas_dagua()
    return HttpResponse("equipamentos inseridos")
