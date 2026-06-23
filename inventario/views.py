from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum

from produccion.models import Referencia
from .models import MovimientoInventario, MateriaPrima
from .services import stock_actual_por_referencia


@login_required
def stock_view(request):
    referencias = Referencia.objects.filter(activo=True)

    stock_data = []
    for ref in referencias:
        stock = stock_actual_por_referencia(ref)
        stock_data.append({
            'id': ref.id,
            'codigo': ref.codigo,
            'nombre': ref.nombre,
            'tipo': ref.tipo,
            'tipo_display': ref.get_tipo_display(),
            'stock': stock,
        })

    movimientos = MovimientoInventario.objects.select_related(
        'referencia', 'estacion'
    ).order_by('-fecha')[:50]

    context = {
        'stock_data': stock_data,
        'movimientos': movimientos,
    }
    return render(request, 'inventario/stock.html', context)


@login_required
def materia_prima_view(request):
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        kg = request.POST.get('cantidad_kg', 0) or 0
        unidades = request.POST.get('cantidad_unidades', 0) or 0
        descripcion = request.POST.get('descripcion', '')

        MateriaPrima.objects.create(
            tipo=tipo,
            cantidad_kg=float(kg),
            cantidad_unidades=float(unidades),
            registrado_por=request.user,
            descripcion=descripcion,
        )

    registros = MateriaPrima.objects.order_by('-fecha')[:20]

    saldo_espuma = MateriaPrima.objects.filter(tipo='espuma').aggregate(
        t=Sum('cantidad_kg')
    )['t'] or 0

    saldo_rollos = MateriaPrima.objects.filter(tipo='rollo').aggregate(
        t=Sum('cantidad_unidades')
    )['t'] or 0

    saldo_tela = MateriaPrima.objects.filter(tipo='tela').aggregate(
        t=Sum('cantidad_kg')
    )['t'] or 0

    context = {
        'registros': registros,
        'saldo_espuma': saldo_espuma,
        'saldo_rollos': saldo_rollos,
        'saldo_tela': saldo_tela,
    }
    return render(request, 'inventario/materia_prima.html', context)


@login_required
def api_stock_actual(request):
    referencias = Referencia.objects.filter(activo=True)
    data = []
    for ref in referencias:
        stock = stock_actual_por_referencia(ref)
        data.append({
            'id': ref.id,
            'codigo': ref.codigo,
            'stock': stock,
        })
    return JsonResponse({'ok': True, 'data': data})
