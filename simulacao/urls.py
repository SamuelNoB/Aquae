from django.urls import path, re_path, include
from . import views

app_name = 'simulacao'

urlpatterns = [
    path('base-de-dados/', include('simulacao.base_de_dados.urls', namespace='base de dados')),
    path('edificacao/', views.edificacao, name='edificacao'),
    re_path(r'selciona-simulacao/(?P<pk>\d+)/$', views.seleciona_simulacao, name='seleciona_simulacao'),
    re_path(r'simulacao-aap/(?P<pk>\d+)/$', views.SimulacaoAAP.as_view(), name='simulacao-aap')

]