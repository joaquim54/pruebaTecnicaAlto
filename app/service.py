from typing import Any, Dict, List
import httpx
import asyncio

SEARCH_URL = "https://api.bencinaenlinea.cl/api/busqueda_estacion_filtro"
DETAIL_URL = "https://api.bencinaenlinea.cl/api/estacion_ciudadano/{id}"

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0",
    "Origin": "https://www.bencinaenlinea.cl",
    "Referer": "https://www.bencinaenlinea.cl/",
}

async def fetch_estacion_detalle(station_id: str) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=20.0, headers=HEADERS) as client:
        r = await client.get(DETAIL_URL.format(id=station_id))
        r.raise_for_status()
        data = r.json()
        return data.get("data", data)


async def fetch_estaciones(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    async with httpx.AsyncClient(timeout=30.0, headers=HEADERS) as client:
        r = await client.get(SEARCH_URL, params=params)
        r.raise_for_status()
        data = r.json()
        return data.get("data", []) if isinstance(data, dict) else data

def station_has_store(est: Dict[str, Any]) -> bool:

    flag = est.get("tiene_tienda")
    if isinstance(flag, bool) and flag:
        return True
    if isinstance(flag, str) and flag.strip().lower() in {"true", "1", "sí", "si"}:
        return True

    t = est.get("tienda") or est.get("Tienda")
    if isinstance(t, dict) and t:
        return True

    servicios = est.get("servicios") or []
    for s in servicios:
        nombre = str(s.get("nombre") or s.get("Nombre") or "").lower()
        if any(pal in nombre for pal in ["tienda", "convenien", "minimarket", "pronto", "upita"]):
            return True
    return False
async def _has_store_from_detail(client: httpx.AsyncClient, station_id: str) -> bool:
    try:
        r = await client.get(DETAIL_URL.format(id=station_id))
        r.raise_for_status()
        det = r.json()
        det = det.get("data", det) if isinstance(det, dict) else det
    except Exception:
        return False

    flag = det.get("tiene_tienda")
    if isinstance(flag, bool) and flag:
        return True
    if isinstance(flag, str) and flag.strip().lower() in {"true", "1", "sí", "si"}:
        return True

    t = det.get("tienda") or det.get("Tienda")
    if isinstance(t, dict) and t:
        return True

    servicios = det.get("servicios") or det.get("Servicios") or []
    if isinstance(servicios, dict):
        servicios = servicios.get("CodSer") or []
    for s in servicios:
        name = ""
        if isinstance(s, dict):
            name = str(s.get("nombre") or s.get("Nombre") or "")
        elif isinstance(s, str):
            name = s
        if name and any(p in name.lower() for p in ["tienda", "convenien", "minimarket", "pronto", "upita"]):
            return True
    return False

async def station_has_store_async_bulk(
    estaciones: List[Dict[str, Any]],
    concurrency: int = 8,
    timeout: float = 15.0,
) -> List[bool]:
    """
    Revisa en paralelo (con límite de concurrencia) si las estaciones tienen tienda,
    consultando el endpoint de detalle solo cuando el chequeo rápido no basta.
    """
    sem = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient(timeout=timeout, headers=HEADERS) as client:
        async def check(e: Dict[str, Any]) -> bool:

            if station_has_store(e):
                return True
            station_id = str(e.get("CodEs") or e.get("id") or "").strip()
            if not station_id:
                return False
            async with sem:
                return await _has_store_from_detail(client, station_id)

        return await asyncio.gather(*[check(e) for e in estaciones])