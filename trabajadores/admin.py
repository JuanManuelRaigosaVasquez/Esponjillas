from django.contrib import admin
from .models import Trabajador


@admin.register(Trabajador)
class TrabajadorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellidos', 'cedula', 'telefono', 'activo', 'fecha_creacion']
    list_filter = ['activo']
    search_fields = ['nombre', 'apellidos', 'cedula']
