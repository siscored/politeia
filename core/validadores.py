"""Controles de calidad minimos (CLAUDE.md §7). Correr en cada ETL.

Uso:
    import pandas as pd
    from core.validadores import correr_todos
    reporte = correr_todos(pd.read_csv("procesados/consolidado.csv"))
    print(reporte)   # y guardarlo en el repo

Trabaja sobre el DataFrame de consolidado.csv. Devuelve una lista de hallazgos;
lista vacia = todo OK. No corta la ejecucion: reporta.
"""
from __future__ import annotations
import pandas as pd

TOLERANCIA_PROVISORIO = 0.07  # DINE queda hasta ~7% bajo el definitivo: esperado

# Años con eleccion por cargo (para detectar huecos). Completar/verificar con fuentes.
ANIOS_ELECCION = {
    "presidente":        [1983,1989,1995,1999,2003,2007,2011,2015,2019,2023],
    "gobernador":        [1983,1987,1991,1995,1999,2003,2007,2011,2015,2019,2023],
    "intendente":        [1983,1987,1991,1995,1999,2003,2007,2011,2015,2019,2023],
    "diputado_nacional": list(range(1983, 2026, 2)),
}


def _unidad(df: pd.DataFrame) -> pd.Series:
    return (df["municipio"].astype(str) + "|" + df["circuito_id"].astype(str)
            + "|" + df["mesa_id"].astype(str))


def cierre_de_totales(df: pd.DataFrame) -> list[str]:
    out = []
    if "votos_tipo" not in df or "mesa_electores" not in df:
        return ["cierre_de_totales: faltan columnas votos_tipo/mesa_electores"]
    g = df.groupby([_unidad(df), "anio", "cargo_nombre"])
    for (u, anio, cargo), sub in g:
        emitidos = sub["votos_cantidad"].sum()
        electores = sub["mesa_electores"].max()
        if electores and emitidos > electores * (1 + TOLERANCIA_PROVISORIO):
            out.append(f"cierre: {u} {anio} {cargo} emitidos>{electores} electores")
    return out


def continuidad_temporal(df: pd.DataFrame) -> list[str]:
    out = []
    presentes = set(zip(df["cargo_nombre"], df["anio"]))
    for cargo, anios in ANIOS_ELECCION.items():
        for a in anios:
            if (cargo, a) not in presentes:
                out.append(f"hueco: falta {cargo} {a}")
    return out


def duplicados(df: pd.DataFrame) -> list[str]:
    claves = ["anio", "eleccion_tipo", "cargo_nombre", "municipio",
              "circuito_id", "mesa_id", "agrupacion_id", "votos_tipo"]
    claves = [c for c in claves if c in df.columns]
    d = df[df.duplicated(claves, keep=False)]
    return [] if d.empty else [f"duplicados: {len(d)} filas repetidas por {claves}"]


def sanidad_porcentajes(df: pd.DataFrame) -> list[str]:
    # aplica sobre vista_mapa (tiene 'porcentaje'); no sobre consolidado
    if "porcentaje" not in df.columns:
        return []
    malos = df[(df["porcentaje"] < 0) | (df["porcentaje"] > 100)]
    return [] if malos.empty else [f"porcentaje fuera de [0,100]: {len(malos)} filas"]


def linaje_agrupaciones(df: pd.DataFrame, diccionario_ids: set[str]) -> list[str]:
    if "agrupacion_id" not in df.columns or not diccionario_ids:
        return []
    faltan = set(df["agrupacion_id"].dropna().astype(str)) - diccionario_ids
    return [] if not faltan else [f"agrupaciones sin mapear: {sorted(faltan)[:20]}"]


def correr_todos(df: pd.DataFrame, diccionario_ids: set[str] | None = None) -> list[str]:
    rep = []
    rep += cierre_de_totales(df)
    rep += continuidad_temporal(df)
    rep += duplicados(df)
    rep += sanidad_porcentajes(df)
    rep += linaje_agrupaciones(df, diccionario_ids or set())
    return rep
