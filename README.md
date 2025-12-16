# 📋 Sistema de Impresión PDF - Documentación HTML

Este proyecto es un **simulador de sistema de impresión PDF** que permite subir, gestionar y procesar archivos PDF a través de múltiples impresoras virtuales. A continuación se documenta cada página HTML disponible.

---

## 🏗️ Estructura del Proyecto

```
project/
├── main.py                 # Servidor FastAPI
├── models.py              # Modelos de datos (PrintJob)
├── printer_process.py     # Proceso de impresión en paralelo
├── queue_manager.py       # Gestor de colas (FIFO/Priority)
├── websocket_manager.py   # Gestor de WebSockets
├── job_registry.py        # Registro SQLite de trabajos
├── templates/
│   ├── index.html         # 📤 Subida de PDFs individual
│   ├── monitor.html       # 📡 Monitor en tiempo real
│   ├── batch_upload.html  # 📚 Carga por lotes
│   └── registry.html      # 📊 Consulta de registro
└── uploads/              # Carpeta de PDFs subidos
```

---

## 🌐 Páginas HTML Disponibles

### 1. **📤 Inicio - Subida Individual** (`/` → `index.html`)

**URL:** `http://localhost:8000/`

**Propósito:** Permite subir un archivo PDF individual con opción de asignar prioridad.

**Características principales:**
- ✅ Selección de archivo PDF
- ✅ Asignación de prioridad (1-10)
- ✅ Validación de archivos PDF
- ✅ Seguimiento en tiempo real de la impresión
- ✅ Barra de progreso visual
- ✅ Descarga del PDF impreso
- ✅ WebSocket para actualizaciones en vivo

**Flujo de trabajo:**
1. Usuario selecciona un archivo PDF
2. Asigna una prioridad (por defecto 1)
3. Hace clic en "Subir PDF"
4. Se genera un ID único de trabajo
5. Visualiza progreso en tiempo real
6. Una vez completado, puede descargar el PDF

**Funcionalidades técnicas:**
- Cálculo automático de número de páginas con PyPDF2
- Conexión WebSocket para actualizaciones en vivo
- Botón para descargar el PDF procesado
- Enlace a la página de registro para ver historial

---

### 2. **📡 Monitor del Sistema** (`/monitor` → `monitor.html`)

**URL:** `http://localhost:8000/monitor`

**Propósito:** Monitoreo en tiempo real del estado de todas las impresoras y la cola de trabajos.

**Características principales:**
- ✅ Estado en vivo de cada impresora
- ✅ Visualización de la cola de trabajos pendientes
- ✅ Indicador de actividad con colores
- ✅ Cambio dinámico de tipo de cola (FIFO ↔ Priority)
- ✅ WebSocket para actualizaciones instantáneas
- ✅ Contador de trabajos en cola
- ✅ Información detallada de cada trabajo en progreso

**Indicadores visualizados:**
- **Estado de Impresoras:**
  - 🟢 Verde: Impresora inactiva (idle)
  - 🟡 Amarillo: Impresora imprimiendo
  - 🔴 Rojo: Impresora con error

**Panel de Control:**
- Selector para cambiar tipo de cola
- Opción entre FIFO (First In First Out) y Priority (por prioridad)
- Cambio de tipo en tiempo real sin reiniciar

**Información de la Cola:**
- ID de trabajo
- Nombre del archivo
- Prioridad asignada
- Número de páginas
- Estado actual

**Funcionalidades técnicas:**
- WebSocket bidireccional (`/ws-monitor`)
- Actualización automática cada 500ms
- Interfaz responsiva con grid layout

---

### 3. **📚 Carga por Lotes** (`/batch` → `batch_upload.html`)

**URL:** `http://localhost:8000/batch`

**Propósito:** Permite subir múltiples archivos PDF simultáneamente con la misma prioridad.

**Características principales:**
- ✅ Selección múltiple de archivos
- ✅ Asignación de prioridad común a todos
- ✅ Vista previa de archivos a subir
- ✅ Progreso por archivo
- ✅ Resumen de carga
- ✅ Manejo de errores individual
- ✅ Descarga de resumen en JSON

