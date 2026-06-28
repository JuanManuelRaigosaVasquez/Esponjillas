from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Trabajador
from core.decorators import staff_required


@staff_required
def lista_view(request):
    trabajadores = Trabajador.objects.all()
    activos = trabajadores.filter(activo=True).count()
    inactivos = trabajadores.filter(activo=False).count()
    context = {
        'trabajadores': trabajadores,
        'activos': activos,
        'inactivos': inactivos,
    }
    return render(request, 'trabajadores/lista.html', context)


@staff_required
def crear_view(request):
    if request.method == 'POST':
        trabajador = Trabajador(
            nombre=request.POST.get('nombre', '').strip(),
            apellidos=request.POST.get('apellidos', '').strip(),
            cedula=request.POST.get('cedula', '').strip() or None,
            telefono=request.POST.get('telefono', '').strip(),
            activo=request.POST.get('activo') == 'on',
        )
        trabajador.save()
        messages.success(request, f'Trabajador {trabajador.nombre_completo} creado exitosamente')
        return redirect('trabajadores:lista')

    context = {'editar': False}
    return render(request, 'trabajadores/form.html', context)


@staff_required
def editar_view(request, pk):
    trabajador = get_object_or_404(Trabajador, id=pk)

    if request.method == 'POST':
        trabajador.nombre = request.POST.get('nombre', '').strip()
        trabajador.apellidos = request.POST.get('apellidos', '').strip()
        trabajador.cedula = request.POST.get('cedula', '').strip() or None
        trabajador.telefono = request.POST.get('telefono', '').strip()
        trabajador.activo = request.POST.get('activo') == 'on'
        trabajador.save()
        messages.success(request, f'Trabajador {trabajador.nombre_completo} actualizado')
        return redirect('trabajadores:lista')

    context = {'trabajador': trabajador, 'editar': True}
    return render(request, 'trabajadores/form.html', context)


@staff_required
def eliminar_view(request, pk):
    trabajador = get_object_or_404(Trabajador, id=pk)

    if request.method == 'POST':
        nombre = trabajador.nombre_completo
        trabajador.delete()
        messages.success(request, f'Trabajador {nombre} eliminado')
        return redirect('trabajadores:lista')

    context = {'trabajador': trabajador}
    return render(request, 'trabajadores/confirmar_eliminar.html', context)
