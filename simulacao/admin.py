from django.contrib import admin
from .models import DemandasDeAgua, Simulacao, OfertasDeAgua

# Register your models here.


class DemandasInline(admin.TabularInline):
    model = DemandasDeAgua


class SimulacaoAdmin(admin.ModelAdmin):
    inlines = [
        DemandasInline
    ]


admin.site.register(Simulacao, SimulacaoAdmin)
admin.site.register(DemandasDeAgua)
admin.site.register(OfertasDeAgua)

