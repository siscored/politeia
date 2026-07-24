# -*- coding: utf-8 -*-
"""
ETL: consolida los CSVs crudos de DINE en dos salidas:

  datos-electorales/consolidado.csv   -> tabla de hechos (nivel mesa x agrupacion)
  datos-electorales/vista_mapa.csv    -> agregado por circuito x eleccion x agrupacion
                                         (lo que consume el mapa de la app)

Uso:
    pip install pandas
    python etl_consolidar.py
"""

import glob
import os

import pandas as pd

RAW = os.path.join("datos-electorales", "raw", "dine")
RAW_JUNTA = os.path.join("datos-electorales", "raw", "junta_pba")

CARGOS_JUNTA = {
    "04": "GOBERNADOR", "06": "SENADORES_PROV", "08": "DIPUTADOS_PROV",
    "10": "INTENDENTE", "11": "CONCEJALES",
}
OUT_CONSOLIDADO = os.path.join("datos-electorales", "consolidado.csv")
OUT_VISTA = os.path.join("datos-electorales", "vista_mapa.csv")

COLUMNAS = [
    "fuente", "municipio", "año", "eleccion_tipo", "cargo_id", "cargo_nombre",
    "distrito_id", "seccion_id", "seccion_nombre", "circuito_id",
    "mesa_id", "mesa_tipo", "mesa_electores",
    "agrupacion_id", "agrupacion_nombre", "lista_numero", "lista_nombre",
    "votos_tipo", "votos_cantidad",
]

NORMALIZA_ELECCION = {
    "GENERAL": "GENERAL", "GENERALES": "GENERAL",
    "PASO": "PASO", "PRIMARIA": "PASO", "PRIMARIAS": "PASO",
    "SEGUNDA VUELTA": "SEGUNDA_VUELTA", "SEGUNDA_VUELTA": "SEGUNDA_VUELTA",
    "BALLOTAGE": "SEGUNDA_VUELTA", "BALOTAJE": "SEGUNDA_VUELTA",
}

NORMALIZA_VOTOS = {
    "POSITIVO": "POSITIVO", "POSITIVOS": "POSITIVO",
    "EN BLANCO": "BLANCO", "BLANCOS": "BLANCO", "BLANCO": "BLANCO",
    "NULO": "NULO", "NULOS": "NULO",
    "RECURRIDO": "RECURRIDO", "RECURRIDOS": "RECURRIDO",
    "IMPUGNADO": "IMPUGNADO", "IMPUGNADOS": "IMPUGNADO",
    "COMANDO": "COMANDO",
}

NORMALIZA_CARGO = {
    "PRESIDENTE/A": "PRESIDENTE", "PRESIDENTE Y VICE": "PRESIDENTE",
    "GOBERNADOR/A": "GOBERNADOR", "GOBERNADOR Y VICE": "GOBERNADOR",
    "INTENDENTE/A": "INTENDENTE",
    "SENADORES/AS NACIONALES": "SENADORES_NAC", "SENADOR/A NACIONAL": "SENADORES_NAC",
    "SENADOR NACIONAL": "SENADORES_NAC", "SENADORES NACIONALES": "SENADORES_NAC",
    "DIPUTADOS/AS NACIONALES": "DIPUTADOS_NAC", "DIPUTADO/A NACIONAL": "DIPUTADOS_NAC",
    "DIPUTADO NACIONAL": "DIPUTADOS_NAC", "DIPUTADOS NACIONALES": "DIPUTADOS_NAC",
    "SENADORES/AS PROVINCIALES": "SENADORES_PROV", "SENADOR PROVINCIAL": "SENADORES_PROV",
    "SENADORES PROVINCIALES": "SENADORES_PROV",
    "DIPUTADOS/AS PROVINCIALES - DIPUTADOS/AS DE LA CIUDAD": "DIPUTADOS_PROV",
    "DIPUTADO PROVINCIAL": "DIPUTADOS_PROV", "DIPUTADOS PROVINCIALES": "DIPUTADOS_PROV",
    "INTENDENTE": "INTENDENTE",
    "CONCEJAL/A - MIEMBROS DE LA JUNTA": "CONCEJALES", "CONCEJALES": "CONCEJALES",
    "CONCEJAL": "CONCEJALES",
    "PARLAMENTO MERCOSUR NACIONAL": "MERCOSUR_NAC",
    "PARLASUR DISTRITO NACIONAL": "MERCOSUR_NAC",
    "PARLAMENTARIOS MERCOSUR NACIONALES": "MERCOSUR_NAC",
    "PARLAMENTO MERCOSUR REGIONAL": "MERCOSUR_REG",
    "PARLASUR DISTRITO REGIONAL": "MERCOSUR_REG",
    "PARLAMENTARIOS MERCOSUR PROVINCIALES": "MERCOSUR_REG",
    "CONCEJALES/AS": "CONCEJALES",
    "DIPUTADOS/AS PROVINCIALES": "DIPUTADOS_PROV",
    "SENADORES/AS PROVINCIALES ": "SENADORES_PROV",
}


