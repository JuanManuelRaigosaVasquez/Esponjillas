from django.db import models
from django.contrib.auth.models import User


class Trabajador(models.Model):
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100, blank=True)
    cedula = models.CharField(max_length=30, unique=True, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True)
    activo = models.BooleanField(default=True)
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='trabajador')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nombre', 'apellidos']

    def __str__(self):
        if self.apellidos:
            return f"{self.nombre} {self.apellidos}"
        return self.nombre

    @property
    def nombre_completo(self):
        return str(self)

    @property
    def iniciales(self):
        inicial = self.nombre[0].upper() if self.nombre else ''
        apellido_inicial = self.apellidos[0].upper() if self.apellidos else ''
        return f"{inicial}{apellido_inicial}"
