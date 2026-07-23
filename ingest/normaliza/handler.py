"""
politeia-normaliza-familias — paso 1 del pipeline `politeia-pipeline-datos`.

Lee la vista_mapa BASE desde S3 (`_source/`), le agrega/recalcula la columna
`familia` con el criterio canónico de `core/agrupaciones/familias.py` (espejo
de `web/src/families.js`) y escribe el resultado en `_staging/`.

NO publica a la key live: eso lo hace el pipeline recién si la validación pasa
(patrón "validar en staging antes de publicar"). Idempotente: si `familia` ya
venía en la entrada, la recalcula. Sin pandas — csv + core (layer politeia-core)
+ boto3 (runtime). Espejo Lambda del CLI `enriquecer_vista_mapa.py`: ambos
resuelven la familia con `familia_de`, así no se duplica el criterio.
"""
import csv
import io
import os

import boto3

from core.agrupaciones.familias import familia_de

s3 = boto3.client("s3")
BUCKET = os.environ["DATA_BUCKET"]
SOURCE_KEY = os.environ["SOURCE_KEY"]
STAGING_KEY = os.environ["STAGING_KEY"]


def lambda_handler(event, context):
    obj = s3.get_object(Bucket=BUCKET, Key=SOURCE_KEY)
    text = obj["Body"].read().decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(text)))
    if not rows:
        raise RuntimeError(f"entrada vacía: s3://{BUCKET}/{SOURCE_KEY}")

    # `familia` va al final; si ya venía, se recalcula (idempotente).
    campos = [c for c in rows[0].keys() if c != "familia"] + ["familia"]
    conteo: dict[str, int] = {}
    for r in rows:
        fam = familia_de(r.get("agrupacion_nombre"))
        r["familia"] = fam
        conteo[fam] = conteo.get(fam, 0) + 1

    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=campos)
    w.writeheader()
    w.writerows(rows)
    s3.put_object(
        Bucket=BUCKET,
        Key=STAGING_KEY,
        Body=buf.getvalue().encode("utf-8"),
        ContentType="text/csv; charset=utf-8",
    )

    # Este dict es el input del paso Valida (el pipeline lo pasa tal cual).
    return {
        "n_filas": len(rows),
        "familias": conteo,
        "staging": f"s3://{BUCKET}/{STAGING_KEY}",
    }
