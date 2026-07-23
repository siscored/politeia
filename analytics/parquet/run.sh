#!/usr/bin/env bash
# Ejecuta un .sql en Athena (workgroup politeia, base politeia_electoral),
# una sentencia por vez (separadas por ';'), esperando cada una.
#
# Uso:
#   AWS_PROFILE=idetec ./run.sh 01_create_consolidado_parquet.sql
#   AWS_PROFILE=idetec ./run.sh 02_load_consolidado_parquet.sql
#   AWS_PROFILE=idetec ./run.sh 03_validate.sql
#
# Requiere que el stack DataStack esté desplegado (base Glue + workgroup + bucket
# de resultados). El bucket de datos y las claves están fijos en los .sql.
set -euo pipefail

: "${AWS_PROFILE:=idetec}"
export AWS_PROFILE
DB=politeia_electoral
WG=politeia

run_one() {
  local sql="$1"
  [[ -z "${sql//[[:space:]]/}" ]] && return 0   # saltar vacíos
  echo "── ejecutando: $(echo "$sql" | tr '\n' ' ' | cut -c1-80)…"
  local qid
  qid=$(aws athena start-query-execution --work-group "$WG" \
    --query-execution-context "Database=$DB" \
    --query-string "$sql" --query 'QueryExecutionId' --output text)
  while :; do
    local st
    st=$(aws athena get-query-execution --query-execution-id "$qid" \
      --query 'QueryExecution.Status.State' --output text)
    case "$st" in
      SUCCEEDED) break;;
      FAILED|CANCELLED)
        echo "  $st: $(aws athena get-query-execution --query-execution-id "$qid" \
          --query 'QueryExecution.Status.StateChangeReason' --output text)" >&2
        return 1;;
    esac
    sleep 2
  done
  # Muestra resultados (útil para 03_validate); para DDL/INSERT es vacío.
  aws athena get-query-results --query-execution-id "$qid" \
    --query 'ResultSet.Rows[].Data[].VarCharValue' --output text 2>/dev/null || true
  echo "  scanned: $(aws athena get-query-execution --query-execution-id "$qid" \
    --query 'QueryExecution.Statistics.DataScannedInBytes' --output text) bytes"
}

file="${1:?uso: ./run.sh <archivo.sql>}"
# Separa por ';' respetando que los .sql de acá no usan ';' dentro de literales.
buf=""
while IFS= read -r line || [[ -n "$line" ]]; do
  case "$line" in \#*|--*) continue;; esac   # saltar comentarios de línea
  buf+="$line"$'\n'
  if [[ "$line" == *';'* ]]; then
    run_one "${buf%;*}"
    buf=""
  fi
done < "$file"
