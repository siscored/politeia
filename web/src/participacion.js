// Escala de color para el modo "Participación" del mapa.
//
// Magnitud (asistencia %) -> escala SECUENCIAL de un solo tono (cyan), tenue→
// brillante (skill dataviz: sequential = one hue, light→dark). Sobre el mapa
// oscuro, más brillo = más participación. En tramos (choropleth) para que la
// leyenda sea legible. Sin dato (s/d) = gris neutro.
export const PART_STEPS = [
  { max: 60,       c: "#155e63", label: "< 60%" },
  { max: 70,       c: "#0e7490", label: "60–70%" },
  { max: 75,       c: "#0891b2", label: "70–75%" },
  { max: 80,       c: "#22d3ee", label: "75–80%" },
  { max: Infinity, c: "#67e8f9", label: "≥ 80%" },
];

export const PART_SD = "#334155"; // sin dato

// Devuelve el color de un % de participación (o gris si no hay dato).
export function partColor(pct) {
  if (pct == null || !Number.isFinite(pct)) return PART_SD;
  for (const s of PART_STEPS) if (pct < s.max) return s.c;
  return PART_STEPS[PART_STEPS.length - 1].c;
}
