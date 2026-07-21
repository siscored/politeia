# Log de decisiones (ADR livianas)

Registrar acá toda decisión de diseño/criterio que no esté ya en los docs. Formato:

## AAAA-MM-DD · Título corto de la decisión
- **Contexto:** qué problema apareció.
- **Decisión:** qué se resolvió.
- **Alternativas descartadas:** por qué no.
- **Impacto:** qué docs/módulos toca.

---

## 2026-XX-XX · (ejemplo) Criterio de normalización de frentes municipales
- **Contexto:** los frentes locales de San Fernando cambian de sigla casi cada elección.
- **Decisión:** se mapean a `agrupacion_id` por familia política + año en el diccionario.
- **Alternativas descartadas:** un id por sigla (rompe la serie histórica).
- **Impacto:** `core/agrupaciones/`, `docs/02`.

---

## 2026-07-20 · Infra como código (CDK) + CI/CD por OIDC
- **Contexto:** el repo no tenía IaC ni forma segura de desplegar a AWS.
- **Decisión:** AWS CDK (Python) en `infra/`. GitHub Actions despliega a AWS por
  **OIDC** (role `politeia-github-deploy`, sin claves de larga vida). Cuenta
  `851679891137`, profile local `idetec`.
- **Alternativas descartadas:** Terraform (suma un lenguaje al stack Python); claves
  IAM en GitHub Secrets (inseguro).
- **Impacto:** `infra/`, `.github/workflows/`, `CLAUDE.md §4`.

## 2026-07-20 · Versionado S3 habilitado
- **Contexto:** HUECO #4 — una recarga pisaba el histórico sin rastro.
- **Decisión:** versionado activado en `electoral-data-851679891137`. Cierra HUECO #4.

## 2026-07-20 · Capa de consulta: Glue + Athena con subprefijos por dataset
- **Contexto:** Glue cataloga por carpeta; `consolidado.csv` y `vista_mapa.csv`
  compartían `procesados/` y colisionaban.
- **Decisión:** cada dataset en su subprefijo (`procesados/consolidado/`,
  `procesados/vista_mapa/`); DB Glue `politeia_electoral`, workgroup Athena `politeia`.
  Los CSV originales en la raíz de `procesados/` se eliminaron (duplicado, recuperable
  por versionado).
- **Alternativas descartadas:** crawler sobre la carpeta mixta (tablas sucias).
- **Impacto:** `infra/stacks/data_stack.py`, layout de S3.

## 2026-07-20 · HUECO #5 — dataset actual no reproducible
- **Contexto:** los scripts que generaron el dataset no existen en ningún repo; la doc
  los referenciaba como si vivieran en un "repo original".
- **Decisión:** reconocerlo como HUECO #5, corregir las referencias muertas y
  reconstruir la ingesta desde cero en `ingest/` (Lambda `politeia-ingest-dine`).
- **Impacto:** `CLAUDE.md §2/§4/§6`, `docs/03`, `docs/06`, `ingest/*`.

## 2026-07-20 · Convención de naming AWS: prefijo politeia-
- **Decisión:** todo recurso AWS lleva prefijo `politeia-` (Lambdas, roles, etc.) para
  agruparlos/identificarlos en la consola.
- **Impacto:** toda la infra.

## 2026-07-21 · GeoJSON de circuitos (polígonos del mapa)
- **Contexto:** el bucket no tenía geometría; el mapa necesita polígonos para dibujar.
- **Decisión:** se obtuvo el GeoJSON de circuitos de PBA (repo
  `tartagalensis/circuitos_electorales_AR`, año 2025, derivado del oficial de
  `datos.gba.gob.ar`), se filtró a Pilar + San Fernando (**37 circuitos**) y se
  normalizó `circuito_id` a 5 chars (`0768`→`00768`) para joinear con `vista_mapa`.
  Verificado **37/37**. Subido a `procesados/geo/circuitos_pilar_sanfernando.geojson`.
- **Alternativas descartadas:** catálogo oficial `datos.gba.gob.ar` (el server cortaba
  la descarga); usar CABA data (no corresponde, son partidos de PBA).
