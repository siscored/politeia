// Cliente del API del mapa (politeia-api-mapa, Function URL).
// La URL se inyecta en build con VITE_API_URL; si no, usa el default conocido.
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
