# Hoja de Ruta — Lumina ERP (Sistema Coquito)

Sistema de registro de produccion en tablet con trazabilidad por costal, inventario
en proceso, merma, tercerizacion y costos. Adaptado al ERP Lumina ya existente.

## Como usar este documento

- [ ] **Tarea pendiente** — falta implementar (etiqueta `FALTA`) o completar (`PARCIAL`)
- [x] **Tarea lista** — implementada y funcionando en el sistema
- Cuando termines una tarea, cambia `[ ]` por `[x]` y (opcional) agrega la fecha

**Leyenda:**
- `LISTO` — existe y funciona
- `PARCIAL` — existe algo, ver la nota de que falta
- `FALTA` — no existe nada todavia

## Estado actual del sistema

ERP Lumina: Django 5.x + Tailwind CSS + Material Symbols. Modelos existentes:
`ProduccionRegistro`, `Referencia`, `Estacion`, `Trabajador`, `MovimientoInventario`,
`MateriaPrima`, `ConsumoEstandar`, `CostoProduccion`, `TarifaOperario`,
`OrdenTercerizacion`. Vistas: `registro_rapido` (kiosco tablet), `operator`,
`dashboard`, `analiticas` (6 graficos Chart.js), inventario/stock, costos/reporte,
trabajadores, tercerizacion. Corre en navegador, sin installs (M10/A3 ya cumplidos).

---

## Modulo M — Registro en Tablet (Interfaz Coquito)

- [x] **M10** — Sistema en la nube, sin peso en la tablet `LISTO`
  App web Django corre en navegador; solo necesita WiFi.

- [ ] **M1** — Seleccion de usuario por foto o numero `PARCIAL`
  `registro_rapido` ya muestra botones por trabajador con avatar (iniciales) y
  entra sin contrasena. FALTA:
  - [ ] Campo `numero` (u `orden`) en modelo `Trabajador` para mostrar visible
  - [ ] Campo `foto` (ImageField) para reemplazar avatar de iniciales por foto
  - [ ] Mostrar el numero junto a la foto en el kiosco

- [ ] **M2** — Seleccion de referencia por imagen (estilo coquito) `PARCIAL`
  `registro_rapido` ya muestra imagenes SVG de esponjas + nombre + codigo, un toque
  registra. FALTA:
  - [ ] Campo `imagen` en `Referencia` (actualmente usa SVGs fijos por codigo)
  - [ ] Panel para subir foto de cada referencia (ver A2)

- [ ] **M3** — Registro de costal terminado con un toque `PARCIAL`
  `registro_rapido` registra con un toque (`registrarProduccion`), pero por unidad
  suelta (cantidad=1). FALTA:
  - [ ] Concepto de "costal" (lote/batch) con un boton "Termine costal"
  - [ ] Que un toque registre el costal completo (no 600 toques)
  - [ ] Mantener acumulado del costal en curso (ver M4, T1)

- [ ] **M4** — Conversion automatica de unidades `PARCIAL`
  `Referencia` ya tiene `consumo_espuma_kg` y `consumo_tela_m`, pero no conversion
  de costales/rollos/pares a unidades individuales. FALTA:
  - [ ] Campo `unidades_por_costal` (ej. 600) en `Referencia`
  - [ ] Logica: operario registra 1 costal -> sistema suma 600 unidades internamente
  - [ ] Permitir diferentes unidades por referencia (costal, rollo, par)

- [ ] **M5** — Registro de unidad defectuosa con un toque `FALTA`
  No existe boton "Unidad mala" en el kiosco. FALTA:
  - [ ] Boton secundario "Unidad mala" visible en `registro_rapido`
  - [ ] Modelo o campo para registrar merma por costal y por operario
  - [ ] Acumular sin interrumpir el flujo (ver C1, C2)

- [ ] **M6** — Confirmacion visual inmediata `PARCIAL`
  `registro_rapido` tiene animacion `pulse` al tocar. FALTA:
  - [ ] Confirmacion grande y clara (palomita verde) durante 2 segundos
  - [ ] Mostrar numero actualizado del contador del dia

