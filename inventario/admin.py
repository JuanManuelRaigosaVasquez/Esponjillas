from django.contrib import admin
from .models import MovimientoInventario, MateriaPrima, ConsumoEstandar


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ['id', 'tipo', 'referencia', 'estacion', 'cantidad', 'fecha']
    list_filter = ['tipo', 'estacion', 'referencia__tipo']
    date_hierarchy = 'fecha'


@admin.register(MateriaPrima)
class MateriaPrimaAdmin(admin.ModelAdmin):
    list_display = ['id', 'tipo', 'cantidad_kg', 'cantidad_unidades', 'fecha']
    list_filter = ['tipo']
    date_hierarchy = 'fecha'


@admin.register(ConsumoEstandar)
class ConsumoEstandarAdmin(admin.ModelAdmin):
    list_display = ['referencia', 'espuma_kg_por_unidad', 'tela_m_por_unidad']
