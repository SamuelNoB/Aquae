from django.contrib import admin
from .models import UsosDeAgua, Simulacao

# Register your models here.


class UsosInline(admin.TabularInline):
    model = UsosDeAgua


class SimulacaoAdmin(admin.ModelAdmin):
    inlines = [UsosInline]


admin.site.register(Simulacao, SimulacaoAdmin)
admin.site.register(UsosDeAgua)
