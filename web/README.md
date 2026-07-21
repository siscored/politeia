# web/ — Frontend "Comando IA" (React + Vite)

Consola de inteligencia electoral. Primer módulo: **mapa por circuito**
(Inteligencia). Consume el API en vivo `politeia-api-mapa` + el GeoJSON de
circuitos (bundleado).

## Correr local
```bash
npm install
cp .env.example .env   # completá VITE_GOOGLE_MAPS_KEY (necesaria para el mapa)
npm run dev            # http://localhost:5173
```
El API se toma de `VITE_API_URL` (si no, usa el default de `src/api.js`). El mapa usa
**Google Maps** con `VITE_GOOGLE_MAPS_KEY` (en `.env` local / secret de GitHub en CI).

## Estructura
| Archivo | Qué es |
|---|---|
| `src/App.jsx` | shell: sidebar de módulos + routing (registro `MODULES`) |
| `src/modules/` | un componente por módulo del mockup (Resumen, Defensa, Inteligencia, Posicionamiento, Producción, Personalización) |
| `src/modules/Inteligencia.jsx` | el mapa real: estado, filtros, fetch al API, panel lateral y composición |
| `src/data/mock.js` | datos hardcodeados del mockup (VL) para los módulos aún no cableados |
| `src/MapGoogle.jsx` | mapa: Data layer de Google Maps, coloreado por familia |
| `src/families.js` | agrupación → familia política → color (espejo del diccionario de `core/`) |
| `src/geoutil.js` | centroides y encuadre (excluye islas del delta del fit) |
| `src/api.js` | cliente del API del mapa |
| `src/circuitos.json` | GeoJSON de los 37 circuitos (Pilar + San Fernando) |

## Hosting
AWS Amplify app `politeia-web` (ver `infra/stacks/web_stack.py`). **No** está
conectado al repo: el CI (`.github/workflows/deploy.yml`) buildea y sube el
artefacto por *manual deployment* en cada push a `main`. URL de producción:
**https://main.d3w3982cnzzi0m.amplifyapp.com**

## Pendiente
- Llevar la columna `familia` al dataset curado vía ETL (hoy `families.js` es el
  espejo por-keyword del diccionario de `core/`; ver docs/02 §normalización).
- Cablear los sub-tabs de Inteligencia (Composición, Issues, Sentimiento, Recomendador)
  y reemplazar los datos de ejemplo de los módulos mock por datos reales.