- [ ] **M7** — Contador visible del dia con semaforo `FALTA`
  No hay contador ni meta visible en el kiosco. FALTA:
  - [ ] Contador "costales hoy / meta del dia" siempre visible en tablet
  - [ ] Semaforo verde/amarillo/rojo segun avance vs meta
  - [ ] Configuracion de meta por estacion y referencia (ver N1)

- [ ] **M8** — Una tablet por zona, no una por operario `PARCIAL`
  `registro_rapido` es un kiosco compartido por estacion; varios operarios se
  turnan. FALTA:
  - [ ] Tras registrar, volver a la pantalla de seleccion de usuario (hoy se
        queda en product-section; `deseleccionarTrabajador` existe pero no se
        llama automaticamente)
  - [ ] Confirmar que el flujo kiosco -> usuario -> producto -> kiosco sea ciclico

- [ ] **M9** — Cierre de sesion automatico por inactividad `FALTA`
  No hay timeout. FALTA:
  - [ ] Timer JS en `registro_rapido` que tras X minutos sin toque vuelva a la
        pantalla de seleccion de usuario
  - [ ] Parametro configurable de minutos (ver N3)

---

## Modulo T — Trazabilidad

- [x] **T6** — Trazabilidad de la fecha en todo momento `LISTO`
  `ProduccionRegistro.timestamp` (DateTimeField) guarda fecha/hora exacta.

- [ ] **T1** — ID unico por costal desde su creacion `FALTA`
  No existe modelo "Costal" (lote). FALTA:
  - [ ] Modelo `Costal` con ID unico, FK a operario/trabajador, referencia,
        estacion origen, timestamp creacion, estado (en proceso/terminado)
  - [ ] Al tocar "Termine costal" asignar ID y hacerlo viajar por todo el flujo
  - [ ] Registrar quien lo hizo, cuando, que referencia es

- [ ] **T2** — Traspaso entre estaciones desde la tablet `PARCIAL`
  `MovimientoInventario` ya mueve saldos entre referencias/estaciones. FALTA:
  - [ ] Vista en tablet de "costales pendientes" para que el receptor seleccione
  - [ ] Descarga de bodega origen y suma a bodega destino (ver I1)
  - [ ] Logica: el que entrega suma, el que recoge para troquelar resta

- [ ] **T3** — Historial completo por costal `FALTA`
  No hay historial por costal. FALTA:
  - [ ] Dado un ID de costal, mostrar estaciones por las que paso, hora, operario
        en cada etapa y tiempo en cada proceso
  - [ ] Vista de detalle de costal (ver T1)

- [ ] **T4** — FIFO: primero en entrar, primero en salir `FALTA`
  No hay ordenamiento FIFO de pendientes. FALTA:
  - [ ] Lista de costales pendientes ordenada del mas antiguo al mas nuevo
  - [ ] Garantizar que siempre se procese primero lo que lleva mas tiempo esperando

- [ ] **T5** — Alerta de costal detenido `FALTA`
  No hay alertas. FALTA:
  - [ ] Si un costal lleva > N horas sin movimiento, generar alerta al supervisor
  - [ ] Umbral configurable por proceso (ver S3)

---

## Modulo I — Inventario en Proceso

- [ ] **I1** — Bodegas virtuales por etapa `PARCIAL`
  `Estacion.tipo_movimiento` (suma/resta/ninguno) ya mueve saldos. FALTA:
  - [ ] Formalizar bodegas: Materia prima - En proceso pegado - En proceso
        troquelado - Producto terminado - En calle
  - [ ] Cada registro en tablet mueve el saldo entre bodegas automaticamente
  - [ ] Vista de saldo por bodega (ver I6)

- [ ] **I2** — Inventario de espuma por rollos `PARCIAL`
  `MateriaPrima` existe para registrar entradas. FALTA:
  - [ ] ID por rollo (individual, trazable)
  - [ ] Entrada de rollos registrada desde la tablet al recibirlos
  - [ ] Descuento automatico segun produccion del horno registrada

