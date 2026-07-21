# web/ — Frontend "Comando IA" (React + Vite)

Consola de inteligencia electoral. Primer módulo: **mapa por circuito**
(Inteligencia). Consume el API en vivo `politeia-api-mapa` + el GeoJSON de
circuitos (bundleado).

## Correr local
```bash
npm install
cp .env.example .env   # completá VITE_GOOGLE_MAPS_KEY (opcional; sin key → MapLibre)
npm run dev            # http://localhost:5173
```
El API se toma de `VITE_API_URL` (si no, usa el default de `src/api.js`). El mapa usa
**Google Maps** si hay `VITE_GOOGLE_MAPS_KEY` (en `.env` local / secret de GitHub en CI),
y cae a **MapLibre** si no la hay.

## Estructura
| Archivo | Qué es |
|---|---|
| `src/App.jsx` | estado, filtros, fetch al API, panel lateral (ganador municipio, corte de boleta, composición) |
| `src/MapView.jsx` | mapa SVG: proyecta el GeoJSON y colorea por fuerza ganadora |
| `src/families.js` | agrupación → familia política → color (por palabra clave) |
| `src/api.js` | cliente del API del mapa |
| `src/circuitos.json` | GeoJSON de los 37 circuitos (Pilar + San Fernando) |

## Hosting
AWS Amplify app `politeia-web` (ver `infra/stacks/web_stack.py`). **No** está
conectado al repo: el CI (`.github/workflows/deploy.yml`) buildea y sube el
artefacto por *manual deployment* en cada push a `main`. URL de producción:
**https://main.d3w3982cnzzi0m.amplifyapp.com**

## Pendiente
- Normalizar agrupaciones con el diccionario de `core/` (hoy: match por keyword).
- Más vistas (margen, participación) y los otros módulos del mockup.
