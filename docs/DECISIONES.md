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

## 2026-07-21 · `familia` en el dataset + validadores en CI
- **Contexto:** la normalización de agrupaciones se resolvía solo en el front
  (`families.js`, por keyword). El dataset curado no llevaba la familia (deuda de
  docs/02 §normalización) y `core/validadores.py` no corría en el CI.
- **Decisión:**
  1. Resolver canónico en Python `core/agrupaciones/familias.py` (espejo de
     `families.js`: mismo orden, patrones y colores). Única fuente en el plano de datos.
  2. ETL reproducible `ingest/normaliza/enriquecer_vista_mapa.py` que agrega la columna
     `familia` a `vista_mapa.csv` (idempotente; aporta al HUECO #5).
  3. `vista_mapa.csv` en S3 re-subido **con** `familia` (versión anterior protegida por
     versionado).
  4. CI: `ci.yml` corre un smoke-test del resolver (sin datos); `deploy.yml` corre
     `core/validadores.py` sobre el `vista_mapa` real de S3 como **gate** antes de desplegar
     (corta si hay errores duros: duplicados, % fuera de rango, unidad sin ganador).
- **Impacto:** `core/agrupaciones/familias.py`, `core/validadores.py`, `core/requirements.txt`,
  `ingest/normaliza/`, `.github/workflows/{ci,deploy}.yml`, `vista_mapa.csv` (S3).
- **Pendiente derivado:** que la API sirva `familia` y el front la consuma (hoy sigue
  usando `famOf`), y habilitar el sub-tab "Composición del voto".

## 2026-07-23 · Pipeline de datos reproducible (politeia-pipeline-datos)
- **Contexto:** el gate de validación vivía en `deploy.yml` y corría DESPUÉS de
  publicar la key live (validaba tarde: un dato malo ya estaba en producción).
  Además el enriquecido `familia` no tenía forma orquestada/reproducible en la nube
  (parte de HUECO #5). Un push de código, encima, no debería republicar datos.
- **Decisión:** Step Functions **Standard** `politeia-pipeline-datos` con el patrón
  *validar en staging antes de publicar*:
  `Normaliza → Valida → Choice(ok) → Publica(_staging→live) | Alerta(SNS)+Fail`.
  - `politeia-normaliza-familias` (Lambda liviana, csv+core): lee `_source/`, agrega
    la columna `familia` (mismo `familia_de` que el CLI y el front) y escribe `_staging/`.
  - `politeia-valida-dataset` (Lambda, pandas del layer gestionado
    `AWSSDKPandas-Python312:29`): corre `core/validadores.validar_vista_mapa` **tal cual**
    sobre `_staging/`; `ok = sin errores duros`.
  - Layer `politeia-core`: empaqueta `core/` (única fuente de verdad) para ambas Lambdas.
    Se stagea a `python/core/` en cada `cdk synth` (helper en `pipeline_stack.py`, sin
    Docker; destino en `infra/.build/`, gitignoreado).
  - Solo si `ok` se copia `_staging/` → key live; si no, SNS `politeia-alertas` + Fail.
  - Claves de trabajo `_source/` y `_staging/` son **hermanas** de `vista_mapa/`
    (no adentro) para que el crawler de Glue no las levante como tablas.
- **Se quitó** el step "Validar dataset" de `deploy.yml`: el gate ya no valida la live
  post-deploy; la live solo cambia vía este pipeline, que valida antes.
- **Alternativas descartadas:** validar en el CI post-deploy (valida tarde, y ata la
  publicación de datos al push de código); reimplementar los validadores en csv puro en
  la Lambda (divergiría de `core/validadores.py`, la fuente de verdad — se prefirió pagar
  el layer de pandas y ejecutar el core sin cambios); tercera Lambda para publicar (se usó
  la integración nativa S3 `copyObject` de Step Functions).
- **Alcance honesto:** cubre enriquecer+validar+publicar. **NO** reconstruye el paso
  consolidado→vista_mapa base (eso lo deja upstream en `_source/`). Cierra el tramo de
  reproducibilidad de HUECO #5, no el HUECO completo.
- **Impacto:** `infra/stacks/pipeline_stack.py` (+`app.py`), `ingest/normaliza/handler.py`,
  `ingest/valida/handler.py`, `.github/workflows/deploy.yml`, `docs/07_pipeline_datos.md`,
  `CLAUDE.md §2` (HUECO #5). Tag `Project=politeia` a nivel app (rótulo de control de costos).
- **Pendiente derivado:** suscribir un email al topic `politeia-alertas`; sembrar
  `_source/` (bootstrap desde la live); trigger automático por llegada de datos requiere
  habilitar EventBridge en el bucket (hoy fuera de IaC).

## 2026-07-21 · Fixes de correctitud del API del mapa
- **CORS duplicado:** la Function URL **y** el handler seteaban ambos
  `Access-Control-Allow-Origin` → con `Origin` del browser se duplicaba y el fetch se
  rechazaba. Se quitó el CORS de la Function URL; lo maneja solo el handler.
- **% sobre positivos:** la composición y el % del ganador ahora **excluyen
  BLANCO/NULO** (convención electoral). Antes el denominador los incluía y subestimaba
  (Pilar 2025 Dip.Nac: 42,8 → **44,2%**).
