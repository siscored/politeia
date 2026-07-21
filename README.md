# POLITEIA

Plataforma de inteligencia electoral (Argentina). Etapa actual: módulos
**Inteligencia** y **Defensa**, sobre una base de datos histórica.

**Empezá por [`CLAUDE.md`](./CLAUDE.md)** — contrato de trabajo y auditor, ya
**sincronizado con el estado real del bucket S3**. Después, en orden:

1. [`docs/01_vision_arquitectura.md`](./docs/01_vision_arquitectura.md)
2. [`docs/02_modelo_de_datos.md`](./docs/02_modelo_de_datos.md) — esquema real + ideal
3. [`docs/03_mvp_recopilacion.md`](./docs/03_mvp_recopilacion.md) — qué está hecho / qué falta
4. [`docs/04_modulos_inteligencia_defensa.md`](./docs/04_modulos_inteligencia_defensa.md)
5. [`docs/05_fuentes_de_datos.md`](./docs/05_fuentes_de_datos.md)
6. [`docs/06_estado_bucket.md`](./docs/06_estado_bucket.md) — inventario real de S3

Decisiones: [`docs/DECISIONES.md`](./docs/DECISIONES.md).

## Estado real
- **Dataset:** Pilar + San Fernando, **2003–2025**, ejecutivo + legislativo
  (DINE + Junta PBA). Bucket: `s3://electoral-data-851679891137` (us-east-1).
- **Hueco #1 abierto:** falta **1983–2002** (vía Andy Tow). El contrato pedía
  "desde 1983". Ver `docs/03` y `docs/05`.
- **Deudas:** migrar `consolidado.csv` (150 MB) a Parquet particionado; reconstruir la
  ingesta (HUECO #5). Versionado S3: **hecho**. Linaje fino: lo escribe `politeia-ingest-dine`.

## Scaffold incluido
- `core/` — esquema (`esquema.py`), validadores (`validadores.py`), diccionario de
  agrupaciones semilla (`agrupaciones/diccionario.csv`). Es el contrato compartido.
- `infra/` — IaC (AWS CDK): OIDC GitHub↔AWS, catálogo Glue/Athena, Lambda de ingesta,
  API del mapa. Se despliega solo por CI/CD (`.github/workflows/`) en cada push a `main`.
- `ingest/dine` — Lambda `politeia-ingest-dine` (reconstruida; no había script previo).
  `ingest/junta_pba` y `ingest/andytow`: pendientes.
- `api/mapa` — Lambda `politeia-api-mapa` (Function URL): sirve `vista_mapa` por circuito
  para el frontend. El mapa joinea con `procesados/geo/circuitos_pilar_sanfernando.geojson`.
- `web/` — Frontend React+Vite "Comando IA" (mapa por circuito). Hosteado en Amplify
  (`politeia-web`), desplegado por el CI. Prod: https://main.d3w3982cnzzi0m.amplifyapp.com

Mockup ("Comando IA"): https://main.d1pthxba9jy105.amplifyapp.com/