- **Impacto:** cierra el gap del mapa; `procesados/geo/`, frontend.

## 2026-07-21 · API del mapa: Lambda + Function URL leyendo el CSV
- **Contexto:** el frontend necesita un endpoint de datos del mapa.
- **Decisión:** Lambda `politeia-api-mapa` con **Function URL** pública (CORS), que lee
  `vista_mapa.csv` **directo** (dataset chico, 2,7 MB) en vez de Athena en el camino
  crítico. Athena queda para analítica ad-hoc.
- **Alternativas descartadas:** Athena por request (latencia/costo innecesarios para
  2,7 MB); API Gateway (Function URL alcanza para un read-only).
- **Impacto:** `api/`, `infra/stacks/api_stack.py`.

## 2026-07-21 · Frontend React + hosting Amplify (manual deploy por el CI)
- **Contexto:** hacía falta el frontend real (no el prototipo/artifact).
- **Decisión:** app **React + Vite** en `web/` (monorepo). Hosting en Amplify app
  `politeia-web`, **sin conectar el repo** (evita manejar un token de GitHub): el CI
  buildea `web/` y sube el artefacto por *manual deployment* (`create-deployment` +
  `start-deployment`), autenticado por el OIDC que ya teníamos. El front consume el
  API en vivo + GeoJSON bundleado. URL: `https://main.d3w3982cnzzi0m.amplifyapp.com`.
- **Alternativas descartadas:** Amplify conectado a GitHub (requiere token/app);
  S3+CloudFront (el pedido era Amplify).
- **Impacto:** `web/`, `infra/stacks/web_stack.py`, `deploy.yml`, role OIDC.

## 2026-07-21 · Mapa sobre Google Maps (con fallback MapLibre)
- **Contexto:** el mockup usa Google Maps; con MapLibre el basemap raster tenía render
  inestable (quedaba negro hasta interactuar) tras muchos intentos de fix.
- **Decisión:** el mapa del módulo Inteligencia usa **Google Maps JS** (estilo oscuro,
  Data layer con los polígonos de circuito coloreados por fuerza + labels + selección)
  cuando existe `VITE_GOOGLE_MAPS_KEY`; si no, cae a **MapLibre** (fallback sin key).
  La key va en `web/.env` (gitignoreado) local y como **secret de GitHub** en el CI —
  nunca en el repo.
- **Impacto:** `web/src/MapGoogle.jsx`, `web/src/MapView.jsx` (fallback), `deploy.yml`
  (inyecta el secret), `web/.env.example`.
- **Ojo:** la key debe permitir el referer del dominio de producción (Amplify) + localhost.

## 2026-07-21 · Baja del fallback MapLibre (Google Maps único)
- **Contexto:** el CI siempre tiene la `VITE_GOOGLE_MAPS_KEY` (secret), así que en
  producción el fallback MapLibre nunca se ejecutaba: era peso muerto. `maplibre-gl`
  era además la dependencia que inflaba el bundle.
- **Decisión:** eliminar el fallback. Se borró `web/src/MapView.jsx`, la dependencia
  `maplibre-gl` y su import de CSS. El mapa usa **solo Google Maps**; sin key, no carga.
- **Impacto:** bundle **1,23 MB → 0,43 MB** (~3×). Archivos: `web/src/modules/Inteligencia.jsx`,
  `web/src/main.jsx`, `web/package.json`, `web/.env.example`, `web/src/styles.css`.
- **Reversible:** el fallback quedó registrado en la decisión anterior si hubiera que reponerlo.

## 2026-07-21 · Fixes de correctitud del API del mapa
- **CORS duplicado:** la Function URL **y** el handler seteaban ambos
  `Access-Control-Allow-Origin` → con `Origin` del browser se duplicaba y el fetch se
  rechazaba. Se quitó el CORS de la Function URL; lo maneja solo el handler.
- **% sobre positivos:** la composición y el % del ganador ahora **excluyen
  BLANCO/NULO** (convención electoral). Antes el denominador los incluía y subestimaba
  (Pilar 2025 Dip.Nac: 42,8 → **44,2%**).
