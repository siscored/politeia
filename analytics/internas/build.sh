#!/usr/bin/env bash
# Genera procesados/vista_internas/vista_internas.csv desde Athena:
# corre vista_internas.sql y copia el resultado a la clave curada.
#
# Uso:  AWS_PROFILE=idetec ./build.sh
#
# Requiere DataStack desplegado y la tabla `consolidado_parquet` cargada (ver
# ../parquet/). No usa CTAS (el workgroup impone output location): corre el SELECT
# y copia su resultado a la clave curada.
set -euo pipefail
: "${AWS_PROFILE:=idetec}"; export AWS_PROFILE
B=electoral-data-851679891137
DB=politeia_electoral
WG=politeia
DEST="s3://$B/electoral/procesados/vista_internas/vista_internas.csv"
SQL_FILE="$(dirname "$0")/vista_internas.sql"

sql=$(grep -v -E '^\s*--' "$SQL_FILE")
qid=$(aws athena start-query-execution --work-group "$WG" \
  --query-execution-context "Database=$DB" --query-string "$sql" \
  --query 'QueryExecutionId' --output text)
[ -z "$qid" ] || [ "$qid" = None ] && { echo "start-query-execution falló" >&2; exit 1; }
while :; do
  st=$(aws athena get-query-execution --query-execution-id "$qid" \
    --query 'QueryExecution.Status.State' --output text)
  case "$st" in
    SUCCEEDED) break;;
    FAILED|CANCELLED)
      aws athena get-query-execution --query-execution-id "$qid" \
        --query 'QueryExecution.Status.StateChangeReason' --output text >&2
      exit 1;;
  esac; sleep 2
done
out=$(aws athena get-query-execution --query-execution-id "$qid" \
  --query 'QueryExecution.ResultConfiguration.OutputLocation' --output text)
aws s3 cp "$out" "$DEST"
echo "OK → $DEST"
