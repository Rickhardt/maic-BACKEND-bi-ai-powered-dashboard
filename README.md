# Creador de Dashboards con IA - Backend

Backend API para la aplicación de creación de dashboards con IA. Este backend procesa archivos .xlsx y .csv, analiza los datos con IA y genera sugerencias de visualización.

## Características

- **Procesamiento de archivos**: Soporta archivos .xlsx, .xls y .csv usando pandas
- **Análisis con IA**: Analiza datos y genera sugerencias de visualización (mock o Claude)
- **API RESTful**: Endpoints para subir archivos y obtener datos de gráficos
- **CORS configurado**: Listo para trabajar con el frontend React
- **Soporte para múltiples codificaciones**: Maneja automáticamente diferentes codificaciones de archivos CSV
- **Análisis de datos categóricos**: Genera sugerencias incluso para archivos con solo columnas categóricas

## Requisitos Previos

- **Python 3.8 o superior**

### Verificar instalación
```bash
# Verificar versión de Python
python --version
# Debe mostrar Python 3.8 o superior

# Verificar pip
pip --version
```

## Instalación Paso a Paso

### 1. Clonar o descargar el proyecto

Si tiene el repositorio en Git:
```bash
git clone https://github.com/Rickhardt/maic-BACKEND-bi-ai-powered-dashboard.git
cd maic-BACKEND-bi-ai-powered-dashboard
```

Si descargó el proyecto como ZIP, extraiga los archivos y navegue a la carpeta.

### 2. Crear entorno virtual

**Windows:**
```bash
python -m venv venv
```

**Linux/Mac:**
```bash
python3 -m venv venv
```

### 3. Activar el entorno virtual

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

> 💡 **Nota**: Cuando el entorno virtual esté activo, verá `(venv)` al inicio de su línea de comandos.

### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```

Esto instalará todas las dependencias necesarias:
- FastAPI
- Uvicorn
- Pandas
- OpenPyXL
- Pydantic
- Anthropic (para Claude API)
- Y otras dependencias

### 5. Configurar variables de entorno

Cree un archivo `.env` en la raíz del proyecto:

**Windows:**
```cmd
type nul > .env
```

**Linux/Mac:**
```bash
touch .env
```

Luego edite el archivo `.env` y agregue las siguientes variables (todas son opcionales):
```env
# Puerto del servidor (opcional, default: 8000)
# En Render, usa PORT automáticamente
BACKEND_PORT=8000

# Clave de API de Anthropic/Claude (opcional)
# Si no se configura, se usa el analizador mock
AI_API_KEY=su_clave_aqui

# Orígenes permitidos para CORS (opcional)
# Separe múltiples orígenes con comas
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,https://su-frontend.vercel.app
```

> **Importante**: El archivo `.env` está en `.gitignore` y no se subirá al repositorio. Esto es por seguridad.

## Ejecutar el Proyecto

### Opción 1: Usando los scripts incluidos (Recomendado)

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
bash start.sh
```

### Opción 2: Directamente con Python
```bash
python main.py
```

### Opción 3: Con uvicorn directamente
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

> **Consejo**: Use `--reload` solo en desarrollo. En producción, omítalo.

### Verificar que funciona

Una vez iniciado, debería ver un mensaje similar a:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Abra su navegador y visite:
- `http://localhost:8000` - Página principal
- `http://localhost:8000/docs` - Documentación interactiva (Swagger UI)
- `http://localhost:8000/api/health` - Health check

## Endpoints de la API

### GET /
Información básica de la API

**Ejemplo de respuesta:**
```json
{
  "message": "Dashboard Creator API",
  "status": "running"
}
```

### GET /api/health
Health check del servidor

**Ejemplo de respuesta:**
```json
{
  "status": "healthy"
}
```

### GET /api/test-anthropic
Prueba la configuración del cliente de Anthropic/Claude

**Ejemplo de respuesta:**
```json
{
  "anthropic_available": true,
  "api_key_configured": true,
  "client_initialization": "success",
  "status": "ready"
}
```

### GET /api/cors-info
Información sobre la configuración CORS (útil para debugging)

**Ejemplo de respuesta:**
```json
{
  "origin_header": "http://localhost:5173",
  "configured_origins": ["http://localhost:5173", "..."],
  "is_origin_allowed": true
}
```

