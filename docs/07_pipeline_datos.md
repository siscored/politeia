# 07 · Pipeline de datos (`politeia-pipeline-datos`)

Pipeline reproducible que toma la **vista_mapa base**, le agrega la columna
`familia`, la **valida** y —solo si pasa— la **publica** a la key live que
consume el API del mapa. Cierra el tramo enriquecer→validar→publicar de
**HUECO #5** (reproducibilidad) y reubica el gate de calidad que antes corría
tarde en `deploy.yml` (validaba la live *después* de publicarla).

> Definido en `infra/stacks/pipeline_stack.py`. Handlers en `ingest/normaliza/`
> y `ingest/valida/`. Decisión: `docs/DECISIONES.md` (2026-07-23).

## Flujo

```
Normaliza ──▶ Valida ──▶ ¿ok? ─┬─ sí ─▶ Publica (_staging → live) ─▶ Publicado ✓
                                └─ no ─▶ Alerta (SNS) ─▶ Rechazado ✗
   (excepción en Normaliza/Valida) ─────▶ AlertaError (SNS) ─▶ FalloEjecución ✗
```

**Patrón clave — validar en staging antes de publicar:** la candidata se escribe
en `_staging/` y se valida ahí; la key **live nunca se toca** salvo que la
validación pase. Una subida mala no llega a producción.

## Claves S3

| Rol | Key | Quién escribe |
|---|---|---|
| Entrada (base upstream) | `electoral/procesados/_source/vista_mapa.csv` | upstream / bootstrap |
| Candidata (se valida) | `electoral/procesados/_staging/vista_mapa.csv` | `politeia-normaliza-familias` |
| **Live (producción)** | `electoral/procesados/vista_mapa/vista_mapa.csv` | el pipeline, solo si valida OK |

`_source/` y `_staging/` son **hermanas** de `vista_mapa/` (no adentro) a
propósito: el crawler de Glue apunta a `.../vista_mapa/` y así no las levanta
como tablas de trabajo sucias.

## Recursos AWS (stack `PoliteiaPipeline`)

- **Lambda `politeia-normaliza-familias`** (liviana, `csv` + `core`): lee `_source/`,
  resuelve `familia` con `core/agrupaciones/familias.py` (mismo criterio que el CLI
  `enriquecer_vista_mapa.py` y que el front), escribe `_staging/`. Idempotente.
- **Lambda `politeia-valida-dataset`** (pandas del layer gestionado
  `AWSSDKPandas-Python312`): corre `core/validadores.validar_vista_mapa` **tal cual**
  sobre `_staging/`. Devuelve `{ok, duros, blandos, n_filas}`.
- **Layer `politeia-core`**: empaqueta `core/` (única fuente de verdad) para ambas
  Lambdas. Se regenera en cada `cdk synth` (staging a `python/core/` sin Docker).
- **SNS `politeia-alertas`**: notifica rechazo/fallo. **Sin suscriptores por defecto.**
- **Step Functions `politeia-pipeline-datos`** (Standard): orquesta el flujo.

## Cómo se opera

### 1. Suscribir el email de alertas (una vez)
```bash
TOPIC=$(aws cloudformation describe-stacks --stack-name PoliteiaPipeline \
  --query "Stacks[0].Outputs[?OutputKey=='AlertasTopicArn'].OutputValue" \
  --output text --profile idetec)
aws sns subscribe --topic-arn "$TOPIC" --protocol email \
  --notification-endpoint TU_EMAIL@dominio.com --profile idetec
# confirmar el mail que llega
```

### 2. Sembrar `_source/` (bootstrap, una vez)
Hoy no existe el paso automatizado consolidado→vista_mapa base (fuera de alcance,
HUECO #5). El bootstrap honesto es partir de la live actual (la normalización
recalcula `familia` de forma idempotente):
```bash
aws s3 cp s3://electoral-data-851679891137/electoral/procesados/vista_mapa/vista_mapa.csv \
          s3://electoral-data-851679891137/electoral/procesados/_source/vista_mapa.csv \
          --profile idetec
```
De ahí en más, upstream deja la nueva base en `_source/` y se corre el pipeline.

### 3. Ejecutar el pipeline
```bash
ARN=$(aws cloudformation describe-stacks --stack-name PoliteiaPipeline \
  --query "Stacks[0].Outputs[?OutputKey=='PipelineArn'].OutputValue" \
  --output text --profile idetec)
aws stepfunctions start-execution --state-machine-arn "$ARN" --profile idetec
```
Seguir el resultado en la consola de Step Functions o con
`aws stepfunctions describe-execution --execution-arn ...`.

## Qué NO hace (alcance honesto)

- No reconstruye `consolidado.csv` → `vista_mapa` base (eso es upstream; sigue siendo
  parte abierta de HUECO #5).
- No se dispara solo al llegar datos: el **trigger automático** por evento de S3
  requiere habilitar EventBridge en el bucket, que hoy está **fuera de IaC**. Por ahora
  la ejecución es manual (o desde una automatización que llame a `start-execution`).
- No migra a Parquet (HUECO #3): sigue operando sobre CSV.
