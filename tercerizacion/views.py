from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from produccion.models import Referencia
from .models import OrdenTercerizacion
from core.decorators import staff_required


@staff_required
def lista_view(request):
    ordenes = OrdenTercerizacion.objects.select_related('referencia').order_by('-fecha_salida')
    abiertas = ordenes.filter(estado='abierta').count()
    cerradas = ordenes.filter(estado='cerrada').count()

    context = {
        'ordenes': ordenes,
        'abiertas': abiertas,
        'cerradas': cerradas,
    }
    return render(request, 'tercerizacion/lista.html', context)


@staff_required
def crear_view(request):
    referencias = Referencia.objects.filter(activo=True)

    if request.method == 'POST':
        orden = OrdenTercerizacion(
            referencia_id=int(request.POST.get('referencia')),
            cantidad_salida=int(request.POST.get('cantidad_salida')),
            cantidad_esperada=int(request.POST.get('cantidad_esperada')),
            observaciones=request.POST.get('observaciones', ''),
            fecha_salida=timezone.now(),
        )
        orden.save()
        messages.success(request, f'Orden {orden.consecutivo} creada exitosamente')
        return redirect('tercerizacion:detalle', pk=orden.id)

    context = {'referencias': referencias}
    return render(request, 'tercerizacion/form.html', context)


@staff_required
def detalle_view(request, pk):
    orden = get_object_or_404(OrdenTercerizacion.objects.select_related('referencia'), id=pk)
    diferencia = orden.diferencia()
    context = {
        'orden': orden,
        'diferencia': diferencia,
    }
    return render(request, 'tercerizacion/detalle.html', context)


@staff_required
def cerrar_view(request, pk):
    orden = get_object_or_404(OrdenTercerizacion, id=pk)

    if request.method == 'POST':
        try:
            cantidad_retorno = int(request.POST.get('cantidad_retorno'))
            orden.cerrar(cantidad_retorno)
            messages.success(request, f'Orden {orden.consecutivo} cerrada. Diferencia: {orden.diferencia()} unidades')
            return redirect('tercerizacion:detalle', pk=orden.id)
        except ValueError as e:
            messages.error(request, str(e))

    return redirect('tercerizacion:detalle', pk=orden.id)