### POST /api/upload
Sube y procesa un archivo .xlsx o .csv

**Request:**
- **Content-Type**: `multipart/form-data`
- **Body**: archivo con nombre `file`

**Ejemplo con curl:**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@ruta/a/su/archivo.csv"
```

**Ejemplo de respuesta:**
```json
{
  "success": true,
  "message": "Archivo procesado exitosamente. 3 sugerencias generadas.",
  "suggestions": [
    {
      "title": "Frecuencia de PROCESSPLANNAME",
      "chart_type": "bar",
      "parameters": {
        "x_axis": "PROCESSPLANNAME",
        "y_axis": "count",
        "group_by": "PROCESSPLANNAME",
        "aggregate": "count"
      },
      "insight": "Este gráfico muestra la frecuencia de cada valor único..."
    }
  ],
  "file_info": {
    "file_id": "uuid-del-archivo",
    "filename": "archivo.csv",
    "rows": 19500,
    "columns": 2,
    "column_names": ["PROCESSPLANNAME", "STEP_HANDLE"]
  }
}
```

### POST /api/chart-data
Obtiene datos agregados para un gráfico específico

**Request:**
```json
{
  "file_id": "uuid-del-archivo",
  "chart_type": "bar",
  "parameters": {
    "x_axis": "PROCESSPLANNAME",
    "y_axis": "count",
    "group_by": "PROCESSPLANNAME",
    "aggregate": "count"
  }
}
```

**Ejemplo de respuesta:**
```json
{
  "success": true,
  "chart_type": "bar",
  "data": [
    {"name": "S_PR_MNG_SWHK1291FG", "value": 150.0},
    {"name": "S_ASS_Pulse_LCS", "value": 120.0}
  ],
  "labels": ["S_PR_MNG_SWHK1291FG", "S_ASS_Pulse_LCS"]
}
```

## Configuración Detallada

### Variables de Entorno

| Variable | Descripción | Requerido | Default |
|----------|-------------|-----------|---------|
| `BACKEND_PORT` | Puerto del servidor (desarrollo local) | No | `8000` |
| `PORT` | Puerto del servidor (usado automáticamente por Render) | No | `8000` |
| `AI_API_KEY` | Clave de API de Anthropic/Claude | No | - (usa mock) |
| `ALLOWED_ORIGINS` | Orígenes permitidos para CORS (separados por comas) | No | Lista por defecto |

> **Nota sobre puertos**: El código primero intenta usar `PORT` (para Render), luego `BACKEND_PORT` (para desarrollo local), y finalmente usa `8000` como default.

### Configuración de CORS

Por defecto, los siguientes orígenes están permitidos:
- `http://localhost:5173` (Vite)
- `http://localhost:3000` (React)
- `http://127.0.0.1:5173`
- `http://127.0.0.1:3000`
- `https://bi-dashboard-vert.vercel.app`

Para agregar más orígenes, use la variable de entorno `ALLOWED_ORIGINS`:
```env
ALLOWED_ORIGINS=http://localhost:5173,https://su-frontend.vercel.app,https://otro-dominio.com
```

## Modo Mock vs Real

### Modo Mock (Por defecto)

Si no configura `AI_API_KEY`, la aplicación usa un analizador mock que genera sugerencias inteligentes basadas en la estructura de los datos. Este modo:
- ✅ No requiere configuración adicional
- ✅ No consume tokens de API
- ✅ Funciona perfectamente para la mayoría de casos
- ✅ Genera sugerencias para archivos con columnas numéricas y categóricas

### Modo Real (Claude API)

Para usar la API real de Claude:

1. **Obtenga una clave de API:**
   - Vaya a https://console.anthropic.com/
   - Cree una cuenta o inicie sesión
   - Genere una nueva API key

2. **Configure la clave:**
   - Agregue `AI_API_KEY=su_clave_aqui` al archivo `.env`
   - Reinicie el servidor

3. **Verifique la configuración:**
   - Visite `http://localhost:8000/api/test-anthropic`
   - Debería ver `"client_initialization": "success"`

> ⚠️ **Importante**: El modo real consume tokens de la API de Claude, lo cual puede tener costos asociados.

## Deploy en Render

