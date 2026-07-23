"""
politeia-valida-dataset — paso 2 (gate de calidad) del pipeline `politeia-pipeline-datos`.

Lee la vista_mapa candidata desde `_staging/` y corre las validaciones de
`core/validadores.validar_vista_mapa` TAL CUAL (misma fuente de verdad que el
CLI local y que usaba el CI). pandas lo provee el layer gestionado
AWSSDKPandas-Python312; `core` viene del layer politeia-core.

Devuelve los hallazgos DUROS (cortan la publicación) y BLANDOS (se reportan).
El pipeline usa `ok` (== no hay duros) como compuerta del Choice: solo si es
True se copia `_staging/` → key live. Así una subida mala nunca llega a producción.
"""
import io
import os

import boto3
import pandas as pd

from core.validadores import validar_vista_mapa

s3 = boto3.client("s3")
BUCKET = os.environ["DATA_BUCKET"]
STAGING_KEY = os.environ["STAGING_KEY"]


def lambda_handler(event, context):
    obj = s3.get_object(Bucket=BUCKET, Key=STAGING_KEY)
    # Mismo criterio de lectura que el CLI: todo string, sin NaN mágicos.
    df = pd.read_csv(io.BytesIO(obj["Body"].read()), dtype=str, keep_default_na=False)
    duros, blandos = validar_vista_mapa(df)
    return {
        "ok": len(duros) == 0,
        "n_filas": int(len(df)),
        "duros": duros,
        "blandos": blandos,
        "staging": f"s3://{BUCKET}/{STAGING_KEY}",
    }
