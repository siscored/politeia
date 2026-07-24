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

## 2026-07-23 · La API sirve `familia`; el front deja de reclasificar
- **Contexto:** el criterio agrupación→familia estaba **duplicado**: los regex vivían
  en `core/agrupaciones/familias.py` (backend) **y** en `web/src/families.js` (front),
  copiados a mano. El front reclasificaba con `famOf(nombre)` en cada render, aunque la
  columna `familia` ya se materializaba en el dataset. Dos fuentes de verdad que podían
  divergir en silencio (el mapa pintaba un color y el dato validado decía otra cosa).
- **Decisión:** separar **clasificación** (backend) de **presentación** (front).
  - La API (`api/mapa/handler.py`) reenvía `familia` en cada item de la composición
    (y por ende en `ganador`), leyéndola de la columna del CSV. Fallback `"otras"`.
  - `web/src/families.js` pierde los 13 regex: queda solo la tabla `META`
    (`familia → {label, color}`) + `famByKey(key)`. Se eliminó `famOf`.
  - `web/src/modules/Inteligencia.jsx` consume `item.familia` (circuito y municipio,
    ganador incluido) en vez de reclasificar por nombre. Import muerto de `famOf` en
    `MapGoogle.jsx` removido.
- **Alternativas descartadas:** que la API sirviera también color/label (el color es
  decisión de diseño del front, no del backend — se dejó la presentación en el front);
  mantener `famOf` como fallback en el front (perpetuaba la duplicación de regex).
- **Validado:** `npm run build` OK (44 módulos); smoke-test del handler contra el CSV
  live real → Pilar 2023 PRESIDENTE devuelve `UNION POR LA PATRIA→peronismo`,
  `LA LIBERTAD AVANZA→lla`, `JUNTOS POR EL CAMBIO→jxc`.
- **Orden de deploy:** la API (infra, por CI en push a main) debe quedar viva **antes**
  de redeployar el front en Amplify; si el front saliera primero, `item.familia` vendría
  `undefined` y el mapa se pintaría gris. El colores/labels de `META` deben seguir
  coincidiendo con `core/agrupaciones/familias.py`.
- **Impacto:** `api/mapa/handler.py`, `web/src/families.js`,
  `web/src/modules/Inteligencia.jsx`, `web/src/MapGoogle.jsx`, `docs/02`. Cierra el
  "cabo suelto" del contrato `core/` ↔ front.

## 2026-07-24 · Internas de las PASO desde el bucket (dimensión latente)
- **Contexto:** el consolidado tenía `lista_numero`/`lista_nombre` (listas internas de
  PASO) sin explotar: 95% de las filas PASO las traen, 243 listas distintas. El mapa
  suma las listas de un partido y las esconde.
- **Decisión:** materializar `procesados/vista_internas/vista_internas.csv` (1147 filas):
  una fila por municipio/anio/cargo/agrupacion/lista con votos, `votos_partido`,
  `pct_en_partido`, `gana_interna` (lista más votada del partido) y `listas_en_partido`.
  Generado con Athena (`analytics/internas/`), mismo patrón que participación (SELECT +
  copia, no CTAS).
- **Ejemplo real validado:** Pilar 2021 interna de CONCEJALES de JUNTOS — lista B 38.52%
  gana a A 37.55% y DAR EL PASO 23.92%.
- **Límites:** solo PASO con voto positivo y lista nombrada (~2011-2025); partidos con
  lista única salen con `listas_en_partido=1`. Hereda caveats de DINE provisorio.
- **Hallazgo colateral (documentado, NO materializado):** `mesa_tipo` distingue
  **nativos vs extranjeros**, con participación muy distinta — Pilar 2023 DIPUTADOS_PROV:
  nativos 77.9% vs **extranjeros 47.7%** (padrón 29.561). Los extranjeros no votan
  cargos nacionales (presidente/diputado nac.). Dimensión materializable a futuro (explica
  parte de los outliers bajos de participación). `mesa_tipo` tiene naming sucio a limpiar.
- **Impacto:** `analytics/internas/`, `docs/02`.

## 2026-07-24 · Participación electoral desde el bucket (deuda #6)
- **Contexto:** el bucket ya tenía datos de valor sin explotar. El más claro: el padrón
  (`mesa_electores`) y el tipo de voto (`votos_tipo`) del consolidado (nivel mesa DINE),
  con los que se calcula **participación** y **desglose positivo/blanco/nulo** — deuda #6,
  sin necesidad de fuentes nuevas.
- **Decisión:** materializar el dataset curado `procesados/vista_participacion/vista_participacion.csv`
  (una fila por municipio/anio/eleccion_tipo/cargo/circuito, con `mesas`, padrón, emitidos,
  participación % y desglose). Se genera con Athena (`analytics/participacion/vista_participacion.sql`
  + `build.sh`). **No CTAS** (el workgroup `politeia` impone la ubicación de salida y lo
  bloquea): se corre un SELECT y se copia su resultado a la clave curada.
