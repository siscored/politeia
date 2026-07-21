"""
politeia-api-mapa — API read-only del mapa electoral.

Lee vista_mapa.csv desde S3 (lo cachea en memoria entre invocaciones) y
devuelve, para un filtro distrito/año/cargo/tipo, el resultado por circuito:
fuerza ganadora, % y la composición completa (para el hover del mapa).

Dataset chico (2,7 MB) → leer el CSV directo es más rápido y barato que
Athena en el camino crítico. Sin dependencias externas (csv + boto3).

GET /?distrito=pilar&anio=2023&cargo=PRESIDENTE&tipo=GENERAL
GET /?meta=1     -> dimensiones disponibles para armar los filtros de la UI
"""
import os
import io
import csv
import json

import boto3

s3 = boto3.client("s3")
BUCKET = os.environ["DATA_BUCKET"]
VM_KEY = os.environ.get("VISTA_MAPA_KEY", "electoral/procesados/vista_mapa/vista_mapa.csv")

_CACHE = {}

CORS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,OPTIONS",
    "Access-Control-Allow-Headers": "*",
    "Content-Type": "application/json; charset=utf-8",
}


def _rows():
    if "rows" not in _CACHE:
        body = s3.get_object(Bucket=BUCKET, Key=VM_KEY)["Body"].read().decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(body))
        # La columna del año viene con ñ ("año"); la renombramos a 'anio'.
        anio_key = next(
            (k for k in (reader.fieldnames or []) if k.strip().lower() in ("año", "ano", "anio")),
            "año",
        )
        rows = []
        for r in reader:
            r["anio"] = r.get(anio_key, "")
            rows.append(r)
        _CACHE["rows"] = rows
    return _CACHE["rows"]


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _resp(status, body):
    return {"statusCode": status, "headers": CORS, "body": json.dumps(body, ensure_ascii=False)}


def lambda_handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method", "GET")
    if method == "OPTIONS":
        return {"statusCode": 204, "headers": CORS, "body": ""}

    qs = event.get("queryStringParameters") or {}
    rows = _rows()

    # Metadatos: dimensiones + disponibilidad para armar los filtros del frontend.
    if qs.get("meta"):
        def uniq(col):
            return sorted({r[col] for r in rows if r.get(col)})
        # disponibles[distrito][anio] = [cargos con eleccion GENERAL]
        disp = {}
        for r in rows:
            if r.get("eleccion_tipo") != "GENERAL":
                continue
            disp.setdefault(r["municipio"], {}).setdefault(r["anio"], set()).add(r["cargo_nombre"])
        disp = {d: {a: sorted(cs) for a, cs in ys.items()} for d, ys in disp.items()}
        return _resp(200, {
            "distritos": uniq("municipio"),
            "anios": sorted({r["anio"] for r in rows if r.get("anio")}, key=lambda x: int(x)),
            "cargos": uniq("cargo_nombre"),
            "tipos": uniq("eleccion_tipo"),
            "disponibles": disp,
        })

    distrito = (qs.get("distrito") or "").lower()
    anio = str(qs.get("anio") or "")
    cargo = (qs.get("cargo") or "").upper()
    tipo = (qs.get("tipo") or "GENERAL").upper()
    if not (distrito and anio and cargo):
        return _resp(400, {"error": "faltan parametros: distrito, anio, cargo (tipo opcional, default GENERAL)"})

    sel = [
        r for r in rows
        if r["municipio"] == distrito and r["anio"] == anio
        and r["cargo_nombre"] == cargo and r["eleccion_tipo"] == tipo
    ]
    if not sel:
        return _resp(404, {"error": "sin datos", "filtro": {"distrito": distrito, "anio": anio, "cargo": cargo, "tipo": tipo}})

    circuitos = {}
    for r in sel:
        pct = _num(r["porcentaje"])
        if pct is None:
            continue  # BLANCO/NULO/etc: voto no positivo, fuera del mapa y del %
        cid = r["circuito_id"]
        c = circuitos.setdefault(cid, {
            "circuito_id": cid,
            "circuito_padre": r.get("circuito_padre") or None,
            "granularidad": r.get("granularidad"),
            "ganador": None,
            "composicion": [],
        })
        item = {
            "agrupacion": r["agrupacion_nombre"],
            "votos": int(_num(r["votos"]) or 0),
            "porcentaje": pct,
            "gana": str(r.get("gana", "")).lower() == "true",
        }
        c["composicion"].append(item)
        if item["gana"]:
            c["ganador"] = item

    for c in circuitos.values():
        c["composicion"].sort(key=lambda i: i["votos"], reverse=True)

    return _resp(200, {
        "filtro": {"distrito": distrito, "anio": anio, "cargo": cargo, "tipo": tipo},
        "granularidad": sel[0].get("granularidad"),
        "circuitos": list(circuitos.values()),
    })