**Proceso de carga por lotes:**
1. Usuario selecciona múltiples PDFs (Ctrl+Click o Cmd+Click)
2. Asigna prioridad común a todos
3. Visualiza lista de archivos a subir
4. Hace clic en "Subir Todo"
5. Barra de progreso por archivo
6. Resumen de resultados (éxitos/fallos)

**Información mostrada:**
- Nombre del archivo
- Tamaño del archivo
- Número de páginas (calculado)
- Estado de carga (procesando/completado/error)
- ID único generado para cada trabajo
- Resumen total: trabajos completados, fallidos, tiempo total

**Funcionalidades técnicas:**
- Carga paralela con Promise.all()
- Validación de cada archivo individualmente
- Gestión independiente de errores por archivo
- Exportación de resultados en JSON

---

### 4. **📊 Registro de Trabajos** (`/registry` → `registry.html`)

**URL:** `http://localhost:8000/registry`

**Propósito:** Consulta y análisis del historial completo de trabajos procesados almacenados en SQLite.

**Características principales:**
- ✅ Listado paginado de todos los trabajos
- ✅ Búsqueda por ID de trabajo
- ✅ Filtrado por impresora
- ✅ Estadísticas del sistema
- ✅ Tabla con detalles completos
- ✅ Copiar JSON a portapapeles
- ✅ Carga asíncrona con spinner

**Paneles disponibles:**

#### **Panel 1: Todos los Trabajos**
- Paginación configurable (por defecto 10 por página)
- Tabla con columnas:
  - ID Trabajo (primeros 8 caracteres)
  - Archivo
  - Impresora que lo procesó
  - Número de páginas
  - Hora de entrada (HH:MM)
  - Hora de salida (HH:MM)

#### **Panel 2: Búsqueda por ID**
- Búsqueda exacta de trabajo
- Información completa del trabajo:
  - ID del trabajo
  - Nombre del archivo
  - Impresora asignada
  - Número de páginas
  - Timestamp de llegada completo
  - Timestamp de salida completo
  - Ruta relativa del PDF
  - Fecha de registro en BD
  - Opción para copiar JSON

#### **Panel 3: Trabajos por Impresora**
- Selector dropdown de impresoras (0, 1, 2)
- Tabla con todos los trabajos procesados por esa impresora
- Información: ID, archivo, páginas, tiempos

#### **Panel 4: Estadísticas**
- Tarjetas de estadísticas:
  - **Total de Trabajos:** Número total de trabajos completados
  - **Total de Páginas:** Suma de todas las páginas impresas
- Tabla desglosada por impresora:
  - Impresora
  - Cantidad de trabajos procesados
  - Total de páginas impresas por impresora

**Almacenamiento de datos:**
- Base de datos: `job_registry.db` (SQLite)
- Tabla: `job_registry`
- Campos registrados:
  - `id` - ID autoincrementable
  - `job_id` - UUID único del trabajo
  - `filename` - Nombre original del archivo
  - `timestamp_arrival` - Cuándo llegó el trabajo
  - `printer_id` - ID de la impresora que lo procesó
  - `num_pages` - Número de páginas impresas
  - `exit_time` - Cuándo se completó
  - `pdf_path` - Ruta relativa del PDF guardado
  - `created_at` - Cuándo se registró en BD

**Funcionalidades técnicas:**
- Consultas asíncronas a SQLite
- Paginación en cliente y servidor
- Formateo de fechas local
- Manejo de errores con mensajes descriptivos

---

## 🔌 APIs REST Disponibles

### Endpoints de Carga

```
POST /upload
  Parámetros:
    - file (FormData): Archivo PDF a subir
    - priority (int): Prioridad del trabajo (1-10)
  Respuesta:
    {
      "job_id": "uuid",
      "total_pages": número
    }
```

### Endpoints de Configuración