### Requisitos Previos

1. Cuenta en [Render](https://render.com)
2. Repositorio Git (GitHub, GitLab, etc.)

### Pasos para Deploy

1. **Conecte su repositorio:**
   - En Render, vaya a "New" → "Web Service"
   - Conecte su repositorio de Git

2. **Configure el servicio:**
   - **Name**: Nombre de su servicio (ej: `dashboard-backend`)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Configure variables de entorno:**
   - Vaya a "Environment" en la configuración del servicio
   - Agregue las siguientes variables:
```
     AI_API_KEY=su_clave_aqui (opcional)
     ALLOWED_ORIGINS=https://su-frontend.vercel.app (opcional)
```
   - **No necesita configurar PORT** - Render lo hace automáticamente

4. **Deploy:**
   - Haga clic en "Create Web Service"
   - Render construirá y desplegará su aplicación automáticamente

### Verificar el Deploy

Una vez desplegado, puede verificar:
- `https://su-servicio.onrender.com/` - Página principal
- `https://su-servicio.onrender.com/docs` - Documentación
- `https://su-servicio.onrender.com/api/health` - Health check
- `https://su-servicio.onrender.com/api/test-anthropic` - Test de Anthropic

## Solución de Problemas

### Error: "No module named 'fastapi'"

**Solución**: Asegúrese de haber activado el entorno virtual y haber instalado las dependencias:
```bash
# Active el entorno virtual
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instale las dependencias
pip install -r requirements.txt
```

### Error: "Address already in use"

**Solución**: El puerto 8000 está en uso. Cambie el puerto:
```bash
# Opción 1: Cambiar en .env
BACKEND_PORT=8001

# Opción 2: Especificar en el comando
uvicorn main:app --port 8001
```

### Error de CORS en el navegador

**Solución**: 
1. Verifique el origen exacto visitando `/api/cors-info`
2. Agregue el origen a `ALLOWED_ORIGINS` en `.env` o en Render
3. Asegúrese de que no haya diferencias sutiles (http vs https, con/sin barra final)

### Error: "Error al leer archivo CSV"

**Solución**: El código intenta múltiples codificaciones automáticamente. Si persiste:
- Verifique que el archivo no esté corrupto
- Asegúrese de que el archivo tenga datos válidos
- Revise los logs para ver el error específico

### Error: "Client.__init__() got an unexpected keyword argument 'proxies'"

**Solución**: Este error se maneja automáticamente y la API usa el modo mock. Si quiere usar Claude:
1. Actualice la versión de anthropic: `pip install --upgrade anthropic`
2. Verifique la configuración en `/api/test-anthropic`

### Error 500 al subir archivo

**Solución**:
1. Revise los logs del servidor para ver el error específico
2. Verifique que el archivo no esté vacío
3. Asegúrese de que el archivo tenga el formato correcto (.csv, .xlsx, .xls)
4. Revise que todas las dependencias estén instaladas correctamente


## Tecnologías Utilizadas

- **FastAPI**: Framework web moderno y rápido para APIs
- **Uvicorn**: Servidor ASGI de alto rendimiento
- **Pandas**: Procesamiento y análisis de datos
- **OpenPyXL**: Lectura de archivos Excel
- **Anthropic (Claude)**: Integración con modelos de lenguaje.
- **Pydantic**: Validación de datos y modelos
- **Python-dotenv**: Manejo de variables de entorno

## Documentación Interactiva

Cuando el servidor esté ejecutándose, puede acceder a:

- **Swagger UI**: `http://localhost:8000/docs`
  - Interfaz interactiva para probar todos los endpoints
  - Incluye ejemplos y esquemas de datos

- **ReDoc**: `http://localhost:8000/redoc`
  - Documentación alternativa con mejor formato para lectura

## Notas Importantes

- **Almacenamiento en memoria**: Los DataFrames se almacenan en memoria durante la sesión del servidor. Si reinicia el servidor, se perderán los datos.
- **Archivos temporales**: Los archivos subidos se procesan y eliminan automáticamente.
- **Producción**: Para producción, considere usar un sistema de cache o base de datos para persistir los datos.
- **Seguridad**: Nunca suba el archivo `.env` al repositorio. Está en `.gitignore` por seguridad.