// Presentación de familias políticas: key -> { label, color }.
//
// IMPORTANTE: la CLASIFICACIÓN (qué familia es cada agrupación cruda) NO vive
// más acá. La decide el backend en core/agrupaciones/familias.py, se materializa
// en la columna `familia` del dataset curado y llega por la API en cada item.
// Este archivo se quedó SOLO con el color/label por familia (una decisión de
// diseño del front). Antes duplicaba los regex del backend y había que
// mantener ambos en sync a mano — se eliminó para tener una única fuente de
// verdad del criterio (ver docs/02 §normalización y DECISIONES 2026-07-23).
//
// Los colores/labels deben coincidir con core/agrupaciones/familias.py (META).
const META = {
  no_partidario:     { label: "Blanco / nulo / s.d.",         c: "#475569" },
  cc_ari:            { label: "Coalición Cívica / ARI",       c: "#db2777" },
  peronismo:         { label: "Peronismo / UxP",              c: "#2563eb" },
  pj_federal:        { label: "Peronismo federal / centro",   c: "#38bdf8" },
  frentes_populares: { label: "Frentes populares",            c: "#0891b2" },
  jxc:               { label: "Juntos por el Cambio",         c: "#eab308" },
  lla:               { label: "La Libertad Avanza",           c: "#7c3aed" },
  liberales:         { label: "Liberales",                    c: "#0d9488" },
  massismo:          { label: "Massismo / F. Renovador",      c: "#ea580c" },
  izquierda:         { label: "Frente de Izquierda",          c: "#dc2626" },
  progresismo:       { label: "Progresismo",                  c: "#84cc16" },
  ucr:               { label: "Radicalismo / UCR",            c: "#06b6d4" },
  vecinalismo:       { label: "Vecinalismo local",            c: "#b45309" },
};

export const OTHER = { key: "otras", label: "Otras fuerzas", c: "#94a3b8" };

// Resuelve una key de familia (la que sirve la API) a { key, label, color }.
// Si la key es desconocida o falta, cae a "Otras fuerzas".
export function famByKey(key) {
  const m = META[key];
  return m ? { key, label: m.label, c: m.c } : OTHER;
}

export function title(s) {
  return s ? s.toLowerCase().replace(/\b\w/g, (m) => m.toUpperCase()) : s;
}
