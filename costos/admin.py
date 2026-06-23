from django.contrib import admin
from .models import TarifaOperario, CostoProduccion


@admin.register(TarifaOperario)
class TarifaOperarioAdmin(admin.ModelAdmin):
    list_display = ['operario', 'tarifa_hora', 'activo']


@admin.register(CostoProduccion)
class CostoProduccionAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'operario', 'referencia', 'unidades_producidas', 'costo_mo', 'costo_mp', 'merma', 'costo_total']
    list_filter = ['fecha', 'referencia__tipo']
    date_hierarchy = 'fecha'
