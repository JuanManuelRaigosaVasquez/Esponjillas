from django.db import models
from django.utils import timezone


class OrdenTercerizacion(models.Model):
    ESTADO_CHOICES = [
        ('abierta', 'Abierta'),
        ('cerrada', 'Cerrada'),
    ]
    consecutivo = models.CharField(max_length=20, unique=True, help_text='Autogenerado')
    referencia = models.ForeignKey('produccion.Referencia', on_delete=models.CASCADE, related_name='ordenes_tercerizacion')
    cantidad_salida = models.PositiveIntegerField()
    cantidad_esperada = models.PositiveIntegerField(help_text='Cantidad esperada de retorno en pacas')
    cantidad_retorno = models.PositiveIntegerField(null=True, blank=True, help_text='Cantidad real al retornar')
    fecha_salida = models.DateTimeField(default=timezone.now)
    fecha_retorno = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='abierta')
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha_salida']

    def save(self, *args, **kwargs):
        if not self.consecutivo:
            ultimo = OrdenTercerizacion.objects.order_by('-id').first()
            num = (ultimo.id + 1) if ultimo else 1
            self.consecutivo = f"OT-{num:05d}"
        super().save(*args, **kwargs)

    def cerrar(self, cantidad_retorno):
        if self.estado == 'cerrada':
            raise ValueError('La orden ya esta cerrada')
        self.cantidad_retorno = cantidad_retorno
        self.fecha_retorno = timezone.now()
        self.estado = 'cerrada'
        self.save()

    def diferencia(self):
        if self.cantidad_retorno is not None:
            return self.cantidad_esperada - self.cantidad_retorno
        return None

    def __str__(self):
        return f"{self.consecutivo} - {self.referencia.codigo} ({self.get_estado_display()})"
