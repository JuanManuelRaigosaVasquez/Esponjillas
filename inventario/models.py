from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class MovimientoInventario(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    ]
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    referencia = models.ForeignKey('produccion.Referencia', on_delete=models.CASCADE, related_name='movimientos')
    estacion = models.ForeignKey('produccion.Estacion', on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos')
    cantidad = models.PositiveIntegerField()
    fecha = models.DateTimeField(default=timezone.now)
    origen = models.CharField(max_length=200, blank=True, help_text='Descripcion del origen del movimiento')
    produccion = models.ForeignKey('produccion.ProduccionRegistro', on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos')

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.referencia.codigo} x{self.cantidad} [{self.fecha:%Y-%m-%d %H:%M}]"


class MateriaPrima(models.Model):
    TIPO_CHOICES = [
        ('espuma', 'Espuma'),
        ('rollo', 'Rollo'),
        ('tela', 'Tela'),
    ]
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    cantidad_kg = models.DecimalField(max_digits=12, decimal_places=3, default=0, help_text='Cantidad en kilogramos')
    cantidad_unidades = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text='Cantidad en unidades (rollos)')
    fecha = models.DateTimeField(default=timezone.now)
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='registros_mp')
    descripcion = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.cantidad_kg}kg / {self.cantidad_unidades}u"


class ConsumoEstandar(models.Model):
    referencia = models.OneToOneField('produccion.Referencia', on_delete=models.CASCADE, related_name='consumo_estandar')
    espuma_kg_por_unidad = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    tela_m_por_unidad = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    rollo_unidades_por_unidad = models.DecimalField(max_digits=10, decimal_places=4, default=0)

    class Meta:
        verbose_name_plural = 'Consumos estandar'

    def __str__(self):
        return f"Consumo estandar: {self.referencia.codigo}"
