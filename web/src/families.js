// Normalización de agrupaciones -> familia política -> color (por palabra clave).
// Es la misma lógica del prototipo; cuando el diccionario de core/ esté completo,
// esto se reemplaza por el agrupacion_id normalizado.
const FAM = [
  { key: "peronismo", c: "#2563eb", test: /victoria|todos|patria|justicialista|ciudadana|kirchner|frejupo|fpv|uxp/i },
  { key: "jxc / cambiemos", c: "#f59e0b", test: /cambiemos|juntos|cambio|pro\b|republican|macri/i },
  { key: "la libertad avanza", c: "#7c3aed", test: /libertad avanza|milei|lla/i },
  { key: "massismo / frentes", c: "#ea580c", test: /renovador|massa|una\b|1pais|1 pais|consenso federal|red x/i },
  { key: "radicalismo / ucr", c: "#0891b2", test: /radical|ucr|civica/i },
  { key: "izquierda / fit", c: "#dc2626", test: /izquierda|obrero|fit|trabajadores|socialista/i },
];
export const OTHER = { key: "otras / blanco", c: "#94a3b8" };

export function famOf(nombre) {
  if (!nombre) return OTHER;
  for (const f of FAM) if (f.test.test(nombre)) return f;
  return OTHER;
}

export function title(s) {
  return s ? s.toLowerCase().replace(/\b\w/g, (m) => m.toUpperCase()) : s;
}
