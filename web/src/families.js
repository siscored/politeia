// Normalización de agrupaciones -> familia política -> color (por palabra clave).
// Colores alineados con el mockup (JxC verde, peronismo azul, LLA ámbar, FIT violeta).
// Cuando el diccionario de core/ esté completo, esto se reemplaza por agrupacion_id.
const FAM = [
  { key: "peronismo", label: "Unión por la Patria / peronismo", c: "#2563eb", test: /victoria|todos|patria|justicialista|ciudadana|kirchner|frejupo|fpv|uxp/i },
  { key: "jxc", label: "Juntos por el Cambio", c: "#16a34a", test: /cambiemos|juntos|cambio|pro\b|republican|macri/i },
  { key: "lla", label: "La Libertad Avanza", c: "#eab308", test: /libertad avanza|milei|lla/i },
  { key: "massismo", label: "Massismo / frentes", c: "#ea580c", test: /renovador|massa|una\b|1pais|1 pais|consenso federal|red x/i },
  { key: "ucr", label: "Radicalismo / UCR", c: "#0891b2", test: /radical|ucr|civica/i },
  { key: "izquierda", label: "Frente de Izquierda", c: "#9333ea", test: /izquierda|obrero|fit|trabajadores|socialista/i },
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