def leer_archivo(ruta):
    municipio = os.path.basename(os.path.dirname(ruta))
    fuente = os.path.basename(os.path.dirname(os.path.dirname(ruta)))
    df = pd.read_csv(ruta, dtype=str)
    df.columns = [c.strip().lower() for c in df.columns]  # Año -> año
    for col in COLUMNAS:
        if col not in df.columns:
            df[col] = None
    df["municipio"] = municipio
    df["fuente"] = fuente
    # limpieza de strings: espacios colgantes en ids y nombres
    for col in ["circuito_id", "agrupacion_nombre", "agrupacion_id",
                "cargo_nombre", "eleccion_tipo", "votos_tipo", "seccion_nombre"]:
        df[col] = df[col].astype(str).str.strip()
    df["eleccion_tipo"] = df["eleccion_tipo"].map(
        lambda v: NORMALIZA_ELECCION.get(v.upper(), v.upper()))
    df["cargo_nombre"] = df["cargo_nombre"].map(
        lambda v: NORMALIZA_CARGO.get(v.upper().strip(), v.upper().strip()))
    df["votos_tipo"] = df["votos_tipo"].map(
        lambda v: NORMALIZA_VOTOS.get(v.upper(), v.upper()))
    # circuito canonico: '0768', '00768' y '000768' son el mismo circuito.
    # regla: quitar ceros a la izquierda y rellenar a 5 ('000768'->'00768', '00768A'->'0768A')
    df["circuito_id"] = df["circuito_id"].str.upper().str.lstrip("0").str.zfill(5)
    # 'undefined' en votos no positivos -> vacio
    df.loc[df["agrupacion_nombre"].isin(["undefined", "nan"]), "agrupacion_nombre"] = ""
    df.loc[df["agrupacion_id"].isin(["undefined", "nan"]), "agrupacion_id"] = ""
    df["votos_cantidad"] = pd.to_numeric(df["votos_cantidad"], errors="coerce").fillna(0).astype(int)
    df["mesa_electores"] = pd.to_numeric(df["mesa_electores"], errors="coerce")
    return df[COLUMNAS]


def leer_junta(ruta):
    """CSV de la Junta Electoral PBA (nivel municipio, sin circuito ni mesa)."""
    municipio = os.path.basename(os.path.dirname(ruta))
    j = pd.read_csv(ruta, sep=";", dtype=str)
    df = pd.DataFrame()
    df["año"] = j["eleccion"].str.strip()
    df["eleccion_tipo"] = "GENERAL"
    df["cargo_id"] = j["cargo_id"].str.strip()
    df["cargo_nombre"] = df["cargo_id"].map(CARGOS_JUNTA).fillna(
        j["cargo"].fillna("").str.strip().str.upper())
    df["distrito_id"] = "2"
    df["seccion_id"] = j["distrito_id"].str.lstrip("0")
    df["seccion_nombre"] = j["distrito"].str.strip().str.title()
    df["agrupacion_id"] = j["lista_id"].str.strip()
    lista = j["lista"].str.replace(r"\s+", " ", regex=True).str.strip()
    es_blanco = df["agrupacion_id"] == "9996"
    df["agrupacion_nombre"] = lista.where(~es_blanco, "")
    df["votos_tipo"] = "POSITIVO"
    df.loc[es_blanco, "votos_tipo"] = "BLANCO"
    df["votos_cantidad"] = (j["votos"].str.replace(".", "", regex=False)
                            .pipe(pd.to_numeric, errors="coerce").fillna(0).astype(int))
    df["municipio"] = municipio
    df["fuente"] = "junta_pba"
    for col in COLUMNAS:
        if col not in df.columns:
            df[col] = None
    return df[COLUMNAS]


