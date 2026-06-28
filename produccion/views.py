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
from datetime import timedelta
from django.db.models.functions import ExtractHour

from .models import Referencia, Estacion, ProduccionRegistro
from .services import procesar_produccion, generar_sticker_data, build_sparkline_path
from inventario.services import stock_actual_por_referencia
from inventario.models import MovimientoInventario
from trabajadores.models import Trabajador
from core.decorators import staff_required


def login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('produccion:dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            if user.is_staff:
                login(request, user)
                return redirect('produccion:dashboard')
            else:
                messages.warning(request, 'Los trabajadores usan la pantalla de registro rapido. Los supervisores usan /login/.')
                return redirect('produccion:registro_rapido')
        messages.error(request, 'Credenciales invalidas')
    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('produccion:login')


@staff_required
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
@staff_required
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


def registro_rapido_view(request):
    trabajadores = Trabajador.objects.filter(activo=True)
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
        trabajador__isnull=False,
        timestamp__date=timezone.now().date()
    ).select_related('trabajador', 'referencia').order_by('-timestamp')[:20]

    context = {
        'trabajadores': trabajadores,
        'referencias': referencias,
        'estaciones': estaciones,
        'estacion_actual': estacion_actual,
        'ultimos': ultimos,
        'hoy': timezone.now().date(),
    }
    return render(request, 'produccion/registro_rapido.html', context)


@csrf_exempt
@require_POST
def api_registrar_rapido(request):
    try:
        data = json.loads(request.body)
        trabajador_id = int(data.get('trabajador_id'))
        referencia_id = int(data.get('referencia_id'))
        estacion_id = int(data.get('estacion_id'))
        cantidad = int(data.get('cantidad', 1))

        trabajador = Trabajador.objects.get(id=trabajador_id, activo=True)
        referencia = Referencia.objects.get(id=referencia_id, activo=True)
        estacion = Estacion.objects.get(id=estacion_id, activo=True)

        registro = ProduccionRegistro.objects.create(
            trabajador=trabajador,
            operario=trabajador.user if trabajador.user else None,
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
            'trabajador': trabajador.nombre_completo,
            'estacion': estacion.nombre,
            'cantidad': cantidad,
            'hora': registro.timestamp.strftime('%H:%M'),
            'stock_actual': stock,
        })
    except Trabajador.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Trabajador no encontrado'}, status=400)
    except Referencia.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Referencia no encontrada'}, status=400)
    except Estacion.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Estacion no valida'}, status=400)
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@staff_required
def dashboard_view(request):
    hoy = timezone.now().date()
    ayer = hoy - timedelta(days=1)

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

    trabajadores_data = []
    for t in Trabajador.objects.filter(activo=True).order_by('nombre'):
        total_hoy_t = ProduccionRegistro.objects.filter(
            trabajador=t, timestamp__date=hoy
        ).aggregate(t=Sum('cantidad'))['t'] or 0
        registros_hoy = ProduccionRegistro.objects.filter(
            trabajador=t, timestamp__date=hoy
        ).count()
        total_ayer_t = ProduccionRegistro.objects.filter(
            trabajador=t, timestamp__date=ayer
        ).aggregate(t=Sum('cantidad'))['t'] or 0

        if total_ayer_t > 0:
            change_pct = round((total_hoy_t - total_ayer_t) / total_ayer_t * 100, 1)
        elif total_hoy_t > 0:
            change_pct = 100
        else:
            change_pct = 0

        series = []
        for offset in range(6, -1, -1):
            dia = hoy - timedelta(days=offset)
            d = ProduccionRegistro.objects.filter(
                trabajador=t, timestamp__date=dia
            ).aggregate(t=Sum('cantidad'))['t'] or 0
            series.append(d)
        svg_path = build_sparkline_path(series)

        trabajadores_data.append({
            'id': t.id,
            'nombre': t.nombre_completo,
            'iniciales': t.iniciales,
            'total_hoy': total_hoy_t,
            'registros_hoy': registros_hoy,
            'change_pct': change_pct,
            'svg_path': svg_path,
        })

    trabajadores_data.sort(key=lambda x: x['total_hoy'], reverse=True)

    context = {
        'hoy': hoy,
        'total_hoy': total_hoy,
        'por_estacion': por_estacion,
        'por_referencia': por_referencia,
        'ultimos_movimientos': ultimos_movimientos,
        'stock_data': stock_data,
        'trabajadores_data': trabajadores_data,
    }
    return render(request, 'produccion/dashboard.html', context)


