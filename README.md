# Creador de Dashboards con IA - Backend

Backend API para la aplicación de creación de dashboards con IA. Este backend procesa archivos .xlsx y .csv, analiza los datos con IA y genera sugerencias de visualización.

## 🚀 Características

- **Procesamiento de archivos**: Soporta archivos .xlsx, .xls y .csv usando pandas
- **Análisis con IA**: Analiza datos y genera sugerencias de visualización (mock o Claude)
- **API RESTful**: Endpoints para subir archivos y obtener datos de gráficos
- **CORS configurado**: Listo para trabajar con el frontend React

## 📋 Requisitos

- Python 3.8+
- pip

## 🛠️ Instalación

1. Crea un entorno virtual (recomendado):
```bash
python -m venv venv
```

2. Activa el entorno virtual:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

4. Configura las variables de entorno:
```bash
# Para desarrollo: copia el archivo de ejemplo y agrega tu API key
cp env.development.example .env.development
# Edita .env.development y agrega tu AI_API_KEY

# Para producción: copia el archivo de ejemplo y agrega tu API key
cp env.production.example .env.production
# Edita .env.production y agrega tu AI_API_KEY

# O crea un archivo .env simple en la raíz del proyecto
# con AI_API_KEY=tu_clave_aqui
```

## 🚀 Ejecución

### Opción 1: Usando el script
- Windows: `start.bat`
- Linux/Mac: `bash start.sh`

### Opción 2: Directamente con Python
```bash
python main.py
```

### Opción 3: Con uvicorn
```bash
uvicorn main:app --reload --port 8000
```

El backend estará disponible en `http://localhost:8000`

## 📡 Endpoints

### GET /
Información básica de la API

### GET /api/health
Health check del servidor

### POST /api/upload
Sube y procesa un archivo .xlsx o .csv

**Request:**
- Content-Type: `multipart/form-data`
- Body: archivo con nombre `file`

**Response:**
```json
{
  "success": true,
  "message": "Archivo procesado exitosamente...",
  "suggestions": [
    {
      "title": "Distribución de Ventas por Región",
      "chart_type": "bar",
      "parameters": {
        "x_axis": "Región",
        "y_axis": "Ventas",
        "group_by": "Región",
        "aggregate": "sum"
      },
      "insight": "Este gráfico muestra..."
    }
  ],
  "file_info": {
    "file_id": "uuid-del-archivo",
    "filename": "archivo.xlsx",
    "rows": 100,
    "columns": 5,
    "column_names": ["Col1", "Col2", ...]
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
    "x_axis": "Región",
    "y_axis": "Ventas",
    "group_by": "Región",
    "aggregate": "sum"
  }
}
```

**Response:**
```json
{
  "success": true,
  "chart_type": "bar",
  "data": [
    {"name": "Norte", "value": 1500.0},
    {"name": "Sur", "value": 1200.0}
  ],
  "labels": ["Norte", "Sur"]
}
```

## 🔧 Configuración

### Variables de Entorno (.env)

- `AI_API_KEY`: Tu clave de API de IA (Claude, OpenAI, etc.) (opcional, usa mock si no está configurada)
- `BACKEND_PORT`: Puerto del servidor (default: 8000)
- `ENVIRONMENT`: Entorno de ejecución (development/production)

## 🧪 Modo Mock vs Real

Por defecto, la aplicación usa un analizador mock que genera sugerencias inteligentes basadas en la estructura de los datos. Para usar la API real de IA (actualmente Claude):

1. Obtén una clave de API según el proveedor que uses:
   - Claude: https://console.anthropic.com/
   - OpenAI: https://platform.openai.com/api-keys
2. Agrega `AI_API_KEY=tu_clave_aqui` al archivo `.env` o `.env.development`/`.env.production`
3. Reinicia el servidor backend

## 🏗️ Estructura del Proyecto

```
maic-BACKEND-bi-ai-powered-dashboard/
├── main.py                 # Aplicación FastAPI principal
├── models/
│   └── schemas.py          # Modelos Pydantic
├── services/
│   ├── data_processor.py   # Procesamiento de archivos
│   └── ai_analyzer.py       # Análisis con IA
├── requirements.txt        # Dependencias Python
├── .env.example           # Variables de entorno ejemplo
└── README.md              # Este archivo
```

## 📚 Tecnologías Utilizadas

- **FastAPI**: Framework web moderno y rápido
- **Pandas**: Procesamiento y análisis de datos
- **Anthropic (Claude)**: Integración con modelos de lenguaje (opcional)
- **Pydantic**: Validación de datos
- **Uvicorn**: Servidor ASGI

## 🔍 Documentación de la API

Cuando el servidor esté ejecutándose, puedes acceder a la documentación interactiva en:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📝 Notas

- Los DataFrames se almacenan en memoria durante la sesión del servidor
- En producción, considera usar un sistema de cache o base de datos
- Los archivos temporales se eliminan automáticamente después del procesamiento

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT.
