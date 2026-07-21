// Datos HARDCODEADOS del mockup "Comando IA" (ilustrativos, Vicente López).
// Se mantienen tal cual hasta cablear datos reales (ver CLAUDE.md §3).
// Fuente de los circuitos de VL en el mockup: DINE (provisorio) + polígonos CNE.

export const KPIS = [
  { label: "Intención estimada (VL)", value: "37,1%", delta: "+1,8", note: "vs medición previa · dato orienta, no decide" },
  { label: "Circuitos en disputa", value: "4 / 9", delta: "+1", note: "margen < 6 pts en Vicente López" },
  { label: "Sentimiento neto", value: "−4", delta: "−6", note: "últimas 24 h · escucha social" },
  { label: "Contenidos publicados", value: "12", delta: "+5", note: "esta semana · todos con revisión humana" },
];

export const PULSO = [
  { modulo: "Defensa", detalle: "Reclamos por recolección en Munro · +240% menciones en 6 h", tag: "1 tema creciendo rápido", tone: "crit" },
  { modulo: "Inteligencia", detalle: "VL a circuito por cargo · corte de boleta intendente↔presidente disponible", tag: "Mapa al día · 2023 (espejo) + 2025", tone: "brand" },
  { modulo: "Posicionamiento", detalle: "El candidato aparece en 2/5 motores de IA para “obras VL”", tag: "Share of answer bajo", tone: "warn" },
  { modulo: "Producción", detalle: "Termómetro: 1 variante supera el umbral de shares a 2 h", tag: "3 piezas en revisión", tone: "brand" },
  { modulo: "Personalización", detalle: "18 reclamos de campo sin asignar responsable", tag: "CRM consentido: 1.240", tone: "warn" },
];

export const ALERTAS = [
  { titulo: "Quejas por recolección de residuos en Munro", fuente: "X / grupos de barrio · hace 2 h", velo: "+240% / 6 h", tone: "crit" },
  { titulo: "Cuenta de oposición instala #VLseInunda", fuente: "Escucha de oposición · hace 5 h", velo: "+70% / 6 h", tone: "warn" },
  { titulo: "Repercusión positiva por obra en Av. Maipú", fuente: "Instagram / prensa local · hace 8 h", velo: "+30% / 12 h", tone: "good" },
];

export const BRECHA = [
  { tema: "Seguridad", votante: 78, candidato: 41, brecha: "+37" },
  { tema: "Limpieza / espacio público", votante: 76, candidato: 34, brecha: "+42" },
  { tema: "Obras y tránsito", votante: 52, candidato: 60, brecha: "−8" },
  { tema: "Salud municipal", votante: 64, candidato: 49, brecha: "+15" },
];

// Nota estándar de "datos de ejemplo" para los módulos aún no cableados.
export const MOCK_NOTE =
  "Capa conceptual con datos de ejemplo etiquetados — no es data real. El motor se " +
  "cablea post-MVP; la IA razona solo sobre datos cargados y la decisión es humana (CLAUDE.md §3).";