- **Cobertura y límites (declarados, no silenciosos):**
  - Solo **2011–2025** (el padrón viene de DINE por mesa; Junta 2003–2009 no lo trae).
  - DINE es **provisorio**.
  - **Outliers bajos** de participación a nivel circuito (PASO y circuitos chicos de SF
    como `0882A`/`00881`, ~30–40%). Verificado que NO son mesas de extranjeros (NATIVOS);
    causa única no fijada. Mitigación: columna `mesas` para juzgar robustez + recomendación
    de leer participación a nivel municipio. NO publicar el dato de circuito sin este contexto.
  - `mesa_tipo` con naming sucio en el origen (`NATIVOS`/`NATIVO`, `EXTRANJEROS`/`EXTRANJERO`,
    vacíos) — anotado como deuda de limpieza del consolidado.
- **Alcance:** entrega el **dato** (Fase 1). Consumirlo en el mapa (endpoint + capa
  "participación") es Fase 2, no hecha.
- **Impacto:** `analytics/participacion/`, `docs/02` (deuda #6 → hecha).

## 2026-07-23 · Migración a Parquet particionado (HUECO #3)
- **Contexto:** `consolidado.csv` es 1 archivo de ~150 MB; cada query de Athena lo
  escanea entero. El contrato (CLAUDE.md §4, docs/03 §2) pide **Parquet particionado
  por `distrito/anio/categoria`**, con CSV como espejo humano.
- **Decisión:** Parquet SNAPPY en `procesados/parquet/consolidado/`, particionado por
  `municipio / anio / categoria`, tabla Glue `consolidado_parquet` con **partition
  projection**. Carga vía Athena `INSERT INTO … SELECT` desde la tabla CSV existente,
  **en tandas** (límite de 100 particiones por query). SQL versionado en `analytics/parquet/`.
- **Interpretaciones del contrato (las libertades que se tomaron, confirmadas con el usuario):**
  1. **"distrito" = `municipio`.** Según la jerarquía del proyecto (docs/02): `País →
     Distrito (PBA) → Sección → Municipio`. Literalmente "Distrito" = PBA = **un único
     valor** → inútil como partición. La unidad analítica real es `municipio`
     (pilar/san_fernando), que es lo que usan `vista_mapa` y el patrón DynamoDB
     (`PK=MUNI#`). Existe además una columna `distrito_id` que significa otra cosa
     (id de distrito electoral) y NO se usa como partición.
  2. **"categoria" = `cargo_nombre`.** En jerga electoral, categoría = el cargo que se
     elige (presidente, diputado, concejal…). `eleccion_tipo` (paso/general/balotaje)
     queda como columna filtrable, NO como partición (el contrato lista 3 claves).
  3. **Partition projection en vez de crawler.** El docstring de `data_stack.py`
     anticipaba re-apuntar el crawler a los prefijos Parquet. Se prefiere projection:
     la tabla deriva sus particiones de la query (sin correr/pagar crawler ni MSCK).
- **Validación:** los totales deben cerrar CSV vs Parquet — `COUNT(*)` y
  `SUM(votos_cantidad)` global y por partición (contrato §6/§7).
- **Gestión de la tabla:** la crea el **DDL versionado** (`analytics/parquet/01_create…sql`
  + runner `run.sh`), NO CloudFormation. Se prefirió no codificarla como `glue.CfnTable`
  ahora (partition projection en CDK suma verbosidad/riesgo y un ciclo de deploy) — el DDL
  versionado ya cumple la reproducibilidad del contrato (§6). **Follow-up documentado:**
  codificar la tabla en `data_stack.py` como IaC. Es una desviación consciente de la
  disciplina IaC-first del repo, registrada acá para que no sea un hueco silencioso.
- **Resultado verificado (2026-07-23):** 1.200.301 filas y 27.095.945 votos idénticos
  CSV↔Parquet, 0 particiones con diferencia, 96 particiones, 3.55 MB (vs 149.7 MB CSV),
  ~41 KB escaneados por consulta típica (vs ~157 MB en CSV, ~3800×).
- **Alcance honesto:** migra `consolidado`. NO toca `vista_mapa` (el API sigue leyendo
  su CSV, chico y en el path crítico). NO cierra el linaje fino (deuda #3.3). El refresh
  automático (enganchar al pipeline de Step Functions) queda como follow-up.
- **Impacto:** `analytics/parquet/`, `docs/02`, `docs/03`, `CLAUDE.md §2` (HUECO #3).

## 2026-07-21 · Fixes de correctitud del API del mapa
- **CORS duplicado:** la Function URL **y** el handler seteaban ambos
  `Access-Control-Allow-Origin` → con `Origin` del browser se duplicaba y el fetch se
  rechazaba. Se quitó el CORS de la Function URL; lo maneja solo el handler.
- **% sobre positivos:** la composición y el % del ganador ahora **excluyen
  BLANCO/NULO** (convención electoral). Antes el denominador los incluía y subestimaba
  (Pilar 2025 Dip.Nac: 42,8 → **44,2%**).
