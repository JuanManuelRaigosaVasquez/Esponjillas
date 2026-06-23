# Lumina ERP - Manufactura Oro/Plata

ERP para linea de produccion de productos sellados con trazabilidad, inventario, tercerizacion y costos.

---

## Requisitos previos

Asegurate de tener instalado en tu maquina:

- **Python 3.10** o superior
- **Git**
- **pip** (viene con Python)

Verifica tu version:

```bash
python3 --version
git --version
```

---

## Paso a paso para levantar el proyecto

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd esponjas
```

### 2. Crear el entorno virtual

```bash
python3 -m venv venv
```

### 3. Activar el entorno virtual

En **Linux / macOS**:

```bash
source venv/bin/activate
```

En **Windows** (PowerShell):

```bash
venv\Scripts\Activate.ps1
```

En **Windows** (CMD):

```bash
venv\Scripts\activate.bat
```

> **Importante**: siempre activa el entorno virtual antes de trabajar en el proyecto. Sabes que esta activo cuando ves `(venv)` al inicio de la terminal.

### 4. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 5. Configurar variables de entorno

```bash
cp .env.example .env
```

Esto crea el archivo `.env` con las variables de configuracion. El archivo `.env.example` contiene valores de ejemplo para desarrollo local. Para produccion, edita `.env` y cambia las claves.

### 6. Ejecutar las migraciones

```bash
python manage.py migrate
```

Esto crea la base de datos SQLite (`db.sqlite3`) con todas las tablas necesarias.

### 7. Poblar la base de datos con datos de prueba

```bash
python seed_data.py
```

Este script crea usuarios, referencias, estaciones, registros de produccion, inventario y ordenes de ejemplo. **Puedes ejecutarlo varias veces sin problema** (no duplica datos).

### 8. Iniciar el servidor de desarrollo

```bash
python manage.py runserver
```

El servidor arranca en `http://127.0.0.1:8000/` por defecto. Al abrir esa URL seras redirigido a la pagina de login.

---

## Credenciales de prueba

| Usuario | Contrasena | Rol |
|----------|-------------|------|
| `admin` | `admin123` | Superusuario (acceso al panel admin) |
| `juan` | `operario123` | Operario (sellado) |
| `maria` | `operario123` | Operaria (flopa) |
| `carlos` | `operario123` | Operario (empaque) |
| `laura` | `supervisor123` | Supervisora (staff, sin acceso admin) |

---

## URLs del sistema

| Ruta | Descripcion |
|------|-------------|
| `/` | Redirige automaticamente a produccion operator |
| `/login/` | Inicio de sesion |
| `/logout/` | Cerrar sesion |
| `/produccion/operator/` | Interfaz tactil para registrar produccion |
| `/produccion/dashboard/` | Dashboard de supervision con KPIs y graficos |
| `/inventario/` | Stock actual por referencia y movimientos |
| `/inventario/materia-prima/` | Registro y saldo de materia prima |
| `/tercerizacion/` | Listado de ordenes de tercerizacion |
| `/tercerizacion/crear/` | Crear nueva orden de tercerizacion |
| `/costos/` | Reporte y calculo de costos diarios |
| `/admin/` | Panel de administracion de Django |

---

## Modulos

### 1. Produccion en Tiempo Real

- **URL**: `/produccion/operator/`
- Interfaz tactil para tablet con botones grandes
- Registro de unidades con un solo toque
- Seleccion de estacion (Sellado, Flopa, Troquel, Empaque)
- Historial de registros del dia en tiempo real
- Impresion de sticker por cada costal completado

### 2. Dashboard Supervisor

- **URL**: `/produccion/dashboard/`
- KPIs diarios: total producido, referencias activas, stock critico
- Graficos de produccion por estacion y por referencia
- Tabla de stock actual con estados OK / Bajo / Critico
- Feed de ultimos movimientos de inventario

### 3. Inventario en Proceso

- **URL**: `/inventario/`
- Stock actual por referencia (suma/resta automaticos desde produccion)
- Logica: estacion suma (+), estacion resta (-), empaque sin movimiento
- Historial de movimientos con trazabilidad

### 4. Materia Prima

- **URL**: `/inventario/materia-prima/`
- Registro de espuma (kg), rollos (unidades) y tela (kg)
- Saldos actualizados en tiempo real
- Entrada manual de compras / lotes

### 5. Ordenes de Tercerizacion

- **URL**: `/tercerizacion/`
- Documento con consecutivo autogenerado (OT-00001)
- Registro: cantidad salida, retorno esperado (en pacas)
- Cierre de orden con comparacion esperado vs real
- Estado: abierta / cerrada con diferencia calculada

### 6. Costos Diarios

- **URL**: `/costos/`
- Calculo: (horas x tarifa) + (unidades x costo MP) + merma%
- Filtro por fecha
- Boton "Calcular Costos del Dia" (API)
- Resumen: Mano de obra, MP, Merma, Costo total

---

## Reglas de negocio

- **Suma automatica**: Sellado y Flopa suman al inventario
- **Resta automatica**: Troquel resta del inventario
- **Sin movimiento**: Empaque solo reporta tiempo y cantidad
- **No se puede cerrar orden sin registro de retorno**
- **No se permite produccion sin referencia / estacion valida**

---

## Impresion de Stickers

Al completar un costal, toca el icono de impresora en los ultimos registros.
Se abre una pantalla con formato de sticker listo para impresora termica.

La libreria `python-escpos` esta incluida para integracion directa con impresoras
termicas USB/red. Configura la impresora en `produccion/views.py:imprimir_sticker`.

---

## Stack

- **Django 5.x** + SQLite
- **Tailwind CSS** (CDN) con paleta ambar/dorado
- **Material Symbols** para iconos
- **Vanilla JavaScript** para interactividad tactil
- **python-escpos** para impresion termica
- **python-dotenv** para variables de entorno
