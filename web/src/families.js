// Normalización de agrupaciones -> familia política -> color.
// Taxonomía y colores validados con el usuario (2026-07-21) sobre las 236
// agrupaciones crudas del dataset (Pilar + San Fernando, 2003-2025).
// El ORDEN importa: gana el primer match. Va de específico a general para
// evitar falsos positivos (ej.: "una" de ARI no debe caer en massismo).
// Fuente de verdad canónica: core/agrupaciones/diccionario.csv (este archivo
// es el espejo por-keyword que colorea el mapa hasta que el ETL traiga la
// columna `familia` al dataset curado — ver docs/02 §normalización).
const FAM = [
  // No partidario primero: blanco/nulo/etc. nunca deben teñirse como fuerza.
  { key: "no_partidario", label: "Blanco / nulo / s.d.", c: "#475569",
    test: /^(en\s+)?(blanco|nulo|votos?\s+nulos?|recurrido|impugnado|comando)s?$/i },

  // Coalición Cívica / ARI (Carrió) — antes de massismo (por "una") y de ucr (por "cívica").
  { key: "cc_ari", label: "Coalición Cívica / ARI", c: "#db2777",
    test: /coalici[oó]n\s*c[ií]vica|\bari\b|a\.?r\.?i\.?\b|afirm.*(rep|igualit)/i },

  // Peronismo troncal (UxP) — patrones específicos, NO "todos" a secas.
  { key: "peronismo", label: "Peronismo / UxP", c: "#2563eb",
    test: /uni[oó]n por la patria|frente de todos|para la victoria|unidad ciudadana|fuerza patria|jus?t[a-z]*ialista|frejupo|\bfpv\b|\buxp\b|patria grande|polo social para la victoria|nueva uni[oó]n ciudadana/i },

  // Peronismo federal / centro (disidente) — incluye "Todos por BA" y "Principios y Valores".
  { key: "pj_federal", label: "Peronismo federal / centro", c: "#38bdf8",
    test: /todos por buenos aires|principios y valores|compromiso federal|consenso federal|hacemos( por nuestro)?|vamos con vos|desarrollo social|udeso|unidad federalista|pa\.?u\.?fe|uni[oó]n popular|provincias unidas/i },

  // Frentes populares / provinciales (peronismo-adyacente).
  { key: "frentes_populares", label: "Frentes populares", c: "#0891b2",
    test: /frente popular|frepobo|afeba|ac\.? federalista|federalista p\/? ?bs/i },

  // Juntos por el Cambio / PRO — amarillo (decisión del usuario).
  { key: "jxc", label: "Juntos por el Cambio", c: "#eab308",
    test: /cambiemos|juntos|\bcambio\b|uni[oó]n pro\b|propuesta republicana|\bpro\b|republicano federal|macri/i },

  // La Libertad Avanza (Milei) — violeta (color de marca real).
  { key: "lla", label: "La Libertad Avanza", c: "#7c3aed",
    test: /libertad avanza|\blla\b|milei/i },

  // Liberales / centro-derecha (Espert, UCeDé, Unite) — familia propia.
  { key: "liberales", label: "Liberales", c: "#0d9488",
    test: /avanza libertad|unidos por la libertad|libertad y (el trabajo|la dignidad)|celeste y blanc|\+\s*valores|centro democr|uced[eé]|\bunite\b|libertari|liber\.?ar|uni[oó]n liberal|uni[oó]n y libertad|uni[oó]n con fe/i },

  // Massismo / Frente Renovador — naranja.
  { key: "massismo", label: "Massismo / F. Renovador", c: "#ea580c",
    test: /renovador|massa|nueva alternativa|\buna\b|1\s?pa[ií]s|red x/i },

  // Frente de Izquierda (FIT) — rojo (antes violeta, chocaba con LLA).
  { key: "izquierda", label: "Frente de Izquierda", c: "#dc2626",
    test: /izquierda|obrer[oa]|\bfit\b|trabajadores|socialis|\bmst\b|\bmas\b|\bpts\b|pol[ií]tica obrera/i },

  // Progresismo / centro-izquierda (FAP, Nuevo Encuentro, GEN, Proyecto Sur).
  { key: "progresismo", label: "Progresismo", c: "#84cc16",
    test: /progresista|nuevo encuentro|frente grande|proyecto sur|libres del sur|acuerdo c[ií]vico|humanista ecologista|encuentro amplio/i },

  // Radicalismo standalone (casi todo migró a Cambiemos/JxC).
  { key: "ucr", label: "Radicalismo / UCR", c: "#06b6d4",
    test: /radical|\bucr\b/i },

  // Vecinalismo / local (sin alineación nacional). Último antes del default.
  { key: "vecinalismo", label: "Vecinalismo local", c: "#b45309",
    test: /vecinal|vecinos|san fernando|\bpilar\b|sumemos|acci[oó]n comunal|encuentro pilar|tiempo de vecinos/i },
];

export const OTHER = { key: "otras", label: "Otras fuerzas", c: "#94a3b8" };

export function famOf(nombre) {
  if (!nombre) return OTHER;
  for (const f of FAM) if (f.test.test(nombre)) return f;
  return OTHER;
}

export function title(s) {
  return s ? s.toLowerCase().replace(/\b\w/g, (m) => m.toUpperCase()) : s;
}