- [ ] **I3** — Estimacion de consumo de tela `PARCIAL`
  `Referencia.consumo_tela_m` y `ConsumoEstandar.tela_m_por_unidad` existen. FALTA:
  - [ ] Calcular consumo estimado = unidades producidas x consumo estandar
  - [ ] Alerta de reabastecimiento para compras en China
  - [ ] Reporte de consumo estimado vs real (ver C3, P3)

- [ ] **I4** — Inventario inicial cargable `FALTA`
  No hay carga de inventario inicial. FALTA:
  - [ ] Formulario para cargar conteo fisico inicial al arrancar el sistema
  - [ ] Inventario fisico semestral: cargar conteo real y calcular diferencia
        acumulada (medir cumplimiento del proveedor)

- [ ] **I5** — Alertas de stock minimo `FALTA`
  No hay nivel minimo configurado. FALTA:
  - [ ] Campo `stock_minimo` en `Referencia` y en materia prima
  - [ ] Alerta automatica cuando el saldo baja del minimo
  - [ ] Panel de configuracion de minimos (ver N2)

- [ ] **I6** — Consulta de saldo en tiempo real `PARCIAL`
  El dashboard ya muestra `stock_data` por referencia y existe la pagina
  `/inventario/stock`. FALTA:
  - [ ] Vista de saldo por bodega virtual en tiempo real (ver I1)
  - [ ] Refrescar sin recargar la pagina (AJAX/polling) para el supervisor

---

## Modulo C — Calidad y Merma

- [ ] **C1** — Registro de defectuosas por toque `FALTA`
  Igual que M5. FALTA:
  - [ ] Boton "Unidad mala" en `registro_rapido`
  - [ ] Acumular total por costal y por operario sin anotar en papel

- [ ] **C2** — Rendimiento real vs esperado por costal `PARCIAL`
  `Referencia.merma_pct` existe (default 3.0). FALTA:
  - [ ] Comparar unidades buenas del costal vs estandar (600-630 u)
  - [ ] Mostrar % de merma asociado al costal y al operario que lo proceso

- [ ] **C3** — Reporte diario de merma por operario y por bolsa `FALTA`
  No hay reporte de merma. FALTA:
  - [ ] Reporte automatico al cierre del dia con unidades defectuosas
  - [ ] % de merma y comparativo historico por operario y por bolsa
  - [ ] (Sustituye lo que hoy hace Mafer en Excel)

- [ ] **C4** — Costo de la merma incluido en el costo de produccion `PARCIAL`
  `CostoProduccion.merma` y `Referencia.merma_pct` existen. FALTA:
  - [ ] Descontar unidades malas del rendimiento
  - [ ] Incluir la merma en el calculo del costo real del dia (ver P3)

---

## Modulo E — Tercerizacion

- [ ] **E1** — Generacion de orden de tercerizacion desde tablet `PARCIAL`
  `OrdenTercerizacion` ya tiene `consecutivo`, `referencia`, `cantidad_salida`,
  `cantidad_esperada`. FALTA:
  - [ ] Interfaz desde tablet para que el jefe de logistica genere la orden
  - [ ] Calculo automatico de cantidad esperada de retorno (ej. 40 -> 34 pacas)

- [ ] **E2** — Bodega virtual "En calle" `PARCIAL`
  `OrdenTercerizacion` existe con estado abierto/cerrado. FALTA:
  - [ ] Formalizar como bodega virtual "En calle"
  - [ ] Consulta: que hay en calle, a que tercero, hace cuantos dias, contra que orden

- [ ] **E3** — Cierre de orden al registrar retorno `PARCIAL`
  `OrdenTercerizacion` tiene `cantidad_retorno` y `estado`. FALTA:
  - [ ] Registrar retorno real desde la tablet
  - [ ] Cerrar orden, calcular diferencia vs esperada, actualizar inventario

- [ ] **E4** — Alerta de ordenes abiertas vencidas `FALTA`
  No hay alertas. FALTA:
  - [ ] Si una orden supera N dias sin cierre, alerta automatica al jefe de logistica
  - [ ] Umbral configurable (ver S3)

