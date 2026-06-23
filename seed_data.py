#!/usr/bin/env python
"""
Script para poblar la base de datos con datos de ejemplo.
Ejecutar: python seed_data.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone
from produccion.models import Referencia, Estacion, ProduccionRegistro
from inventario.models import MovimientoInventario, MateriaPrima, ConsumoEstandar
from tercerizacion.models import OrdenTercerizacion
from costos.models import TarifaOperario, CostoProduccion

print("Creando usuarios...")

admin, created = User.objects.get_or_create(username='admin')
if created:
    admin.set_password('admin123')
    admin.email = 'admin@esponjas.com'
    admin.is_superuser = True
    admin.is_staff = True
    admin.first_name = 'Admin'
    admin.last_name = 'Sistema'
    admin.save()
    print("  admin creado")
else:
    print("  admin ya existe")

juan, created = User.objects.get_or_create(username='juan')
if created:
    juan.set_password('operario123')
    juan.first_name = 'Juan'
    juan.last_name = 'Operario'
    juan.save()
    print("  juan creado")
else:
    print("  juan ya existe")

maria, created = User.objects.get_or_create(username='maria')
if created:
    maria.set_password('operario123')
    maria.first_name = 'Maria'
    maria.last_name = 'Flopa'
    maria.save()
    print("  maria creada")
else:
    print("  maria ya existe")

carlos, created = User.objects.get_or_create(username='carlos')
if created:
    carlos.set_password('operario123')
    carlos.first_name = 'Carlos'
    carlos.last_name = 'Empaque'
    carlos.save()
    print("  carlos creado")
else:
    print("  carlos ya existe")

laura, created = User.objects.get_or_create(username='laura')
if created:
    laura.set_password('supervisor123')
    laura.first_name = 'Laura'
    laura.last_name = 'Supervisora'
    laura.is_staff = True
    laura.save()
    print("  laura creada")
else:
    print("  laura ya existe")

print("Creando tarifas de operarios...")
TarifaOperario.objects.get_or_create(
    operario=juan, defaults={'tarifa_hora': 5800}
)
TarifaOperario.objects.get_or_create(
    operario=maria, defaults={'tarifa_hora': 5800}
)
TarifaOperario.objects.get_or_create(
    operario=carlos, defaults={'tarifa_hora': 5500}
)

print("Creando estaciones...")
estaciones = []
for nombre, tipo_mov, orden in [
    ('Sellado', 'suma', 1),
    ('Flopa', 'suma', 2),
    ('Troquel', 'resta', 3),
    ('Empaque', 'ninguno', 4),
]:
    est, _ = Estacion.objects.get_or_create(
        nombre=nombre,
        defaults={'tipo_movimiento': tipo_mov, 'orden': orden}
    )
    estaciones.append(est)

print("Creando referencias...")
refs_data = [
    {
        'codigo': 'AN-ORO-001', 'nombre': 'Anillo Oro', 'tipo': 'oro',
        'merma_pct': 2.5, 'consumo_espuma_kg': 0.015, 'consumo_tela_m': 0.05,
        'costo_mp_estandar': 12000
    },
    {
        'codigo': 'CD-ORO-002', 'nombre': 'Cadena Oro', 'tipo': 'oro',
        'merma_pct': 3.0, 'consumo_espuma_kg': 0.020, 'consumo_tela_m': 0.08,
        'costo_mp_estandar': 25000
    },
    {
        'codigo': 'AN-PL-001', 'nombre': 'Anillo Plata', 'tipo': 'plata',
        'merma_pct': 2.0, 'consumo_espuma_kg': 0.012, 'consumo_tela_m': 0.04,
        'costo_mp_estandar': 5000
    },
    {
        'codigo': 'CD-PL-002', 'nombre': 'Cadena Plata', 'tipo': 'plata',
        'merma_pct': 2.5, 'consumo_espuma_kg': 0.018, 'consumo_tela_m': 0.07,
        'costo_mp_estandar': 8000
    },
]

referencias = []
for data in refs_data:
    ref, _ = Referencia.objects.get_or_create(
        codigo=data['codigo'],
        defaults={k: v for k, v in data.items() if k != 'codigo'}
    )
    referencias.append(ref)

for ref in referencias:
    ConsumoEstandar.objects.get_or_create(
        referencia=ref,
        defaults={
            'espuma_kg_por_unidad': ref.consumo_espuma_kg,
            'tela_m_por_unidad': ref.consumo_tela_m,
        }
    )

sellado = estaciones[0]
flopa = estaciones[1]
empaque = estaciones[3]

# Solo crear datos de produccion si no hay registros previos
if ProduccionRegistro.objects.count() == 0:
    print("Creando produccion de ejemplo...")

    hora = timezone.now().replace(hour=8, minute=0, second=0)

    for i in range(20):
        reg = ProduccionRegistro.objects.create(
            operario=juan,
            referencia=referencias[0],
            estacion=sellado,
            cantidad=1,
            timestamp=hora
        )
        MovimientoInventario.objects.create(
            tipo='entrada', referencia=referencias[0], estacion=sellado,
            cantidad=1, produccion=reg, origen=f'Sellado Anillo Oro #{reg.id}'
        )
        hora = hora + timedelta(minutes=3)

    for i in range(15):
        reg = ProduccionRegistro.objects.create(
            operario=juan,
            referencia=referencias[2],
            estacion=sellado,
            cantidad=1,
            timestamp=hora
        )
        MovimientoInventario.objects.create(
            tipo='entrada', referencia=referencias[2], estacion=sellado,
            cantidad=1, produccion=reg, origen=f'Sellado Anillo Plata #{reg.id}'
        )
        hora = hora + timedelta(minutes=3)

    for i in range(10):
        reg = ProduccionRegistro.objects.create(
            operario=maria,
            referencia=referencias[1],
            estacion=flopa,
            cantidad=1,
            timestamp=hora
        )
        MovimientoInventario.objects.create(
            tipo='entrada', referencia=referencias[1], estacion=flopa,
            cantidad=1, produccion=reg, origen=f'Flopa Cadena Oro #{reg.id}'
        )
        hora = hora + timedelta(minutes=4)

    for i in range(8):
        ProduccionRegistro.objects.create(
            operario=carlos,
            referencia=referencias[2],
            estacion=empaque,
            cantidad=1,
            timestamp=hora
        )
        hora = hora + timedelta(minutes=5)
else:
    print(f"  Ya existen {ProduccionRegistro.objects.count()} registros de produccion, saltando...")

# Solo crear materia prima si no hay registros previos
if MateriaPrima.objects.count() == 0:
    print("Creando materia prima de ejemplo...")
    MateriaPrima.objects.create(tipo='espuma', cantidad_kg=50.0, cantidad_unidades=0, registrado_por=juan, descripcion='Compra inicial espuma')
    MateriaPrima.objects.create(tipo='rollo', cantidad_kg=0, cantidad_unidades=200, registrado_por=juan, descripcion='Compra rollos proveedor A')
    MateriaPrima.objects.create(tipo='tela', cantidad_kg=30.0, cantidad_unidades=0, registrado_por=maria, descripcion='Tela microfibra lote 8821')
else:
    print(f"  Ya existen {MateriaPrima.objects.count()} registros de materia prima, saltando...")

# Solo crear ordenes si no hay registros previos
if OrdenTercerizacion.objects.count() == 0:
    print("Creando orden de tercerizacion de ejemplo...")
    orden = OrdenTercerizacion(
        referencia=referencias[0],
        cantidad_salida=100,
        cantidad_esperada=100,
        observaciones='Tercerizacion anillos oro para acabado especial'
    )
    orden.save()

    orden2 = OrdenTercerizacion(
        referencia=referencias[1],
        cantidad_salida=50,
        cantidad_esperada=50,
        observaciones='Cadenas oro para baño adicional'
    )
    orden2.save()
    orden2.cerrar(48)
else:
    print(f"  Ya existen {OrdenTercerizacion.objects.count()} ordenes de tercerizacion, saltando...")

print("\nDatos de ejemplo creados exitosamente!")
print("=" * 50)
print("Usuarios:")
print("  admin / admin123 (superusuario)")
print("  juan / operario123 (sellado)")
print("  maria / operario123 (flopa)")
print("  carlos / operario123 (empaque)")
print("  laura / supervisor123 (supervisora)")
print(f"\nReferencias: {Referencia.objects.count()}")
print(f"Estaciones: {Estacion.objects.count()}")
print(f"Producciones: {ProduccionRegistro.objects.count()}")
print(f"Movimientos: {MovimientoInventario.objects.count()}")
print(f"Ordenes: {OrdenTercerizacion.objects.count()}")
print("=" * 50)
