from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum

from .models import CostoProduccion, TarifaOperario
from .services import calcular_costo_diario
from produccion.models import Referencia, ProduccionRegistro
from django.contrib.auth.models import User
from core.decorators import staff_required


@staff_required
def reporte_view(request):
    fecha = request.GET.get('fecha', timezone.now().date())

    if isinstance(fecha, str):
        from datetime import datetime
        fecha = datetime.strptime(fecha, '%Y-%m-%d').date()

    costos = CostoProduccion.objects.filter(fecha=fecha).select_related(
        'operario', 'referencia'
    ).order_by('referencia__tipo', 'referencia__codigo')

    total_hoy = costos.aggregate(
        t_mo=Sum('costo_mo'),
        t_mp=Sum('costo_mp'),
        t_merma=Sum('merma'),
        t_total=Sum('costo_total'),
        t_unidades=Sum('unidades_producidas'),
    )

    context = {
        'fecha': fecha,
        'costos': costos,
        'totales': total_hoy,
    }
    return render(request, 'costos/reporte.html', context)


@staff_required
def api_calcular(request):
    fecha = request.GET.get('fecha', timezone.now().date())
    if isinstance(fecha, str):
        from datetime import datetime
        fecha = datetime.strptime(fecha, '%Y-%m-%d').date()

    operarios = User.objects.filter(is_active=True)
    referencias = Referencia.objects.filter(activo=True)

    resultados = []
    for op in operarios:
        for ref in referencias:
            costo = calcular_costo_diario(op, ref, fecha)
            if costo.unidades_producidas > 0:
                resultados.append({
                    'operario': op.username,
                    'referencia': ref.codigo,
                    'unidades': costo.unidades_producidas,
                    'costo_mo': float(costo.costo_mo),
                    'costo_mp': float(costo.costo_mp),
                    'merma': float(costo.merma),
                    'costo_total': float(costo.costo_total),
                })

    return JsonResponse({'ok': True, 'fecha': str(fecha), 'resultados': resultados})
