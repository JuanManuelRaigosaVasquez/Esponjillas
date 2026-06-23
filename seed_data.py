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
    maria.last_name = 'Horneado'
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
Estacion.objects.all().delete()
estaciones = []
for nombre, tipo_mov, orden in [
    ('Troquelado de espuma', 'suma', 1),
    ('Horneado', 'suma', 2),
    ('Corte', 'suma', 3),
    ('Pegado', 'suma', 4),
    ('Empaque', 'suma', 5),
]:
    est, _ = Estacion.objects.get_or_create(
        nombre=nombre,
        defaults={'tipo_movimiento': tipo_mov, 'orden': orden}
    )
    estaciones.append(est)

print("Creando referencias...")
refs_data = [
    {
        'codigo': 'ESP-BRI-001', 'nombre': 'Esponja de brillo', 'tipo': 'oro',
        'merma_pct': 2.5, 'consumo_espuma_kg': 0.015, 'consumo_tela_m': 0.05,
        'costo_mp_estandar': 1200
    },
    {
        'codigo': 'ESP-OP-002', 'nombre': 'Esponja oro plata', 'tipo': 'oro',
        'merma_pct': 3.0, 'consumo_espuma_kg': 0.020, 'consumo_tela_m': 0.08,
        'costo_mp_estandar': 1500
    },
    {
        'codigo': 'ESP-ORO-003', 'nombre': 'Esponja oro', 'tipo': 'oro',
        'merma_pct': 2.0, 'consumo_espuma_kg': 0.018, 'consumo_tela_m': 0.06,
        'costo_mp_estandar': 1300
    },
    {
        'codigo': 'ESP-DU-004', 'nombre': 'Esponja doble uso', 'tipo': 'plata',
        'merma_pct': 2.5, 'consumo_espuma_kg': 0.022, 'consumo_tela_m': 0.07,
        'costo_mp_estandar': 1800
    },
    {
        'codigo': 'ESP-SV-005', 'nombre': 'Esponja sabra verde', 'tipo': 'plata',
        'merma_pct': 2.0, 'consumo_espuma_kg': 0.016, 'consumo_tela_m': 0.05,
        'costo_mp_estandar': 1100
    },
]

Referencia.objects.all().delete()
ConsumoEstandar.objects.all().delete()
referencias = []
for data in refs_data:
    ref = Referencia.objects.create(**data)
    referencias.append(ref)

for ref in referencias:
    ConsumoEstandar.objects.create(
        referencia=ref,
        espuma_kg_por_unidad=ref.consumo_espuma_kg,
        tela_m_por_unidad=ref.consumo_tela_m,
    )

troquelado = estaciones[0]
horneado = estaciones[1]
corte = estaciones[2]
pegado = estaciones[3]
empaque = estaciones[4]

ProduccionRegistro.objects.all().delete()
MovimientoInventario.objects.all().delete()
print("Creando produccion diaria (~120 costales por estacion)...")

operarios = [juan, maria, carlos]
costales_por_estacion = 120
piezas_por_costal = 120

hora = timezone.now().replace(hour=6, minute=0, second=0, microsecond=0)

for estacion in estaciones:
    intervalo_min = 480 / costales_por_estacion
    for i in range(costales_por_estacion):
        operario = operarios[i % len(operarios)]
        referencia = referencias[i % len(referencias)]
        timestamp = hora + timedelta(minutes=intervalo_min * i)

        reg = ProduccionRegistro.objects.create(
            operario=operario,
            referencia=referencia,
            estacion=estacion,
            cantidad=piezas_por_costal,
            timestamp=timestamp,
        )
        MovimientoInventario.objects.create(
            tipo='entrada',
            referencia=referencia,
            estacion=estacion,
            cantidad=piezas_por_costal,
            produccion=reg,
            origen=f'{estacion.nombre} - {referencia.nombre} costal #{i+1}',
        )
    print(f"  {estacion.nombre}: {costales_por_estacion} costales creados")

MateriaPrima.objects.all().delete()
print("Creando materia prima de ejemplo...")
MateriaPrima.objects.create(tipo='espuma', cantidad_kg=5000.0, cantidad_unidades=0, registrado_por=juan, descripcion='Compra inicial espuma')
MateriaPrima.objects.create(tipo='rollo', cantidad_kg=0, cantidad_unidades=2000, registrado_por=juan, descripcion='Compra rollos proveedor A')
MateriaPrima.objects.create(tipo='tela', cantidad_kg=3000.0, cantidad_unidades=0, registrado_por=maria, descripcion='Tela microfibra lote 8821')

OrdenTercerizacion.objects.all().delete()
print("Creando orden de tercerizacion de ejemplo...")
orden = OrdenTercerizacion(
    referencia=referencias[0],
    cantidad_salida=1000,
    cantidad_esperada=1000,
    observaciones='Tercerizacion esponjas de brillo para acabado especial'
)
orden.save()

orden2 = OrdenTercerizacion(
    referencia=referencias[1],
    cantidad_salida=500,
    cantidad_esperada=500,
    observaciones='Esponjas oro plata para proceso adicional'
)
orden2.save()
orden2.cerrar(480)

print("\nDatos de ejemplo creados exitosamente!")
print("=" * 50)
print("Usuarios:")
print("  admin / admin123 (superusuario)")
print("  juan / operario123 (troquelado)")
print("  maria / operario123 (horneado)")
print("  carlos / operario123 (empaque)")
print("  laura / supervisor123 (supervisora)")
print(f"\nReferencias: {Referencia.objects.count()}")
print(f"Estaciones: {Estacion.objects.count()}")
print(f"Producciones: {ProduccionRegistro.objects.count()}")
print(f"Movimientos: {MovimientoInventario.objects.count()}")
print(f"Ordenes: {OrdenTercerizacion.objects.count()}")
print("=" * 50)