```
GET /config/queue-type
  Respuesta: {"queue_type": "fifo" | "priority"}

POST /config/queue-type?queue_type=fifo
  Respuesta: {"message": "...", "queue_type": "..."}
```

### Endpoints de Registro

```
GET /registry/jobs?limit=10&offset=0
  Retorna lista paginada de todos los trabajos

GET /registry/job/{job_id}
  Retorna detalles de un trabajo específico

GET /registry/printer/{printer_id}
  Retorna todos los trabajos de una impresora

GET /registry/statistics
  Retorna estadísticas del sistema

DELETE /registry/job/{job_id}
  Elimina un trabajo del registro

POST /registry/clear
  Limpia todo el registro
```

### WebSocket Endpoints

```
WS /ws/{job_id}
  Conexión en vivo para seguimiento de trabajo individual

WS /ws-monitor
  Conexión para monitoreo del sistema completo
```

---

## 🎨 Diseño y Estilo

Todas las páginas comparten:
- **Color primario:** Morado/Azul (`#667eea` → `#764ba2`)
- **Diseño responsivo:** Compatible con desktop, tablet y móvil
- **Fuente:** Segoe UI, Tahoma, Geneva, Verdana
- **Animaciones:** Transiciones suaves y spinners de carga
- **Tabla responsive:** Overflow horizontal en dispositivos pequeños

---

## 🚀 Cómo Iniciar el Sistema

### 1. Instalar dependencias
```bash
pip install fastapi uvicorn PyPDF2 python-multiprocessing
```

### 2. Iniciar el servidor
```bash
python main.py
```

### 3. Acceder a las páginas

| Página | URL | Función |
|--------|-----|---------|
| Subida Individual | `http://localhost:8000/` | Subir 1 PDF con prioridad |
| Monitor | `http://localhost:8000/monitor` | Ver estado en tiempo real |
| Carga por Lotes | `http://localhost:8000/batch` | Subir múltiples PDFs |
| Registro | `http://localhost:8000/registry` | Consultar historial de trabajos |

---

## 💾 Archivos Generados

El sistema genera automáticamente:

- **Carpeta `uploads/`** - Almacena todos los PDFs subidos
- **Archivo `job_registry.db`** - Base de datos SQLite con historial (en .gitignore)
- **Carpeta `__pycache__/`** - Bytecode compilado de Python (en .gitignore)

---

## 🔄 Flujo de Datos Completo

```
Usuario sube PDF
    ↓
FastAPI recibe archivo
    ↓
Valida y calcula páginas (PyPDF2)
    ↓
Crea PrintJob con timestamp
    ↓
Agrega a cola (FIFO o Priority)
    ↓
Impresora disponible toma trabajo
    ↓
Simula impresión (10 seg por página)
    ↓
Registra en job_registry.db
    ↓
Emite eventos vía WebSocket
    ↓
Monitor y usuario actualizados
    ↓
Trabajo disponible para descargar
    ↓
Consulta en registro permanente
```

---

## 📱 Características Clave

✅ **Multiimpresora:** 3 impresoras virtuales procesando en paralelo  
✅ **Colas dinámicas:** Cambio entre FIFO y Priority sin reiniciar  
✅ **WebSocket:** Actualizaciones en tiempo real  
✅ **Base de datos:** Registro persistente en SQLite  
✅ **Interfaz moderna:** Diseño responsivo y atractivo  
✅ **Manejo de errores:** Validaciones y mensajes descriptivos  
✅ **Carga por lotes:** Procesamiento de múltiples archivos  
✅ **Estadísticas:** Análisis completo del sistema  

---

## 📝 Notas Importantes

- La base de datos `job_registry.db` **NO se versionará en Git** (está en `.gitignore`)
- Los PDFs en `uploads/` también están en `.gitignore`
- El servidor usa **multiprocessing** para simular impresoras reales
- Cada página es **totalmente responsiva** para dispositivos móviles
- Las conexiones **WebSocket** requieren navegador moderno

---

**Versión:** 1.0  
**Última actualización:** Diciembre 2025  
**Autor:** Sistema de Impresión PDF
