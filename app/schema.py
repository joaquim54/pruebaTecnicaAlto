from pydantic import BaseModel
from typing import Dict, Optional

class StationOut(BaseModel):
    id: str
    compania: str
    direccion: str
    comuna: str
    region: str
    latitud: float
    longitud: float
    distancia_km: float
    precios: Dict[str, Optional[float]]
    tiene_tienda: bool
    tienda: Optional[dict] = None