@staff_required
def analiticas_view(request):
    context = {
        'hoy': timezone.now().date(),
        'filtros': [
            ('Hoy', 1),
            ('7 dias', 7),
            ('14 dias', 14),
            ('30 dias', 30),
        ],
    }
    return render(request, 'produccion/analiticas.html', context)


@staff_required
def api_analiticas(request):
    hoy = timezone.now().date()
    dias = int(request.GET.get('dias', 7))
    inicio = hoy - timedelta(days=dias - 1)

    diario_qs = (ProduccionRegistro.objects
        .filter(timestamp__date__gte=inicio)
        .values('timestamp__date')
        .annotate(total=Sum('cantidad'))
        .order_by('timestamp__date'))
    diario_dict = {d['timestamp__date']: d['total'] for d in diario_qs}
    diario = []
    for i in range(dias):
        dia = inicio + timedelta(days=i)
        diario.append({
            'fecha': dia.strftime('%d/%m'),
            'total': diario_dict.get(dia, 0),
        })

    por_referencia = list(ProduccionRegistro.objects
        .filter(timestamp__date__gte=inicio)
        .values('referencia__codigo', 'referencia__nombre', 'referencia__tipo')
        .annotate(total=Sum('cantidad'))
        .order_by('-total'))

    por_estacion = list(ProduccionRegistro.objects
        .filter(timestamp__date__gte=inicio)
        .values('estacion__nombre', 'estacion__tipo_movimiento')
        .annotate(total=Sum('cantidad'))
        .order_by('-total'))

    por_trabajador = list(ProduccionRegistro.objects
        .filter(timestamp__date__gte=inicio, trabajador__isnull=False)
        .values('trabajador__nombre', 'trabajador__apellidos')
        .annotate(total=Sum('cantidad'))
        .order_by('-total')[:10])
    for item in por_trabajador:
        apellidos = (item.get('trabajador__apellidos') or '').strip()
        nombre = (item.get('trabajador__nombre') or '').strip()
        item['nombre_completo'] = f"{nombre} {apellidos}".strip()

    por_hora_qs = (ProduccionRegistro.objects
        .filter(timestamp__date__gte=inicio)
        .annotate(hora=ExtractHour('timestamp'))
        .values('hora')
        .annotate(total=Sum('cantidad'))
        .order_by('hora'))
    hora_dict = {d['hora']: d['total'] for d in por_hora_qs}
    por_hora = []
    for h in range(24):
        por_hora.append({
            'hora': f"{h:02d}:00",
            'total': hora_dict.get(h, 0),
        })

    referencias = Referencia.objects.filter(activo=True)
    stock_vs_prod = []
    for ref in referencias:
        stock = stock_actual_por_referencia(ref)
        producido = (ProduccionRegistro.objects
            .filter(referencia=ref, timestamp__date__gte=inicio)
            .aggregate(t=Sum('cantidad'))['t'] or 0)
        if stock > 0 or producido > 0:
            stock_vs_prod.append({
                'codigo': ref.codigo,
                'nombre': ref.nombre,
                'tipo': ref.get_tipo_display(),
                'stock': stock,
                'producido': producido,
            })
    stock_vs_prod.sort(key=lambda x: x['producido'] + x['stock'], reverse=True)

    return JsonResponse({
        'diario': diario,
        'por_referencia': por_referencia,
        'por_estacion': por_estacion,
        'por_trabajador': por_trabajador,
        'por_hora': por_hora,
        'stock_vs_prod': stock_vs_prod,
    })


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
