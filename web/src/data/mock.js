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

// ===== 01 · DEFENSA — escucha activa + protocolo de respuesta =====
export const ESCUCHA = [
  { fuente: "X // Twitter", tipo: "Red social", volumen: 1840, pos: 18, neu: 34, neg: 48, temas: ["Inseguridad", "Tránsito"], curada: true, procesa: "interno" },
  { fuente: "Grupos de barrio (Facebook)", tipo: "Red social", volumen: 2210, pos: 22, neu: 39, neg: 39, temas: ["Alumbrado", "Residuos", "Veredas"], curada: true, procesa: "onclusive" },
  { fuente: "Instagram local", tipo: "Red social", volumen: 970, pos: 41, neu: 37, neg: 22, temas: ["Obras", "Espacios verdes"], curada: true, procesa: "interno" },
  { fuente: "Prensa local (portales)", tipo: "Medios", volumen: 340, pos: 33, neu: 45, neg: 22, temas: ["Gestión", "Tasas"], curada: true, procesa: "interno" },
];

export const PROTOCOLO = [
  { paso: "Detectar por velocidad", detalle: "Un ataque que mueve blandos dispara la alerta antes del pico." },
  { paso: "Priorizar", detalle: "Alcance × negatividad × credibilidad. El sistema ordena; no responde solo." },
  { paso: "Verificar la fuente", detalle: "Cuenta, historial y si es orgánico o coordinado." },
  { paso: "Decidir respuesta", detalle: "Responder, desmentir o no amplificar — la decisión es humana." },
];

// ===== 03 · POSICIONAMIENTO — share of answer en motores de IA =====
export const MOTORES = [
  { motor: "ChatGPT", pres: true }, { motor: "Gemini", pres: true },
  { motor: "Perplexity", pres: false }, { motor: "Claude", pres: false }, { motor: "Copilot", pres: false },
];
export const SHARE_VOICE = [
  { quien: "Candidato propio", val: 42 },
  { quien: "Principal opositor", val: 58 },
  { quien: "Tercer espacio", val: 27 },
];
// rel = relevancia para el votante · ocup = ocupación del candidato en la respuesta
export const AGENDA_MOTORES = [
  { tema: "Seguridad", rel: 88, ocup: 56 },
  { tema: "Limpieza / espacio público", rel: 72, ocup: 24 },
  { tema: "Tasas", rel: 63, ocup: 38 },
  { tema: "Salud municipal", rel: 52, ocup: 30 },
  { tema: "Obras y tránsito", rel: 55, ocup: 80 },
  { tema: "Espacios verdes", rel: 34, ocup: 62 },
];

// ===== 04 · PRODUCCIÓN — fábrica de contenido con termómetro orgánico =====
export const PRODUCCION_FLOW = [
  { paso: "Brief", detalle: "El equipo carga el objetivo y el tono." },
  { paso: "Variantes IA", detalle: "La IA genera el volumen de piezas." },
  { paso: "Termómetro A/B", detalle: "Se mide en orgánico; sube la que rinde." },
  { paso: "Decisión humana", detalle: "Ninguna se publica sin revisión." },
];
export const FUNNEL = [
  { paso: "Mensajes enviados", n: 4200 },
  { paso: "Entregados", n: 3980 },
  { paso: "Respondidos", n: 1510 },
  { paso: "Derivados a humano", n: 280 },
];

// ===== 05 · PERSONALIZACIÓN — CRM de reclamos de campo (consentido) =====
// Anillos: duro (centro) → imposible (borde). Tamaño = adhesión estimada.
export const SEGMENTOS = [
  { segmento: "Duro", pct: 31, tone: "brand" },
  { segmento: "Blando", pct: 24, tone: "good" },
  { segmento: "Posible", pct: 22, tone: "warn" },
  { segmento: "Difícil", pct: 15, tone: "warn" },
  { segmento: "Imposible", pct: 8, tone: "crit" },
];
export const RECLAMOS = [
  { t: "Calle en mal estado · Carapachay", canal: "Bot Ciudadano Activo", estado: "sin asignar", tone: "warn" },
  { t: "Luminaria apagada · Munro", canal: "Bot Ciudadano Activo", estado: "en curso", tone: "brand" },
  { t: "Relevamiento manzana 12 · Florida O.", canal: "Bot asistente militante", estado: "cargado", tone: "good" },
];
