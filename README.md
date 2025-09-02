# Prueba Técnica – API de Búsqueda de Estaciones de Combustible

API en **Python + FastAPI** que consulta la API pública de **Bencina en Línea** (endpoint descubierto por inspección) y resuelve 4 casos de búsqueda:

1) **Estación más cercana** por producto  
2) **Más cercana entre las de menor precio** por producto  
3) **Más cercana con tienda** por producto  
4) **Más cercana con tienda y menor precio** por producto



## Requisitos

- **Python 3.11+**
- **pip**



## Instalación y ejecución

### 1) Clonar y entrar al proyecto
```bash
git clone https://github.com/joaquim54/pruebaTecnicaAlto.git
cd pruebaTecnicaAlto
2) Crear y activar entorno virtual
Windows (PowerShell):

powershell
Copiar código
python -m venv .venv
.venv\Scripts\Activate.ps1
Windows (CMD):

cmd
Copiar código
python -m venv .venv
.venv\Scripts\activate.bat
macOS / Linux:

bash
Copiar código
python3 -m venv .venv
source .venv/bin/activate
Para salir del venv: deactivate

3) Instalar dependencias
bash
Copiar código
pip install --upgrade pip
pip install -r requirements.txt
4) Ejecutar en modo desarrollo
bash
Copiar código
uvicorn app.main:app --reload --port 8000
Swagger UI: http://127.0.0.1:8000/docs

OpenAPI JSON: http://127.0.0.1:8000/openapi.json

Uso rápido
Más cercana por producto
bash
Copiar código
curl "http://127.0.0.1:8000/api/stations/search?lat=-33.45&lng=-70.66&product=95"
Más cercana ENTRE las de menor precio
bash
Copiar código
curl "http://127.0.0.1:8000/api/stations/search?lat=-33.45&lng=-70.66&product=95&cheapest=true"
Más cercana con tienda
bash
Copiar código
curl "http://127.0.0.1:8000/api/stations/search?lat=-33.45&lng=-70.66&product=95&store=true"
Más cercana con tienda y menor precio
bash
Copiar código
curl "http://127.0.0.1:8000/api/stations/search?lat=-33.45&lng=-70.66&product=95&store=true&cheapest=true"
Modo mock (sin depender de Internet)
bash
Copiar código
curl "http://127.0.0.1:8000/api/stations/search?lat=-33.6&lng=-70.7&product=95&mock=1"


Ejemplo de respuesta
json
Copiar código
{
  "success": true,
  "data": {
    "id": "2069",
    "compania": "A4",
    "direccion": "Panamericana Sur Km. 21",
    "comuna": "San Bernardo",
    "region": "Metropolitana de Santiago",
    "latitud": -33.614949,
    "longitud": -70.716499,
    "distancia_km": 2.21,
    "precios": {
      "93": null,
      "95": null,
      "97": null,
      "diesel": 1011.0,
      "kerosene": null
    },
    "tiene_tienda": true,
    "tienda": {
      "nombre": "Tienda de conveniencia",
      "fuente": "servicios"
    }
  }
}
