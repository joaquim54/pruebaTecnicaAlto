# Prueba Técnica – API de Búsqueda de Estaciones

API en **Python + FastAPI** que consulta la API pública de **Bencina en Línea** (endpoint descubierto por inspección) y resuelve 4 casos de búsqueda:

1. Estación **más cercana** por producto  
2. Estación **más cercana entre las de menor precio** por producto  
3. Estación **más cercana con tienda** por producto  
4. Estación **más cercana con tienda y menor precio** por producto

## Requisitos

- Python 3.11+
- pip

## Instalación

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate  # Mac/Linux

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
