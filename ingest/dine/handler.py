"""
politeia-ingest-dine

Baja UN recurso de DINE (una URL) y lo guarda CRUDO en
    s3://<bucket>/electoral/raw/dine/<municipio>/<nombre_archivo>
junto con su linaje (fuente_url, fecha_extraccion, hash).

Diseno (segun CLAUDE.md):
- raw-first : se persiste exactamente lo que baja, ANTES de transformar.
- idempotente: misma entrada -> misma key S3 (re-correr no duplica).
- linaje    : se guardan fuente_url, fecha_extraccion y sha256.
- sin PII   : solo agregados publicos por unidad.

Sin dependencias externas: usa urllib (stdlib) + boto3 (ya viene en el
runtime de Lambda). Asi el paquete no necesita bundling y despliega directo.

Evento de invocacion esperado (JSON):
{
  "fuente_url": "https://.../resultado.csv",   # obligatorio
  "municipio":  "pilar",                        # opcional (default: sin_municipio)
  "nombre_archivo": "2025_generales_dip_nac.csv" # obligatorio
}
"""
import os
import json
import hashlib
import urllib.request
from datetime import datetime, timezone

import boto3

s3 = boto3.client("s3")

BUCKET = os.environ["DATA_BUCKET"]
RAW_PREFIX = os.environ.get("RAW_PREFIX", "electoral/raw/dine")


def lambda_handler(event, context):
    # 1. Parametros de la corrida.
    url = event["fuente_url"]
    municipio = event.get("municipio", "sin_municipio")
    nombre = event["nombre_archivo"]

    # 2. Descargar el crudo.
    req = urllib.request.Request(url, headers={"User-Agent": "politeia-ingest/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        contenido = resp.read()

    # 3. Linaje: hash del contenido + timestamp de extraccion.
    sha256 = hashlib.sha256(contenido).hexdigest()
    ahora = datetime.now(timezone.utc).isoformat()

    # 4. Guardar el crudo en raw/dine/<municipio>/<nombre>.
    #    La metadata viaja pegada al objeto S3 (linaje minimo).
    key = f"{RAW_PREFIX}/{municipio}/{nombre}"
    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=contenido,
        Metadata={
            "fuente": "dine",
            "fuente-url": url,
            "fecha-extraccion": ahora,
            "sha256": sha256,
        },
    )

    # 5. Sidecar de linaje: un .meta.json legible al lado del crudo.
    meta = {
        "fuente": "dine",
        "fuente_url": url,
        "fecha_extraccion": ahora,
        "sha256": sha256,
        "bytes": len(contenido),
        "s3_key": key,
    }
    s3.put_object(
        Bucket=BUCKET,
        Key=key + ".meta.json",
        Body=json.dumps(meta, ensure_ascii=False, indent=2).encode("utf-8"),
        ContentType="application/json",
    )

    print(json.dumps({"ok": True, **meta}))
    return {"ok": True, **meta}
