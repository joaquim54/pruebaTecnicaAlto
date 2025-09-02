Prueba Técnica – API de Búsqueda de Estaciones de Combustible

API en Python + FastAPI que consulta la API pública de Bencina en Línea (endpoint descubierto por inspección) y resuelve 4 casos de búsqueda:

Estación más cercana por producto

Más cercana entre las de menor precio por producto

Más cercana con tienda por producto

Más cercana con tienda y menor precio por producto

La API normaliza datos heterogéneos de la fuente (nombres de productos, claves con mayúsculas/minúsculas, etc.) y, cuando es necesario, consulta el detalle de estación para confirmar si tiene tienda.

Índice

Requisitos

Instalación y ejecución

Uso

Parámetros

Ejemplo de respuesta

Estructura del proyecto

Manejo de errores

Notas técnicas

Tests

Entrega

Requisitos

Python 3.11+

pip

(Opcional) Git para clonar el repo

Instalación y ejecución
1) Clonar y entrar al proyecto
git clone https://github.com/joaquim54/pruebaTecnicaAlto.git
cd pruebaTecnicaAlto

2) Crear y activar entorno virtual

Windows (PowerShell)

python -m venv .venv
.venv\Scripts\Activate.ps1


Windows (CMD)

python -m venv .venv
.venv\Scripts\activate.bat


macOS / Linux

python3 -m venv .venv
source .venv/bin/activate


Para salir del venv: deactivate

3) Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

4) Ejecutar en modo desarrollo
uvicorn app.main:app --reload --port 8000


Swagger UI: http://127.0.0.1:8000/docs

OpenAPI JSON: http://127.0.0.1:8000/openapi.json

Uso

Endpoint principal

GET /api/stations/search

Ejemplos rápidos

1. Más cercana (producto 95)

curl "http://127.0.0.1:8000/api/stations/search?lat=-33.6181&lng=-70.74&product=95"


2. Más cercana con tienda

curl "http://127.0.0.1:8000/api/stations/search?lat=-33.6181&lng=-70.74&product=95&store=true"


3. Más cercana entre las de menor precio

curl "http://127.0.0.1:8000/api/stations/search?lat=-33.6181&lng=-70.74&product=95&cheapest=true"


4. Más cercana con tienda y menor precio

curl "http://127.0.0.1:8000/api/stations/search?lat=-33.6181&lng=-70.74&product=95&store=true&cheapest=true"


Modo mock (sin Internet)

curl "http://127.0.0.1:8000/api/stations/search?lat=-33.6&lng=-70.7&product=95&mock=1"