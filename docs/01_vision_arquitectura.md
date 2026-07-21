# 01 · Visión y Arquitectura

## Visión

POLITEIA transforma datos electorales dispersos (nacionales, provinciales y
municipales; desde 1983) en inteligencia accionable para campañas y gestión.
Dos módulos en esta etapa:

- **Inteligencia** — analítica sobre datos duros: cómo se compone, estructura y
  mueve el voto; qué temas (issues) pesan por circuito; qué recomienda el sistema.
- **Defensa** — reacción en tiempo real: escucha activa de conversación pública y
  simulación del impacto de eventos sobre la estructura de voto.

Ambos módulos se paran sobre **la misma base de datos histórica**. Por eso el MVP
es esa base, no las features.

## Arquitectura (versión pulida del diagrama)

El diagrama original mezcla capas; acá quedan separadas por responsabilidad. Se
mantienen todos los servicios que aparecían (Route 53, WAF/Shield, Amplify,
Cognito, API Gateway, Lambda, DynamoDB, S3, Location Service, EventBridge/Step
Functions, Bedrock) y se ordena su rol.

### Capa de borde / acceso
- **Route 53** — DNS.
- **AWS WAF + Shield** — protección perimetral.
- **CloudFront** (implícito vía Amplify) — CDN/TLS.
- **Amplify Hosting** — sirve el frontend (React del mockup).
- **Amazon Cognito** — identidad y autorización (usuarios de campaña, roles).
- **API Gateway** — puerta única al backend (HTTP/REST).

### Capa de aplicación (backend serverless)
- **Lambda por dominio**: un conjunto de funciones por sub-módulo
  (composición del voto, estructura del voto, issues por circuito, sentimiento por
  fuente, recomendador IA; escucha activa; impacto en estructura de voto).
- **Step Functions / EventBridge** — orquestación de pipelines y jobs programados.
- **Amazon Bedrock** — LLM para recomendador, síntesis y análisis de sentimiento.
- **Amazon Location Service** — geografía electoral (circuitos, geocoding, mapas).

### Capa de datos (patrón lakehouse)
- **S3 `raw`** — crudos tal cual bajan de cada fuente (respaldo e insumo de re-proceso).
- **S3 `curated`** — datos normalizados en **Parquet**, particionados por
  `distrito / anio / categoria`. Catalogados en **Glue** y consultables con **Athena**.
- **DynamoDB** — lecturas operacionales del API: **agregados precomputados** por
  circuito/partido/elección (baja latencia para el frontend). No es el sistema de
  registro analítico; es la caché consultable.
- Opcional a futuro: capa "AI-ready" (embeddings/serie curada) para el recomendador.

### Ingesta / ETL (núcleo del MVP)
```
Fuentes (DINE API, Andy Tow, Junta Electoral PBA, Data CP, Wikipedia, PDFs)
      │  (Lambda/Fargate scraper por fuente, disparado por EventBridge)
      ▼
S3 raw  ──►  Normalización + validación (core/)  ──►  S3 curated (Parquet)
                                                  └─►  DynamoDB (agregados)
```
- Cada fuente tiene su extractor idempotente. El crudo se guarda **antes** de transformar.
- La normalización (agrupaciones, geografía, cargos) es común y vive en `core/`.

### Observabilidad y seguridad
- **CloudWatch** (logs/métricas), **X-Ray** (trazas), **Secrets Manager** (secretos),
  **IAM** con permisos mínimos por función. Sin PII de votantes en ningún lado.

## Por qué este orden

- **S3 primero, DynamoDB después.** El registro de verdad es el lago (auditable,
  barato, re-procesable). DynamoDB sirve consultas rápidas ya agregadas; si hay que
  recalcular, se recomputa desde `curated`.
- **Athena para lo analítico** (comparaciones históricas, cruces por circuito):
  SQL sobre Parquet, sin servidores.
- **Bedrock y Location aislados** detrás de Lambdas: se activan cuando llegan las
  features, sin bloquear el MVP de datos.

## Mapa módulo → servicios

| Sub-módulo | Cómputo | Datos | Extra |
|---|---|---|---|
| Composición del voto | Lambda | Athena/curated + DynamoDB | — |
| Estructura del voto | Lambda | curated + DynamoDB | Location Service |
| Issues por circuito | Lambda | curated + DynamoDB | Bedrock (clasificación) |
| Sentimiento por fuente | Lambda | curated + DynamoDB | Bedrock |
| Recomendador IA | Lambda | curated + DynamoDB | Bedrock |
| Escucha activa (Defensa) | Lambda + streaming | S3 raw + DynamoDB | EventBridge, Bedrock |
| Impacto en estructura de voto (Defensa) | Lambda / Step Functions | curated (base histórica) | — |
