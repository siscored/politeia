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

# ---------------------------------------------------------------------------
# Calendario electoral 1983-2025 para Pilar y San Fernando (ambos 1ª Sección
# Electoral PBA). Claves = cargo_nombre canónico del dataset (mayúsculas).
# Un año ausente acá = NO hubo esa elección (su falta en los datos no es hueco).
#
# Reglas que lo generan (validado contra el meta del API en vivo, 2026-07-24):
# - Legislatura PBA renueva por mitades; a la 1ª Sección le tocan SENADORES_PROV
#   en 1985+4k (…2017, 2021, 2025) y DIPUTADOS_PROV en 1987+4k (…2019, 2023).
#   1983 eligió la legislatura completa (ambas cámaras).
# - SENADORES_NAC: voto popular recién desde 2001 (Senado completo); luego la
#   clase PBA: 2005, 2011, 2017, 2023. Pre-2001 era elección indirecta → no es
#   hueco de datos.
# - CONCEJALES: renovación por mitades cada 2 años → todos los años impares.
# - MERCOSUR: única elección directa de Parlasur fue 2015 (después se suspendió).
#   Ojo: el dataset dice tener 2023 — anomalía a verificar, ver check "inesperado".
ANIOS_ELECCION = {
    "PRESIDENTE":     [1983, 1989, 1995, 1999, 2003, 2007, 2011, 2015, 2019, 2023],
    "GOBERNADOR":     [1983, 1987, 1991, 1995, 1999, 2003, 2007, 2011, 2015, 2019, 2023],
    "INTENDENTE":     [1983, 1987, 1991, 1995, 1999, 2003, 2007, 2011, 2015, 2019, 2023],
    "DIPUTADOS_NAC":  list(range(1983, 2026, 2)),
    "SENADORES_NAC":  [2001, 2005, 2011, 2017, 2023],
    "DIPUTADOS_PROV": [1983, 1987, 1991, 1995, 1999, 2003, 2007, 2011, 2015, 2019, 2023],
    "SENADORES_PROV": [1983, 1985, 1989, 1993, 1997, 2001, 2005, 2009, 2013, 2017, 2021, 2025],
    "CONCEJALES":     list(range(1983, 2026, 2)),
    "MERCOSUR_NAC":   [2015],
    "MERCOSUR_REG":   [2015],
}

# Dimensión eleccion_tipo (GENERAL es lo que cubre ANIOS_ELECCION):
# - PASO nacionales: 2011-2023; suspendidas en 2025. Sept-2025 (provincial) fue sin PASO.
# - Segunda vuelta presidencial realizada: 2015 y 2023 (la de 2003 se convocó y
#   se canceló: su ausencia no es hueco).
ANIOS_PASO = [2011, 2013, 2015, 2017, 2019, 2021, 2023]
ANIOS_SEGUNDA_VUELTA = {"PRESIDENTE": [2015, 2023]}


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
    """Cruza el dataset contra ANIOS_ELECCION por (municipio, cargo, año).

    Devuelve dos clases de hallazgos:
      - "hueco: ..."      → hubo elección según el calendario y no hay datos.
      - "inesperado: ..." → hay datos en un año sin elección según el calendario
                            (p.ej. MERCOSUR 2023): o el calendario está mal o el
                            dato está mal etiquetado. Ambos ameritan revisión.

    Acepta consolidado y vista_mapa reales: la columna de año puede llamarse
    "anio" o "año", y cargo_nombre se compara en mayúsculas (valores canónicos
    del ETL: PRESIDENTE, DIPUTADOS_NAC, ...).
    """
    anio_col = "anio" if "anio" in df.columns else "año"
    if anio_col not in df.columns or "cargo_nombre" not in df.columns:
        return ["continuidad_temporal: faltan columnas cargo_nombre/año"]

    cargos = df["cargo_nombre"].astype(str).str.strip().str.upper()
    anios = pd.to_numeric(df[anio_col], errors="coerce")
    munis = (df["municipio"].astype(str).str.strip().str.lower()
             if "municipio" in df.columns
             else pd.Series(["(todos)"] * len(df), index=df.index))

    presentes = {(m, c, int(a)) for m, c, a in zip(munis, cargos, anios)
                 if pd.notna(a)}

    out = []
    for muni in sorted({m for m, _, _ in presentes}):
        for cargo, esperados in ANIOS_ELECCION.items():
            for a in esperados:
                if (muni, cargo, a) not in presentes:
                    out.append(f"hueco: falta {cargo} {a} en {muni}")
    for muni, cargo, a in sorted(presentes):
        if cargo in ANIOS_ELECCION and a not in ANIOS_ELECCION[cargo]:
            out.append(f"inesperado: {cargo} {a} en {muni} sin elección en calendario")
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
