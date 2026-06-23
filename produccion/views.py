from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

from .models import Referencia, Estacion, ProduccionRegistro
from .services import procesar_produccion, generar_sticker_data
from inventario.services import stock_actual_por_referencia
from inventario.models import MovimientoInventario


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('produccion:operator')
        messages.error(request, 'Credenciales invalidas')
    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('produccion:login')


@login_required
def operator_view(request):
    referencias = Referencia.objects.filter(activo=True)
    estaciones = Estacion.objects.filter(activo=True)
    estacion_actual = request.GET.get('estacion')

    if estacion_actual:
        try:
            estacion_actual = Estacion.objects.get(id=int(estacion_actual), activo=True)
        except (ValueError, Estacion.DoesNotExist):
            estacion_actual = estaciones.first()
    elif estaciones.exists():
        estacion_actual = estaciones.first()

    ultimos = ProduccionRegistro.objects.filter(
        operario=request.user,
        timestamp__date=timezone.now().date()
    ).order_by('-timestamp')[:20]

    context = {
        'referencias': referencias,
        'estaciones': estaciones,
        'estacion_actual': estacion_actual,
        'ultimos': ultimos,
        'hoy': timezone.now().date(),
    }
    return render(request, 'produccion/operator.html', context)


@csrf_exempt
@require_POST
@login_required
def api_registrar(request):
    try:
        data = json.loads(request.body)
        referencia_id = int(data.get('referencia_id'))
        estacion_id = int(data.get('estacion_id'))
        cantidad = int(data.get('cantidad', 1))

        referencia = Referencia.objects.get(id=referencia_id, activo=True)
        estacion = Estacion.objects.get(id=estacion_id, activo=True)

        registro = ProduccionRegistro.objects.create(
            operario=request.user,
            referencia=referencia,
            estacion=estacion,
            cantidad=cantidad,
        )

        procesar_produccion(registro)

        stock = stock_actual_por_referencia(referencia)

        return JsonResponse({
            'ok': True,
            'id': registro.id,
            'referencia': referencia.codigo,
            'codigo': referencia.codigo,
            'tipo': referencia.get_tipo_display(),
            'estacion': estacion.nombre,
            'cantidad': cantidad,
            'hora': registro.timestamp.strftime('%H:%M'),
            'stock_actual': stock,
        })
    except Referencia.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Referencia no encontrada'}, status=400)
    except Estacion.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Estacion no valida'}, status=400)
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@login_required
def dashboard_view(request):
    hoy = timezone.now().date()

    total_hoy = ProduccionRegistro.objects.filter(
        timestamp__date=hoy
    ).aggregate(t=Sum('cantidad'))['t'] or 0

    por_estacion = ProduccionRegistro.objects.filter(
        timestamp__date=hoy
    ).values('estacion__nombre').annotate(total=Sum('cantidad')).order_by('-total')

    por_referencia = ProduccionRegistro.objects.filter(
        timestamp__date=hoy
    ).values('referencia__codigo', 'referencia__tipo').annotate(total=Sum('cantidad')).order_by('-total')

    ultimos_movimientos = MovimientoInventario.objects.order_by('-fecha')[:10]

    referencias = Referencia.objects.filter(activo=True)
    stock_data = []
    for ref in referencias:
        s = stock_actual_por_referencia(ref)
        stock_data.append({'ref': ref, 'stock': s})

    context = {
        'hoy': hoy,
        'total_hoy': total_hoy,
        'por_estacion': por_estacion,
        'por_referencia': por_referencia,
        'ultimos_movimientos': ultimos_movimientos,
        'stock_data': stock_data,
    }
    return render(request, 'produccion/dashboard.html', context)


@login_required
def imprimir_sticker(request, pk):
    registro = get_object_or_404(ProduccionRegistro, id=pk)
    sticker = generar_sticker_data(registro)
    registro.sticker_impreso = True
    registro.save()

    context = {
        'sticker': sticker,
        'registro': registro,
    }
    return render(request, 'produccion/sticker_print.html', context)
