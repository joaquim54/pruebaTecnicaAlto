from typing import Any, Dict, Optional
import math

PRODUCT_ALIASES = {
    "93": {"93", "gasolina 93"},
    "95": {"95", "gasolina 95"},
    "97": {"97", "gasolina 97"},
    "diesel": {"diesel", "di", "d", "petroleo diesel", "petróleo diésel", "petroleo di"},
    "kerosene": {"kerosene", "kero", "kerosén"},
}

def _norm(s: str) -> str:
    return (s or "").strip().lower()

def normalize_product(p: str) -> Optional[str]:
    w = _norm(p)
    for key, aliases in PRODUCT_ALIASES.items():
        if w in aliases or w == key:
            return key
    return None

def to_float_safe(x: Any) -> Optional[float]:
    if x is None:
        return None
    try:
        return float(str(x).replace(",", "."))
    except Exception:
        return None

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl   = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(p1) * math.cos(p2) * math.sin(dl/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# helper de lectura tolerante a claves en mayúsc/minúsc
def get_first(est: Dict[str, Any], *keys, default=None):
    for k in keys:
        if k in est and est[k] not in (None, "", "null"):
            return est[k]
    return default

def parse_price_for_product(est: Dict[str, Any], product: str) -> Optional[float]:
    fam = normalize_product(product)
    if not fam:
        return None

    # 1) Formato clásico "Prices"
    target_names = {
        "93": {"gasolina 93", "93"},
        "95": {"gasolina 95", "95"},
        "97": {"gasolina 97", "97"},
        "diesel": {"diesel", "di", "petróleo diésel", "petroleo diesel"},
        "kerosene": {"kerosene", "kerosén"},
    }
    prices = est.get("Prices") or est.get("prices") or []
    for item in prices:
        name = _norm(item.get("Producto") or item.get("producto") or "")
        if name in target_names.get(fam, set()):
            val = to_float_safe(item.get("Precio") or item.get("precio"))
            if val is not None:
                return val

    # 2) Formato nuevo "combustibles"
    combs = est.get("combustibles") or []
    alias = {
        "diesel": {"di", "diesel", "d", "petroleo di", "petróleo diésel"},
        "kerosene": {"kerosene", "kero", "kerosén"},
        "93": {"93", "gasolina 93"},
        "95": {"95", "gasolina 95"},
        "97": {"97", "gasolina 97"},
    }
    for c in combs:
        nombre_corto = _norm(str(c.get("nombre_corto") or ""))
        if fam in {"93","95","97"} and nombre_corto == fam:
            return to_float_safe(c.get("precio"))
        if fam in {"diesel","kerosene"} and (nombre_corto in alias[fam]):
            return to_float_safe(c.get("precio"))
    return None

def extract_lat_lon(est: Dict[str, Any]) -> Optional[tuple]:
    lat = to_float_safe(get_first(est, "latitud", "Latitud"))
    lon = to_float_safe(get_first(est, "longitud", "Longitud"))
    if lat is None or lon is None:
        return None
    return (lat, lon)
