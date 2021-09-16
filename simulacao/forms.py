from django import forms
from .models import Simulacao, DemandasDeAgua, OfertasDeAgua


class EdificacaoForm(forms.ModelForm):
    class Meta:
        model = Simulacao
        fields = '__all__'


class DemandasForm(forms.ModelForm):
    class Meta:
        model = DemandasDeAgua
        fields = '__all__'


class OfertasForm(forms.ModelForm):
    class Meta:
        model = OfertasDeAgua
        fields = '__all__'


class SimulacaoAAPForm(forms.Form):
    intervalos_de_cisterna = forms.IntegerField(min_value=0, label= 'Intervalo', initial=5)
    taxa_de_juros = forms.FloatField(max_value=100, min_value=0, label="Taxa de juros", initial=3)


class DemandaSimulacaoAAPForm(forms.Form):
    ativo = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input",
                                                                 'style': "margin: 0px;transform: scale(0.8)"}))
    nome_consumo = forms.CharField()
    demanda_mensal = forms.FloatField()
