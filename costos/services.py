from django.utils import timezone
from django.db.models import Sum
from produccion.models import ProduccionRegistro
from .models import CostoProduccion, TarifaOperario


def calcular_costo_diario(operario, referencia, fecha=None):
    if fecha is None:
        fecha = timezone.now().date()

    producciones_hoy = ProduccionRegistro.objects.filter(
        operario=operario,
        referencia=referencia,
        timestamp__date=fecha
    )

    total_unidades = producciones_hoy.aggregate(t=Sum('cantidad'))['t'] or 0

    costo = CostoProduccion.objects.filter(
        fecha=fecha,
        operario=operario,
        referencia=referencia
    ).first()

    if not costo:
        costo = CostoProduccion(
            fecha=fecha,
            operario=operario,
            referencia=referencia,
            unidades_producidas=total_unidades,
            horas_trabajadas=8.0
        )
    else:
        costo.unidades_producidas = total_unidades

    costo.calcular()
    costo.save()
    return costo