- [ ] **E5** — Documento de orden imprimible `FALTA`
  No existe plantilla de orden. FALTA:
  - [ ] Plantilla imprimible (PDF) con consecutivo, cantidad enviada, esperada, tercero
  - [ ] Boton de impresion (existe el patron `sticker_print.html` como referencia)

---

## Modulo P — Tiempos y Costos

- [ ] **P1** — Tiempo por costal calculado automaticamente `FALTA`
  No hay captura de inicio/fin de costal. FALTA:
  - [ ] Timestamp de inicio (al seleccionar referencia) y fin (al tocar "Termine")
  - [ ] Calcular duracion exacta por costal sin anotaciones manuales (ver T1, M3)

- [ ] **P2** — Comparativo tiempo real vs estandar por operario `PARCIAL`
  No hay tiempo estandar por referencia. FALTA:
  - [ ] Campo `tiempo_estandar` (minutos) en `Referencia` o `Estacion` (ver F3)
  - [ ] Comparativo tiempo real vs estandar en tiempo real por operario

- [ ] **P3** — Costo de produccion diario automatico `PARCIAL`
  `CostoProduccion` y `TarifaOperario` existen, hay reporte en `/costos/`. FALTA:
  - [ ] Automatizar el calculo diario sin boton manual (hoy hay "Calcular Costos")
  - [ ] Incluir ajuste por merma (ver C4)
  - [ ] Vista por operario y por linea

- [ ] **P4** — Visibilidad cada 2 horas, no al final del dia `PARCIAL`
  `dashboard` y `analiticas` muestran produccion acumulada. FALTA:
  - [ ] Vista intradia con corte cada 2 horas (cuanto se ha producido a esa hora)
  - [ ] Rendimiento en tiempo real (no esperar al cierre)

- [ ] **P5** — Historico de productividad por operario `PARCIAL`
  `analiticas` ya da serie diaria global y top trabajadores por periodo. FALTA:
  - [ ] Serie historica por operario individual (unidades, tiempos, merma)
  - [ ] Comparativo entre semanas, deteccion de tendencias

---

## Modulo F — Arranque por Fases

- [ ] **F1** — Fase 1: linea oro/plata (producto estrella — pareto) `PARCIAL`
  El sistema ya diferencia `Referencia.tipo` oro/plata. FALTA:
  - [ ] Ajustar parametros (cantidad estandar, tiempo estandar) de la linea oro/plata
  - [ ] Validar el modelo en planta antes de expandir

- [ ] **F2** — Replicable a otras lineas sin redisenar `PARCIAL`
  La estructura de `Referencia` es generica. FALTA:
  - [ ] Agregar una linea nueva = configurar parametros, no tocar codigo
  - [ ] Verificar que la conversion de unidades (M4) soporte multiples tipos

- [ ] **F3** — Parametrizacion de tiempos estandar `FALTA`
  No hay campo de tiempo estandar. FALTA:
  - [ ] Cargar los tiempos actuales de cada proceso como estandar
  - [ ] Panel para actualizarlos cuando cambie el proceso (ver N4)

---

## Modulo A — Administracion del Sistema

- [x] **A3** — Acceso web desde tablets y computadores `LISTO`
  App web; solo requiere WiFi. Falta coordinar cobertura WiFi con Camilo (infra).

- [ ] **A1** — Gestion de usuarios y roles `PARCIAL`
  Existe `User.is_staff` y `Trabajador.user` OneToOne. FALTA:
  - [ ] Roles formales: operario, supervisor, gerencia, administrador
  - [ ] Permisos por rol (operario solo ve su tablet, supervisor toda la planta,
        gerencia reportes/costos, administrador configura)
  - [ ] Panel de gestion de usuarios (ver R1)

- [ ] **A2** — Configuracion de referencias con imagen `PARCIAL`
  CRUD de `Referencia` y `Trabajador` existe. FALTA:
  - [ ] Subida de foto del producto (mismo icono que ve el operario en tablet)
  - [ ] Campos cantidad estandar por costal y tiempo estandar en el formulario
  - [ ] Sin tocar codigo (ver M2, M4, P2)

