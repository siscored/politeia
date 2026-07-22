"""Resolución canónica agrupación cruda -> familia política.

Fuente de verdad en el plano de datos (Python). Es el ESPEJO de
`web/src/families.js`: mismo orden, mismos patrones, mismos colores. Cuando
`diccionario.csv` esté completo, este resolver puede pasar a leerlo primero y
caer al keyword-match solo para lo no mapeado.

Uso:
    from core.agrupaciones.familias import familia_de, FAMILIAS
    fam = familia_de("UNION POR LA PATRIA")   # -> "peronismo"

El ORDEN importa: gana el primer patrón que matchea (de específico a general),
para que, por ejemplo, "una" de ARI no caiga en massismo.
"""
from __future__ import annotations
import re

# (key, label, color, patrón). Mismo orden que web/src/families.js.
FAMILIAS = [
    ("no_partidario", "Blanco / nulo / s.d.", "#475569",
     r"^(en\s+)?(blanco|nulo|votos?\s+nulos?|recurrido|impugnado|comando)s?$"),
    ("cc_ari", "Coalición Cívica / ARI", "#db2777",
     r"coalici[oó]n\s*c[ií]vica|\bari\b|a\.?r\.?i\.?\b|afirm.*(rep|igualit)"),
    ("peronismo", "Peronismo / UxP", "#2563eb",
     r"uni[oó]n por la patria|frente de todos|para la victoria|unidad ciudadana|fuerza patria|jus?t[a-z]*ialista|frejupo|\bfpv\b|\buxp\b|patria grande|polo social para la victoria|nueva uni[oó]n ciudadana"),
    ("pj_federal", "Peronismo federal / centro", "#38bdf8",
     r"todos por buenos aires|principios y valores|compromiso federal|consenso federal|hacemos( por nuestro)?|vamos con vos|desarrollo social|udeso|unidad federalista|pa\.?u\.?fe|uni[oó]n popular|provincias unidas"),
    ("frentes_populares", "Frentes populares", "#0891b2",
     r"frente popular|frepobo|afeba|ac\.? federalista|federalista p\/? ?bs"),
    ("jxc", "Juntos por el Cambio", "#eab308",
     r"cambiemos|juntos|\bcambio\b|uni[oó]n pro\b|propuesta republicana|\bpro\b|republicano federal|macri"),
    ("lla", "La Libertad Avanza", "#7c3aed",
     r"libertad avanza|\blla\b|milei"),
    ("liberales", "Liberales", "#0d9488",
     r"avanza libertad|unidos por la libertad|libertad y (el trabajo|la dignidad)|celeste y blanc|\+\s*valores|centro democr|uced[eé]|\bunite\b|libertari|liber\.?ar|uni[oó]n liberal|uni[oó]n y libertad|uni[oó]n con fe"),
    ("massismo", "Massismo / F. Renovador", "#ea580c",
     r"renovador|massa|nueva alternativa|\buna\b|1\s?pa[ií]s|red x"),
    ("izquierda", "Frente de Izquierda", "#dc2626",
     r"izquierda|obrer[oa]|\bfit\b|trabajadores|socialis|\bmst\b|\bmas\b|\bpts\b|pol[ií]tica obrera"),
    ("progresismo", "Progresismo", "#84cc16",
     r"progresista|nuevo encuentro|frente grande|proyecto sur|libres del sur|acuerdo c[ií]vico|humanista ecologista|encuentro amplio"),
    ("ucr", "Radicalismo / UCR", "#06b6d4",
     r"radical|\bucr\b"),
    ("vecinalismo", "Vecinalismo local", "#b45309",
     r"vecinal|vecinos|san fernando|\bpilar\b|sumemos|acci[oó]n comunal|encuentro pilar|tiempo de vecinos"),
]

OTRAS = ("otras", "Otras fuerzas", "#94a3b8")

_COMPILADAS = [(key, re.compile(pat, re.IGNORECASE)) for key, _lbl, _c, pat in FAMILIAS]

# Metadatos por familia (label, color), incluyendo 'otras'.
META = {key: {"label": lbl, "color": c} for key, lbl, c, _pat in FAMILIAS}
META[OTRAS[0]] = {"label": OTRAS[1], "color": OTRAS[2]}

# Todas las keys válidas (para el chequeo de linaje en validadores).
FAMILIAS_VALIDAS = set(META.keys())


def familia_de(nombre: str | None) -> str:
    """Devuelve la key de familia para un nombre crudo de agrupación."""
    if not nombre:
        return OTRAS[0]
    for key, rx in _COMPILADAS:
        if rx.search(nombre):
            return key
    return OTRAS[0]
