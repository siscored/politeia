"""Contrato de datos POLITEIA (alineado a procesados/consolidado.csv y vista_mapa.csv).

Fuente de verdad del esquema: docs/02_modelo_de_datos.md.
Los tipos acá deben coincidir con lo que produce el ETL. Si cambia el CSV, se
actualiza esto Y docs/02, y se registra en docs/DECISIONES.md.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

AMBITOS = {"nacional", "provincial", "municipal"}
ELECCION_TIPOS = {"paso", "generales", "segunda_vuelta", "interna"}
VOTOS_TIPOS = {"positivo", "nulo", "blanco", "impugnado", "recurrido", "comando"}
CARGOS_EJECUTIVOS = {"presidente", "gobernador", "intendente"}


@dataclass
class FilaConsolidado:
    """Una fila de procesados/consolidado.csv (formato largo, nivel mesa)."""
    fuente: str                 # "dine" | "junta"
    municipio: str              # "Pilar" | "San Fernando"
    anio: int                   # columna 'año' en el CSV
    eleccion_tipo: str
    cargo_id: str
    cargo_nombre: str
    distrito_id: str
    seccion_id: str
    seccion_nombre: str
    circuito_id: str            # join con GeoJSON CNE
    mesa_id: str
    mesa_tipo: str
    mesa_electores: int
    agrupacion_id: str          # normalizada (ver core/agrupaciones/diccionario.csv)
    agrupacion_nombre: str      # nombre segun fuente
    lista_numero: str
    lista_nombre: str
    votos_tipo: str
    votos_cantidad: int
    # --- DEUDA de contrato (agregar en proximo ETL) ---
    agrupacion_raw: Optional[str] = None    # texto ORIGINAL, nunca pisar
    ambito: Optional[str] = None            # derivar de cargo/fuente
    fuente_url: Optional[str] = None
    fecha_extraccion: Optional[str] = None
    hash_registro: Optional[str] = None


@dataclass
class FilaVistaMapa:
    """Una fila de procesados/vista_mapa.csv (agregado para el mapa)."""
    municipio: str
    anio: int
    eleccion_tipo: str
    cargo_nombre: str
    circuito_id: str
    agrupacion_nombre: str
    votos: int
    porcentaje: float
    gana: bool
    granularidad: str           # "circuito" | "municipio"
    circuito_padre: Optional[str] = None    # herencia pre/post cambio 2019


def es_ejecutivo(cargo_nombre: str) -> bool:
    return cargo_nombre.strip().lower() in CARGOS_EJECUTIVOS