- [ ] **A4** — Dashboard en tiempo real para supervisor y gerencia `PARCIAL`
  `dashboard` y `analiticas` existen. FALTA:
  - [ ] Semaforo de cumplimiento (ver M7)
  - [ ] Inventario por bodega consolidado
  - [ ] Vista distinta por rol (supervisor vs gerencia)

- [ ] **A5** — Exportacion de reportes a Excel `FALTA`
  No hay exportacion. FALTA:
  - [ ] Cualquier reporte exportable a Excel (analiticas, costos, merma, stock)
  - [ ] Boton "Exportar" en cada reporte (ver X1)

- [ ] **A6** — Respaldo automatico en la nube `PARCIAL`
  El sistema ya corre en servidor. FALTA (infraestructura):
  - [ ] Respaldo automatico diario
  - [ ] Disponibilidad minima 99%
  - [ ] Si la tablet se dana no se pierde nada (ya se cumple: datos en servidor)

---

## Modulo N — Parametrizacion (NUEVO, sugerido para completar el sistema)

Reune toda la configuracion que requieren M7/I5/M9/P2/F3 para no dispersar reglas.

- [ ] **N1** — Meta diaria por estacion y referencia `FALTA`
  Para el semaforo de M7. FALTA:
  - [ ] Modelo `MetaDiaria` (estacion, referencia, fecha, cantidad_meta)
  - [ ] Valores por defecto por dia de la semana
  - [ ] Panel de configuracion

- [ ] **N2** — Stock minimo configurable por referencia y materia prima `FALTA`
  Para alertas de I5. FALTA:
  - [ ] Campo `stock_minimo` en `Referencia` y en `MateriaPrima`
  - [ ] Panel de configuracion de minimos

- [ ] **N3** — Timeout de inactividad del kiosco configurable `FALTA`
  Para M9. FALTA:
  - [ ] Parametro global `MINUTOS_INACTIVIDAD_KIOSCO`
  - [ ] Panel/ajustes para editarlo

- [ ] **N4** — Tiempo estandar por referencia y proceso configurable `FALTA`
  Para P2 y F3. FALTA:
  - [ ] Campo `tiempo_estandar_minutos` en `Referencia` (o por estacion)
  - [ ] Panel para editarlo sin tocar codigo

- [ ] **N5** — Unidades por costal configurable por referencia `FALTA`
  Para M4. FALTA:
  - [ ] Campo `unidades_por_costal` en `Referencia`
  - [ ] Soportar costal, rollo, par segun la referencia

---

## Modulo S — Alertas y Notificaciones (NUEVO, sugerido)

Muchos requisitos piden "alerta al supervisor" (T5, I5, E4). Centralizarlo evita
duplicar logica.

- [ ] **S1** — Centro de notificaciones unificado `FALTA`
  FALTA:
  - [ ] Modelo `Notificacion` (tipo, mensaje, severidad, fecha, leida, destinatario)
  - [ ] Campana/contador en el sidebar o topbar
  - [ ] Vista de lista de notificaciones

- [ ] **S2** — Alerta de stock minimo `FALTA`
  Source: I5. Alerta cuando saldo < minimo.

- [ ] **S3** — Alerta de costal detenido y orden vencida `FALTA`
  Source: T5 y E4. Umbral configurable por proceso/dias.

- [ ] **S4** — Alerta de avance por debajo de meta `FALTA`
  Source: M7. Alerta al supervisor cuando semaforo del kiosco este en rojo.

---

## Modulo R — Roles y Permisos (NUEVO, sugerido)

Desglose de A1 para hacerlo trackable.

- [ ] **R1** — Panel de gestion de usuarios `FALTA`
  Crear/editar usuarios, asignar rol, asociar a `Trabajador`.

- [ ] **R2** — Rol Operario (tablet) `PARCIAL`
  registro_rapido ya es sin login. FALTA:
  - [ ] Restringir que no vea dashboard/analiticas/costos

