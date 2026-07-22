"""ETL reproducible: agrega la columna `familia` a vista_mapa.csv.

Cierra parte de la deuda de docs/02 §normalización (llevar la familia al dataset
curado en vez de resolverla por keyword en el front) y aporta al HUECO #5
(reproducibilidad: este script regenera la salida desde la entrada, idempotente).

Uso:
    python ingest/normaliza/enriquecer_vista_mapa.py entrada.csv salida.csv

Resuelve `familia` con el mismo criterio canónico que el front
(core/agrupaciones/familias.py, espejo de web/src/families.js). Idempotente:
si la columna ya existe, la recalcula.
"""
from __future__ import annotations
import csv
import os
import sys

# Permite correrlo desde la raíz del repo sin instalar el paquete.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from core.agrupaciones.familias import familia_de  # noqa: E402


def enriquecer(entrada: str, salida: str) -> tuple[int, dict[str, int]]:
    with open(entrada, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise SystemExit(f"entrada vacía: {entrada}")

    campos = [c for c in rows[0].keys() if c != "familia"] + ["familia"]
    conteo: dict[str, int] = {}
    for r in rows:
        fam = familia_de(r.get("agrupacion_nombre"))
        r["familia"] = fam
        conteo[fam] = conteo.get(fam, 0) + 1

    with open(salida, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(rows)
    return len(rows), conteo


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("uso: enriquecer_vista_mapa.py <entrada.csv> <salida.csv>")
    n, conteo = enriquecer(sys.argv[1], sys.argv[2])
    print(f"OK · {n} filas → {sys.argv[2]}")
    total = sum(conteo.values())
    for fam, c in sorted(conteo.items(), key=lambda x: -x[1]):
        print(f"  {fam:18} {c:>6} filas ({100*c/total:4.1f}%)")
