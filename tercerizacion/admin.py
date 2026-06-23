from django.contrib import admin
from .models import OrdenTercerizacion


@admin.register(OrdenTercerizacion)
class OrdenTercerizacionAdmin(admin.ModelAdmin):
    list_display = ['consecutivo', 'referencia', 'cantidad_salida', 'cantidad_esperada', 'cantidad_retorno', 'estado', 'fecha_salida']
    list_filter = ['estado', 'referencia__tipo']
    search_fields = ['consecutivo', 'referencia__codigo']
    date_hierarchy = 'fecha_salida'
