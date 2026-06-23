from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class TarifaOperario(models.Model):
    operario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tarifa')
    tarifa_hora = models.DecimalField(max_digits=10, decimal_places=2, default=5000, help_text='COP por hora')
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Tarifas de operarios'

    def __str__(self):
        return f"{self.operario.username}: ${self.tarifa_hora}/h"


class CostoProduccion(models.Model):
    fecha = models.DateField(default=timezone.now)
    operario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='costos')
    referencia = models.ForeignKey('produccion.Referencia', on_delete=models.CASCADE, related_name='costos')
    unidades_producidas = models.PositiveIntegerField(default=0)
    horas_trabajadas = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    costo_mo = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text='Costo mano de obra')
    costo_mp = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text='Costo materia prima')
    merma = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text='Costo por merma')
    costo_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['-fecha', 'referencia']),
            models.Index(fields=['-fecha', 'operario']),
        ]

    def calcular(self):
        tarifa = TarifaOperario.objects.filter(operario=self.operario, activo=True).first()
        tarifa_hora = tarifa.tarifa_hora if tarifa else 5000
        self.costo_mo = self.horas_trabajadas * tarifa_hora
        self.costo_mp = self.unidades_producidas * self.referencia.costo_mp_estandar
        subtotal = self.costo_mo + self.costo_mp
        self.merma = subtotal * (self.referencia.merma_pct / 100)
        self.costo_total = subtotal + self.merma
        return self.costo_total

    def __str__(self):
        return f"Costo {self.fecha} - {self.operario.username} - {self.referencia.codigo} = ${self.costo_total}"
