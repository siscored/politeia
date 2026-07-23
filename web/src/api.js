// Cliente del API del mapa (politeia-api-mapa, API Gateway HTTP API).
// La URL real se inyecta en build con VITE_API_URL (output ApiMapaUrl del stack
// PoliteiaApi). El fallback de abajo es solo para dev local sin env; tras el
// primer deploy con API Gateway, reemplazar por la URL execute-api.* o setear
// VITE_API_URL en web/.env.
const BASE =
  import.meta.env.VITE_API_URL ||
  "https://vlcwwo3krujfmwxe735xwppmmq0czzga.lambda-url.us-east-1.on.aws/";

async function get(params) {
  const qs = new URLSearchParams(params).toString();
  const r = await fetch(`${BASE}?${qs}`);
  // Un 404 (combinación inexistente) trae un body JSON de error: parsearlo como
  // si fuera un resultado deja el mapa vacío sin explicación. Mejor que falle.
  if (!r.ok) throw new Error(`API ${r.status} · ${qs}`);
  return r.json();
}

export const fetchMeta = () => get({ meta: 1 });

export const fetchMapa = (distrito, anio, cargo, tipo = "GENERAL") =>
  get({ distrito, anio, cargo, tipo });