def main():
    archivos = sorted(glob.glob(os.path.join(RAW, "*", "*.csv")))
    junta = sorted(glob.glob(os.path.join(RAW_JUNTA, "*", "*.csv")))
    print(f"leyendo {len(archivos)} archivos DINE + {len(junta)} Junta PBA...")
    partes = [leer_archivo(f) for f in archivos] + [leer_junta(f) for f in junta]
    df = pd.concat(partes, ignore_index=True)
    df.to_csv(OUT_CONSOLIDADO, index=False, encoding="utf-8")
    print(f"consolidado: {len(df):,} filas -> {OUT_CONSOLIDADO}")

    # --- vista_mapa: agregado por circuito (solo filas con circuito, i.e. DINE) ---
    con_circuito = df[df["circuito_id"].notna()]
    pos = con_circuito[con_circuito["votos_tipo"] == "POSITIVO"]
    g = (pos.groupby(["municipio", "año", "eleccion_tipo", "cargo_nombre",
                      "circuito_id", "agrupacion_nombre"], as_index=False)
            .agg(votos=("votos_cantidad", "sum")))
    tot = (g.groupby(["municipio", "año", "eleccion_tipo", "cargo_nombre",
                      "circuito_id"], as_index=False)
             .agg(votos_positivos_circuito=("votos", "sum")))
    g = g.merge(tot, on=["municipio", "año", "eleccion_tipo", "cargo_nombre", "circuito_id"])
    g["porcentaje"] = (100 * g["votos"] / g["votos_positivos_circuito"]).round(2)
    g["gana"] = g.groupby(["municipio", "año", "eleccion_tipo", "cargo_nombre",
                           "circuito_id"])["votos"].transform("max") == g["votos"]

    # votos no positivos por circuito (blanco/nulo/etc) para tener participacion completa
    otros = (con_circuito[con_circuito["votos_tipo"] != "POSITIVO"]
             .groupby(["municipio", "año", "eleccion_tipo", "cargo_nombre",
                       "circuito_id", "votos_tipo"], as_index=False)
             .agg(votos=("votos_cantidad", "sum")))
    otros = otros.rename(columns={"votos_tipo": "agrupacion_nombre"})
    otros["porcentaje"] = None
    otros["gana"] = False

    vista = pd.concat([g.drop(columns=["votos_positivos_circuito"]), otros],
                      ignore_index=True)
    vista["granularidad"] = "circuito"
    # circuito_padre: estructura pre-2019 (0768A/B/C... hijos de 00768).
    # Para años viejos el mapa pinta cada poligono actual con el valor de su padre.
    vista["circuito_padre"] = (vista["circuito_id"].str.replace(r"[A-Z]$", "", regex=True)
                               .str.lstrip("0").str.zfill(5))

    # fallback municipio: combos sin datos por circuito (ej. sept 2025, 2003-2009)
    # se agregan desde la Junta con granularidad='municipio'
    j = df[df["fuente"] == "junta_pba"]
    claves_circ = set(map(tuple, vista[["municipio", "año", "eleccion_tipo",
                                        "cargo_nombre"]].drop_duplicates().values))
    jg = (j.groupby(["municipio", "año", "eleccion_tipo", "cargo_nombre",
                     "votos_tipo", "agrupacion_nombre"], as_index=False)
            .agg(votos=("votos_cantidad", "sum")))
    jg = jg[~jg[["municipio", "año", "eleccion_tipo", "cargo_nombre"]]
            .apply(tuple, axis=1).isin(claves_circ)]
    if len(jg):
        pos_m = jg[jg.votos_tipo == "POSITIVO"].copy()
        tot_m = (pos_m.groupby(["municipio", "año", "eleccion_tipo", "cargo_nombre"])
                 ["votos"].transform("sum"))
        pos_m["porcentaje"] = (100 * pos_m["votos"] / tot_m).round(2)
        pos_m["gana"] = pos_m.groupby(["municipio", "año", "eleccion_tipo",
                                       "cargo_nombre"])["votos"].transform("max") == pos_m["votos"]
        otros_m = jg[jg.votos_tipo != "POSITIVO"].copy()
        otros_m["agrupacion_nombre"] = otros_m["votos_tipo"]
        otros_m["porcentaje"] = None
        otros_m["gana"] = False
        fallback = pd.concat([pos_m, otros_m], ignore_index=True).drop(columns=["votos_tipo"])
        fallback["circuito_id"] = ""
        fallback["circuito_padre"] = ""
        fallback["granularidad"] = "municipio"
        vista = pd.concat([vista, fallback], ignore_index=True)

    vista = vista.sort_values(["municipio", "año", "eleccion_tipo", "cargo_nombre",
                               "circuito_id", "votos"], ascending=[True]*5+[False])
    vista.to_csv(OUT_VISTA, index=False, encoding="utf-8")
    print(f"vista_mapa: {len(vista):,} filas -> {OUT_VISTA}")

    # sanity check
    chk = vista[(vista.municipio == "pilar") & (vista["año"] == "2023") &
                (vista.eleccion_tipo == "GENERAL") & (vista.cargo_nombre == "PRESIDENTE")]
    print("\ncheck Pilar 2023 Presidente (suma por agrupacion):")
    print(chk[chk.porcentaje.notna()].groupby("agrupacion_nombre")["votos"]
          .sum().sort_values(ascending=False).head(5).to_string())


if __name__ == "__main__":
    main()
