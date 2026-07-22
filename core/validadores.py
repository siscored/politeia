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


# ---------------------------------------------------------------------------
# Validación sobre vista_mapa.csv (capa de consumo). Distinta de consolidado:
# columnas municipio,año,eleccion_tipo,cargo_nombre,circuito_id,agrupacion_nombre,
# votos,porcentaje,gana,granularidad,circuito_padre[,familia].
# Devuelve (duros, blandos): 'duros' debe cortar el CI; 'blandos' solo se reportan.
# ---------------------------------------------------------------------------
_NO_PARTIDO = {"BLANCO", "NULO", "RECURRIDO", "IMPUGNADO", "COMANDO"}
_CLAVE_VM = ["año", "eleccion_tipo", "cargo_nombre", "municipio",
             "circuito_id", "agrupacion_nombre"]


def _unidad_vm(df: pd.DataFrame) -> pd.Series:
    return (df["año"].astype(str) + "|" + df["eleccion_tipo"].astype(str) + "|"
            + df["cargo_nombre"].astype(str) + "|" + df["municipio"].astype(str)
            + "|" + df["circuito_id"].astype(str))


def validar_vista_mapa(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    duros: list[str] = []
    blandos: list[str] = []

    # 1) Duplicados por clave (error duro)
    claves = [c for c in _CLAVE_VM if c in df.columns]
    d = df[df.duplicated(claves, keep=False)]
    if not d.empty:
        duros.append(f"duplicados: {len(d)} filas por {claves}")

    # 2) % fuera de [0,100] (error duro)
    pct = pd.to_numeric(df.get("porcentaje"), errors="coerce")
    malos = df[(pct < 0) | (pct > 100)]
    if not malos.empty:
        duros.append(f"porcentaje fuera de [0,100]: {len(malos)} filas")

    # 3) Suma de % por unidad ~100 (blando: puede haber redondeos)
    tmp = df.assign(_u=_unidad_vm(df), _p=pct)
    sumas = tmp.dropna(subset=["_p"]).groupby("_u")["_p"].sum()
    fuera = sumas[(sumas < 95) | (sumas > 105)]
    if len(fuera):
        blandos.append(f"Σ% fuera de [95,105] en {len(fuera)}/{len(sumas)} unidades")

    # 4) Flag 'gana': exactamente 1 por unidad y = máximo de votos
    votos = pd.to_numeric(df.get("votos"), errors="coerce")
    tmp = df.assign(_u=_unidad_vm(df), _v=votos, _g=df["gana"].astype(str) == "True")
    sin = mult = 0
    for _u, sub in tmp.groupby("_u"):
        ng = int(sub["_g"].sum())
        if ng == 0:
            sin += 1
        elif ng > 1:
            mult += 1
    if sin:
        duros.append(f"unidades sin ganador: {sin}")
    if mult:
        blandos.append(f"unidades con >1 ganador (empates): {mult}")

    # 5) Linaje de familia: cuántas caen en 'otras' (blando, informativo)
    if "familia" in df.columns:
        from core.agrupaciones.familias import FAMILIAS_VALIDAS
        invalidas = set(df["familia"].dropna().astype(str)) - FAMILIAS_VALIDAS
        if invalidas:
            duros.append(f"familia con valores no válidos: {sorted(invalidas)[:10]}")
        otras = df[df["familia"] == "otras"]["agrupacion_nombre"].nunique()
        blandos.append(f"agrupaciones en 'otras' (sin familia clara): {otras}")

    return duros, blandos


if __name__ == "__main__":
    # CLI para el CI:  python core/validadores.py <vista_mapa.csv>
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    ruta = sys.argv[1] if len(sys.argv) > 1 else "vista_mapa.csv"
    df = pd.read_csv(ruta, dtype=str, keep_default_na=False)
    duros, blandos = validar_vista_mapa(df)
    print(f"== Validación de {ruta} ({len(df)} filas) ==")
    for b in blandos:
        print(f"  [reporta] {b}")
    if duros:
        print("ERRORES DUROS:")
        for x in duros:
            print(f"  [FALLA] {x}")
        sys.exit(1)
    print("OK · sin errores duros.")
