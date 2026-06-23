from django.contrib import admin
from .models import Referencia, Estacion, ProduccionRegistro


@admin.register(Referencia)
class ReferenciaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'tipo', 'merma_pct', 'costo_mp_estandar', 'activo']
    list_filter = ['tipo', 'activo']
    search_fields = ['codigo', 'nombre']


@admin.register(Estacion)
class EstacionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo_movimiento', 'orden', 'activo']
    list_filter = ['tipo_movimiento', 'activo']


@admin.register(ProduccionRegistro)
class ProduccionRegistroAdmin(admin.ModelAdmin):
    list_display = ['id', 'operario', 'referencia', 'estacion', 'cantidad', 'timestamp', 'sticker_impreso']
    list_filter = ['estacion', 'referencia__tipo', 'sticker_impreso']
    search_fields = ['operario__username', 'referencia__codigo']
    date_hierarchy = 'timestamp'
