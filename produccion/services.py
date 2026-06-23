from django.utils import timezone
from inventario.models import MovimientoInventario
from .models import ProduccionRegistro


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
        'operario': registro.operario.get_full_name() or registro.operario.username,
        'cantidad': registro.cantidad,
        'fecha': registro.timestamp.strftime('%d/%m/%Y'),
        'hora': registro.timestamp.strftime('%H:%M'),
        'estacion': registro.estacion.nombre,
    }
