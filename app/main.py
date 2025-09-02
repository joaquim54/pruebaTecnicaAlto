# app/main.py
import asyncio
from fastapi import FastAPI, Query, HTTPException
from typing import Any, Dict, List
from .service import (
    fetch_estaciones,
    station_has_store,
    station_has_store_async_bulk,
    fetch_estacion_detalle
)
from .models import (
    haversine_km,
    normalize_product,
    parse_price_for_product,
    get_first,
    extract_lat_lon,
)
from .schema import StationOut

app = FastAPI(title="Estaciones API", version="1.0.0")

@app.get("/")
def root():
    return {"message": "Estaciones API OK. Visita /docs para probar."}

def build_station_out(est: Dict[str, Any], dist_km: float) -> StationOut:
    latlon = extract_lat_lon(est)
    if not latlon:
        raise HTTPException(status_code=500, detail="Estación sin coordenadas")

    precios = {
        "93": parse_price_for_product(est, "93"),
        "95": parse_price_for_product(est, "95"),
        "97": parse_price_for_product(est, "97"),
        "diesel": parse_price_for_product(est, "diesel"),
        "kerosene": parse_price_for_product(est, "kerosene"),
    }
    return StationOut(
        id=str(est.get("CodEs") or est.get("id") or ""),
        compania=str(get_first(est, "Compania", "compania", "marca", default="")),
        direccion=str(get_first(est, "Direccion", "direccion", default="")),
        comuna=str(get_first(est, "Comuna", "comuna", default="")),
        region=str(get_first(est, "Region", "region", default="")),
        latitud=float(latlon[0]),
        longitud=float(latlon[1]),
        distancia_km=dist_km,
        precios=precios,
        # usa chequeo rápido o el flag que marcamos al consultar detalle
        tiene_tienda=(station_has_store(est) or bool(est.get("_has_store"))),
        tienda=est.get("tienda") or est.get("Tienda") or None,
    )

@app.get("/api/stations/search")
@app.get("/api/stations/search")
async def search_stations(
    lat: float = Query(..., description="Latitud"),
    lng: float = Query(..., description="Longitud"),
    product: str = Query(..., description="93,95,97,diesel,kerosene"),
    nearest: bool = Query(True, description="Devolver la estación más cercana"),
    store: bool = Query(False, description="Requerir tienda"),
    cheapest: bool = Query(False, description="Filtrar por menor precio"),
    mock: int = Query(0, description="1 = datos de prueba"),
):
    fam = normalize_product(product)
    if not fam:
        raise HTTPException(status_code=400, detail="product inválido: use 93,95,97,diesel,kerosene")

    # 1) Obtener estaciones
    if mock == 1:
        estaciones = [
            {
                "CodEs": "1001", "Compania": "COPEC", "Direccion": "Av. Principal 123",
                "Comuna": "Buin", "Region": "RM", "Latitud": "-33.7335", "Longitud": "-70.7422",
                "Prices": [
                    {"Producto": "Gasolina 93", "Precio": "1290"},
                    {"Producto": "Gasolina 95", "Precio": "1340"},
                    {"Producto": "Diésel",      "Precio": "1090"},
                ],
                "Tienda": {"NombreTienda": "Pronto Copec"}
            },
            {
                "CodEs": "1002", "Compania": "SHELL", "Direccion": "Ruta 5 KM 45",
                "Comuna": "Buin", "Region": "RM", "Latitud": "-33.6500", "Longitud": "-70.7200",
                "Prices": [
                    {"Producto": "Gasolina 93", "Precio": "1285"},
                    {"Producto": "Gasolina 95", "Precio": "1335"},
                    {"Producto": "Diésel",      "Precio": "1080"},
                ],
            },
        ]
    else:
        params: Dict[str, Any] = {"latitud": lat, "longitud": lng}
        estaciones = await fetch_estaciones(params)

    # 2) Calcular distancias y precios
    enriched: List[Dict[str, Any]] = []
    for e in estaciones:
        coords = extract_lat_lon(e)
        if not coords:
            continue
        d = haversine_km(lat, lng, coords[0], coords[1])
        price = parse_price_for_product(e, fam)
        enriched.append({"raw": e, "dist": d, "price": price})

    if not enriched:
        raise HTTPException(status_code=404, detail="Sin estaciones válidas con coordenadas")

    # 3) Si piden tienda, primero intento rápido; si no hay, consulto detalle a las N más cercanas
    if store:
        quick = [x for x in enriched if station_has_store(x["raw"])]
        if not quick:
            MAX_DETAIL = 40
            subset = sorted(enriched, key=lambda x: x["dist"])[:MAX_DETAIL]
            flags = await station_has_store_async_bulk(
                [x["raw"] for x in subset], concurrency=8, timeout=15.0
            )
            ids_ok = {
                str(e.get("CodEs") or e.get("id") or "")
                for e, ok in zip([x["raw"] for x in subset], flags) if ok
            }
            enriched = [x for x in enriched if str(x["raw"].get("CodEs") or x["raw"].get("id") or "") in ids_ok]
            for x in enriched:
                x["raw"]["_has_store"] = True
        else:
            enriched = quick

        if not enriched:
            raise HTTPException(status_code=404, detail="No hay estaciones con tienda en el área")

    # 4) Si piden cheapest, filtrar por menor precio dentro del set actual
    subset = enriched
    if cheapest:
        precios_validos = [x["price"] for x in enriched if x["price"] is not None]
        if not precios_validos:
            raise HTTPException(status_code=404, detail="No hay precios para ese producto")
        min_price = min(precios_validos)
        subset = [x for x in enriched if x["price"] is not None and x["price"] == min_price]

    # 5) Devolver la más cercana del subset (siempre se define 'best')
    best = min(subset, key=lambda x: x["dist"])

    # 6) Si pidieron tienda y el objeto no viene, completar con detalle/fallback
    if store:
        raw = best["raw"]
        if not (raw.get("tienda") or raw.get("Tienda")):
            station_id = str(raw.get("CodEs") or raw.get("id") or "").strip()
            if station_id:
                try:
                    det = await fetch_estacion_detalle(station_id)

                    # intento directo
                    tienda_obj = det.get("tienda") or det.get("Tienda")

                    # fallback por servicios
                    if not tienda_obj:
                        servicios = det.get("servicios") or det.get("Servicios") or []
                        if isinstance(servicios, dict):  # {"CodSer": [...]}
                            servicios = servicios.get("CodSer") or []

                        names = []
                        for s in servicios:
                            if isinstance(s, dict):
                                names.append(str(s.get("nombre") or s.get("Nombre") or "").lower())
                            else:
                                names.append(str(s).lower())

                        brand = None
                        if any("pronto" in n for n in names):
                            brand = "Pronto"
                        elif any("upita" in n for n in names):
                            brand = "Upita"
                        elif any("spacio" in n for n in names):
                            brand = "Spacio 1"
                        elif any("tienda" in n or "convenien" in n or "minimarket" in n for n in names):
                            brand = "Tienda de conveniencia"

                        if brand:
                            tienda_obj = {"nombre": brand, "fuente": "servicios"}

                    if tienda_obj:
                        raw["tienda"] = tienda_obj

                except Exception:
                    pass  # mantenemos tiene_tienda=True pero tienda=None

    return {"success": True, "data": build_station_out(best["raw"], best["dist"]).dict()}
