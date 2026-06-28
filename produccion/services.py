from django.utils import timezone
from inventario.models import MovimientoInventario
from .models import ProduccionRegistro


def build_sparkline_path(values, width=100, height=50, pad=1):
    if not values:
        return ""

    n = len(values)
    max_v = max(values)
    min_v = min(values)
    rng = max_v - min_v

    points = []
    for i, v in enumerate(values):
        x = pad + (width - 2 * pad) * i / (n - 1) if n > 1 else width / 2
        if rng == 0:
            y = height / 2
        else:
            y = height - pad - (v - min_v) / rng * (height - 3 * pad)
        points.append(f"{x:.1f},{y:.1f}")

    d = f"M{points[0]}"
    for p in points[1:]:
        d += f" L{p}"
    d += f" L{width},{height} L0,{height} Z"
    return d


def procesar_produccion(registro):
    estacion = registro.estacion
    referencia = registro.referencia
    cantidad = registro.cantidad

    if estacion.tipo_movimiento == 'suma':
        MovimientoInventario.objects.create(
            tipo='entrada',
            referencia=referencia,
            estacion=estacion,
            cantidad=cantidad,
            produccion=registro,
            origen=f'Produccion #{registro.id} - {estacion.nombre}'
        )
    elif estacion.tipo_movimiento == 'resta':
        MovimientoInventario.objects.create(
            tipo='salida',
            referencia=referencia,
            estacion=estacion,
            cantidad=cantidad,
            produccion=registro,
            origen=f'Produccion #{registro.id} - {estacion.nombre}'
        )

    return registro


def generar_sticker_data(registro):
    return {
        'consecutivo': f"STK-{registro.id:06d}",
        'referencia': registro.referencia.codigo,
        'tipo': registro.referencia.get_tipo_display(),
        'operario': registro.trabajador.nombre_completo if registro.trabajador else (registro.operario.get_full_name() or registro.operario.username if registro.operario else '—'),
        'cantidad': registro.cantidad,
        'fecha': registro.timestamp.strftime('%d/%m/%Y'),
        'hora': registro.timestamp.strftime('%H:%M'),
        'estacion': registro.estacion.nombre,
    }
