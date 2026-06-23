from django.db.models import Sum, Q
from django.utils import timezone
from inventario.models import MovimientoInventario
from produccion.models import ProduccionRegistro


def stock_actual_por_referencia(referencia):
    entradas = MovimientoInventario.objects.filter(
        referencia=referencia, tipo='entrada'
    ).aggregate(total=Sum('cantidad'))['total'] or 0

    salidas = MovimientoInventario.objects.filter(
        referencia=referencia, tipo='salida'
    ).aggregate(total=Sum('cantidad'))['total'] or 0

    return entradas - salidas


def stock_actual_por_estacion(referencia, estacion):
    entradas = MovimientoInventario.objects.filter(
        referencia=referencia, tipo='entrada', estacion=estacion
    ).aggregate(total=Sum('cantidad'))['total'] or 0

    salidas = MovimientoInventario.objects.filter(
        referencia=referencia, tipo='salida', estacion=estacion
    ).aggregate(total=Sum('cantidad'))['total'] or 0

    return entradas - salidas


def calcular_consumo_tela(fecha_inicio, fecha_fin=None):
    if fecha_fin is None:
        fecha_fin = timezone.now()

    producciones = ProduccionRegistro.objects.filter(
        timestamp__date__gte=fecha_inicio,
        timestamp__date__lte=fecha_fin
    )

    total_tela = 0
    for prod in producciones:
        total_tela += prod.cantidad * prod.referencia.consumo_tela_m

    return total_tela