- [ ] **R3** — Rol Supervisor (toda la planta en tiempo real) `PARCIAL`
  `@staff_required` ya protege dashboard/analiticas. FALTA:
  - [ ] Definir el alcance exacto del rol supervisor

- [ ] **R4** — Rol Gerencia (reportes y costos) `FALTA`
  Acceso a reportes y costos, no a configuracion.

- [ ] **R5** — Rol Administrador (configura el sistema) `PARCIAL`
  Acceso al admin de Django ya existe. FALTA:
  - [ ] Paneles propios para configurar sin entrar al admin de Django

---

## Modulo K — Modelo Costal (NUEVO, sugerido)

Requisitos M3, M4, T1, T2, T3, P1 requieren un modelo "Costal" (lote).
Centralizarlo como modulo aparte facilita el seguimiento.

- [ ] **K1** — Modelo `Costal` `FALTA`
  ID unico, FK referencia, FK operario/trabajador, estacion origen, timestamp
  creacion, estado (en proceso / terminado / en transito / despachado).

- [ ] **K2** — Registro de cantidades (buenas y malas) por costal `FALTA`
  Unidades buenas (M3) y unidades defectuosas (M5/C1) asociadas al costal.

- [ ] **K3** — Traspaso de costal entre estaciones `FALTA`
  Registro de entrada/salida de un costal en cada estacion (T2/T3).

- [ ] **K4** — Calculo de tiempo por costal `FALTA`
  Duracion entre seleccion de referencia y "Termine costal" (P1).

- [ ] **K5** — Vista de detalle e historial por costal `FALTA`
  Estaciones por las que paso, horas, operarios, duracion (T3).

---

## Modulo X — Exportacion (NUEVO, sugerido)

Desglose de A5.

- [ ] **X1** — Exportar a Excel `.xlsx` `FALTA`
  Fuente: A5. FALTA:
  - [ ] Dependencia `openpyxl` en `requirements.txt`
  - [ ] Boton "Exportar" en analiticas, costos/merma, stock, productividad por operario

- [ ] **X2** — Exportar a PDF `FALTA`
  Para ordenes de tercerizacion (E5) y stickers. FALTA:
  - [ ] Generacion de PDF (WeasyPrint o reportlab) para la orden de tercerizacion

---

## Resumen de avance

| Modulo | Total | Listos | Parciales | Faltan |
|---|---|---|---|---|
| M — Registro Tablet | 10 | 1 | 6 | 3 |
| T — Trazabilidad | 6 | 1 | 1 | 4 |
| I — Inventario | 6 | 0 | 3 | 3 |
| C — Calidad/Merma | 4 | 0 | 2 | 2 |
| E — Tercerizacion | 5 | 0 | 3 | 2 |
| P — Tiempos/Costos | 5 | 0 | 4 | 1 |
| F — Arranque | 3 | 0 | 2 | 1 |
| A — Administracion | 6 | 1 | 3 | 2 |
| N — Parametrizacion (nuevo) | 5 | 0 | 0 | 5 |
| S — Alertas (nuevo) | 4 | 0 | 0 | 4 |
| R — Roles (nuevo) | 5 | 0 | 2 | 3 |
| K — Modelo Costal (nuevo) | 5 | 0 | 0 | 5 |
| X — Exportacion (nuevo) | 2 | 0 | 0 | 2 |
| **TOTAL** | **66** | **3** | **24** | **39** |

## Orden de implementacion sugerido

1. **K (Modelo Costal)** + **N4/N5 (tiempo y unidades estandar)** — base de todo
2. **M3/M4/M5/M6** — kiosco con boton "Termine costal", conversion y merma
3. **T1/T3/T4** — trazabilidad e historial del costal
4. **I1/I6** — bodegas virtuales y consulta de saldos
5. **N1/S1** — metas y centro de alertas
6. **M7/P2** — semaforo en kiosco y comparativo tiempo real
7. **C2/C3/C4** — merma y reportes
8. **E1/E3/E5** — tercerizacion desde tablet
9. **R1/R2/R3** — roles y permisos
10. **X1/X2** — exportacion
11. **M9** — timeout de inactividad
12. **F1** — arranque fase 1 en planta
