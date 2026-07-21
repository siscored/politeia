# api/ — API read-only (lo que consume el frontend)

Endpoints HTTP sobre los datos curados. Son Lambdas detrás de Function URL,
desplegadas por CDK (`infra/stacks/api_stack.py`) vía el pipeline.

## `mapa/` — `politeia-api-mapa`

Sirve `vista_mapa` filtrado, para pintar el mapa electoral por circuito.

- **URL:** Function URL pública (CORS abierto; los datos son públicos). Se
  obtiene del output `ApiMapaUrl` del stack `PoliteiaApi`.
- **Implementación:** lee `vista_mapa.csv` directo desde S3 y lo cachea en
  memoria (dataset chico, 2,7 MB → más rápido/barato que Athena en el request).

### Endpoints
| Request | Devuelve |
|---|---|
| `GET /?meta=1` | dimensiones para los filtros: `distritos`, `anios`, `cargos`, `tipos` |
| `GET /?distrito=pilar&anio=2023&cargo=PRESIDENTE&tipo=GENERAL` | por circuito: `ganador` (agrupación, votos, %), `composicion` completa, `granularidad`, `circuito_padre` |

`tipo` es opcional (default `GENERAL`). Valores: ver `docs/02` y el `?meta=1`.

### Cómo joinea con el mapa
El `circuito_id` que devuelve la API es la **clave de join con el GeoJSON**
`procesados/geo/circuitos_pilar_sanfernando.geojson` (mismo formato de 5 chars,
`00768` / `0768A`). El frontend pinta cada polígono con el `ganador` de su
`circuito_id` (o con el `circuito_padre` para años pre-2019 — ver `vista_mapa`).

### Reglas de render (heredadas de `vista_mapa`)
- Si la combinación elegida solo trae `granularidad='municipio'` (años 2003–2009,
  sept-2025), pintar todo el partido uniforme (el mapa nunca queda vacío).
- Años pre-2019: pintar cada polígono actual con el valor de su `circuito_padre`.
