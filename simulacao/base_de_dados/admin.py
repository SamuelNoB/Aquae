from django.contrib import admin
from .models import *

# Register your models here.

class TarifaDeAguaInline(admin.TabularInline):
    model = TarifaDeAgua

class IndicePluviometricoInline(admin.TabularInline):
    model = IndicePluviometrico


class EquipamentosInline(admin.TabularInline):
    model = Equipamentos


class AreaDeColetaAdmin(admin.ModelAdmin):
    inlines = [
        EquipamentosInline
    ]


class CidadeAdmin(admin.ModelAdmin):
    inlines = [
        IndicePluviometricoInline,
        TarifaDeAguaInline
    ]


admin.site.register(Cidade, CidadeAdmin)
admin.site.register(IndicePluviometrico)
admin.site.register(AreaDeColeta, AreaDeColetaAdmin)
admin.site.register(Equipamentos)
admin.site.register(BombaDeAgua)
admin.site.register(TarifaDeAgua)
admin.site.register(CaixaDAgua)
admin.site.register(CapacidadeDeTratamento)

