from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Referencia(models.Model):
    TIPO_CHOICES = [
        ('oro', 'Oro'),
        ('plata', 'Plata'),
    ]
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='oro')
    merma_pct = models.DecimalField(max_digits=5, decimal_places=2, default=3.0, help_text='% de merma aplicable')
    consumo_espuma_kg = models.DecimalField(max_digits=10, decimal_places=4, default=0, help_text='kg de espuma por unidad')
    consumo_tela_m = models.DecimalField(max_digits=10, decimal_places=4, default=0, help_text='metros de tela por unidad')
    costo_mp_estandar = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text='Costo materia prima por unidad')
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['tipo', 'codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre} ({self.get_tipo_display()})"


class Estacion(models.Model):
    TIPO_MOV_CHOICES = [
        ('suma', 'Suma al inventario'),
        ('resta', 'Resta del inventario'),
        ('ninguno', 'Sin movimiento de inventario'),
    ]
    nombre = models.CharField(max_length=50, unique=True)
    tipo_movimiento = models.CharField(max_length=10, choices=TIPO_MOV_CHOICES, default='suma')
    orden = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return self.nombre


class ProduccionRegistro(models.Model):
    operario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='producciones', null=True, blank=True)
    trabajador = models.ForeignKey('trabajadores.Trabajador', null=True, blank=True, on_delete=models.SET_NULL, related_name='producciones')
    referencia = models.ForeignKey(Referencia, on_delete=models.CASCADE, related_name='producciones')
    estacion = models.ForeignKey(Estacion, on_delete=models.CASCADE, related_name='producciones')
    cantidad = models.PositiveIntegerField(default=1)
    timestamp = models.DateTimeField(default=timezone.now)
    sticker_impreso = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
        ]

    @property
    def fecha(self):
        return self.timestamp.date()

    @property
    def hora(self):
        return self.timestamp.time()

    def __str__(self):
        who = self.trabajador.nombre_completo if self.trabajador else (self.operario.username if self.operario else '?')
        return f"{self.referencia.codigo} x{self.cantidad} - {self.estacion.nombre} [{who}] {self.timestamp:%H:%M}"
