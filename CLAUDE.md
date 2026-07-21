# POLITEIA — Contrato de trabajo (CLAUDE.md)

> Fuente de verdad y **auditor** del proyecto. Cualquier instancia de Claude Code que
> trabaje en cualquier módulo lee esto primero. Ante ambigüedad, gana lo escrito acá;
> si acá no dice nada, se propone y se registra la decisión en `docs/DECISIONES.md`
> antes de codear. Este archivo está **sincronizado con el estado real del bucket S3**
> (inventario del 19-jul-2026). Ver `docs/06_estado_bucket.md`.

---

## 0. Estado real hoy (lo que ya existe)

- **Bucket fuente de verdad:** `s3://electoral-data-851679891137` (cuenta
  `851679891137`, región `us-east-1`, SSE-S3, **sin versionado**).
- **Prefijo raíz:** `electoral/` → `raw/` (por fuente→municipio), `procesados/`
  (curated), `docs/`.
- **Dataset actual:** Pilar + San Fernando, **2003–2025**, ejecutivo y legislativo,
  cruzando **DINE** (provisorio, por mesa, 2011-2025) + **Junta Electoral PBA**
  (definitivo, por municipio, 2003-2025). 180 objetos, 374 MB, carga batch única.
- **App mockup:** "Comando IA"; `procesados/vista_mapa.csv` es la versión productiva
  del contrato del mapa que se mockeó ahí.

## 1. Qué es POLITEIA (en una frase)

Plataforma de **inteligencia electoral** para campañas y gestión política en la
Argentina. Dos módulos en esta etapa: **Inteligencia** (analítica sobre datos duros)
y **Defensa** (escucha en tiempo real + simulación de impacto). Mockup de referencia:
`https://main.d1pthxba9jy105.amplifyapp.com/`.

## 2. Alcance y HUECOS ABIERTOS (leer antes de tocar nada)

| | Estado |
|---|---|
| Módulos de la etapa | Inteligencia y Defensa |
| Geografía | Pilar y San Fernando (PBA) |
| **Cobertura lograda** | **2003–2025**, ejecutivo + legislativo (DINE + Junta PBA) |
| **HUECO #1 (crítico)** | **1983–2002 NO está.** El contrato pedía "desde 1983". Falta la franja que cubre **Andy Tow** (presidencial/gobernador/municipal 1983-2011). Ver `docs/05`. |
| HUECO #2 | Sept-2025 solo a nivel **municipio** (no circuito) para lo no cubierto por DINE. |
| HUECO #3 | Formato analítico: `consolidado.csv` es 1 CSV de ~150 MB; el contrato pide **Parquet particionado**. Ver `docs/03 §migración`. |
| ~~HUECO #4~~ **RESUELTO** | Versionado S3 **habilitado** (2026-07-20): el bucket ya protege el histórico. |
| **HUECO #5 (nuevo, crítico)** | **El dataset actual NO es reproducible:** los scripts que lo generaron no existen en ningún repo. Se reconstruyen desde cero en `ingest/` (primera pieza: Lambda `politeia-ingest-dine`). |
| Fuera de alcance | Resto del país, features de IA/escucha en vivo (se diseñan, no se implementan) |

**Regla dura:** un hueco documentado es aceptable; un hueco silencioso, no. Están
sobre la mesa: no cerrarlos en silencio ni asumir que no existen.

## 3. Estructura del repo

```
politeia/
├── CLAUDE.md                     ← este archivo (auditor)
├── docs/
│   ├── 01_vision_arquitectura.md
│   ├── 02_modelo_de_datos.md     ← esquema REAL (consolidado + vista_mapa) + ideal
│   ├── 03_mvp_recopilacion.md    ← qué está hecho / qué falta
│   ├── 04_modulos_inteligencia_defensa.md
│   ├── 05_fuentes_de_datos.md
│   ├── 06_estado_bucket.md       ← inventario real de S3 + recomendaciones
│   └── DECISIONES.md
├── core/                         ← contrato compartido: esquema, validadores, diccionario
│   ├── esquema.py
│   ├── validadores.py
│   └── agrupaciones/diccionario.csv
├── ingest/                       ← extractores/ETL (se reconstruyen acá; no había scripts previos)
│   ├── dine/                     ← Lambda politeia-ingest-dine (handler.py) + README
│   ├── junta_pba/README.md       ← pendiente
│   └── andytow/README.md         ← pendiente (hueco 1983-2002)
├── infra/                        ← IaC (AWS CDK Python): OIDC + Glue/Athena + ingest
└── .github/workflows/            ← CI/CD (deploy a AWS por OIDC en push a main)
```

> Nota de naming: el bucket usa `procesados/`; el contrato usa `curated/`. Se acepta
> `procesados/` como **alias oficial** de `curated/` (registrado en `docs/06`). No
> renombrar sin coordinar.

## 4. Stack y convenciones (no negociar sin registrar decisión)

- **Cloud:** AWS serverless. Ingesta/ETL en **Lambda** (Fargate si excede 15 min),
  orquestada por **EventBridge**/**Step Functions**.
- **Lenguaje de ingesta/ETL:** **Python 3.12**. Los scripts que produjeron el dataset
  actual NO se conservaron (HUECO #5); se reconstruyen como Lambdas en `ingest/`,
  empezando por `politeia-ingest-dine`.
- **Almacenamiento:** S3 (`raw` + `procesados`/curated) con Athena para analítica;
  DynamoDB/Aurora para lecturas del API. `vista_mapa.csv` es el agregado de consumo.
- **Formato canónico objetivo:** Parquet particionado por `distrito/anio/categoria`
  (hoy es CSV — ver HUECO #3). Mantener CSV como espejo humano.
- **Secretos:** nunca en el repo. Credenciales AWS por profile (`idetec`, cuenta
  851679891137) / Secrets Manager. El CI/CD se autentica por **OIDC** (sin claves).
- **Sin PII de votantes.** Solo agregados públicos por unidad (mesa/circuito/municipio).

## 5. Contrato de datos (resumen; detalle y schema real en `docs/02`)

Toda fila debe responder: **¿qué elección, qué cargo, qué unidad, qué agrupación,
cuántos votos, de qué fuente?** El dataset real ya trae la columna `fuente`
(`dine`/`junta`) como linaje mínimo. **Deuda del contrato:** falta linaje fino
(`fuente_url`, `fecha_extraccion`, `hash`) y no está garantizado un `agrupacion_raw`
preservado — verificar y completar (ver `docs/02 §deuda`).

## 6. Definición de "Terminado" (el auditor)

Una tarea/PR NO está terminada hasta cumplir lo que aplique:

- [ ] **Trazabilidad:** cada dato mapea a una fuente (`fuente` como mínimo; ideal
      `fuente_url` + `fecha_extraccion`).
- [ ] **Reproducible:** hay script que regenera la salida desde `raw`. Nada editado a
      mano sin script. (Los scripts del dataset actual NO existen — HUECO #5; se
      reconstruyen en `ingest/`.)
- [ ] **Validado:** pasa `core/validadores.py`. Los totales cierran o el desvío está
      documentado (DINE provisorio queda 0,4–7% bajo el definitivo: es esperable).
- [ ] **Cobertura declarada:** el módulo dice qué años/cargos/unidades cubre y cuáles
      no (con motivo). Los HUECOS de §2 se mencionan si se tocan.
- [ ] **Sin secretos** ni PII.
- [ ] **Docs actualizados** y decisión registrada si cambió el esquema o el criterio.

## 7. Controles de calidad mínimos (en `core/validadores.py`)

1. **Cierre de totales** por unidad y elección (tolerar desvío provisorio↔definitivo).
2. **Continuidad temporal:** listar `(municipio, cargo)` sin datos donde hubo elección
   → hoy detecta el hueco 1983-2002 y el 2009 (solo concejales).
3. **Duplicados:** unicidad por `(año, eleccion_tipo, cargo, unidad, agrupacion_id)`.
4. **Sanidad de %:** ninguna agrupación >100%; suma ≈100 por unidad.
5. **Linaje de agrupaciones:** todo `agrupacion_id` resoluble en el diccionario.

## 8. Cómo trabaja cada persona/módulo

- Trabajás en una carpeta de módulo; `core/` es compartido (no tocar sin coordinar).
- El crudo se guarda en `raw/<fuente>/<municipio>/` **antes** de transformar.
- Idempotencia: correr el ETL dos veces da lo mismo.
- Ante duda de un dato histórico, cruzar dos fuentes y anotar el desempate.

## 9. Guardrails de dominio (Argentina)

- **Normalización de agrupaciones a lo largo del tiempo = problema central**
  (PJ→FpV→UxP/Fuerza Patria; UCR→Cambiemos→JxC→LLA como nuevo eje). El valor del
  dataset depende de esto.
- **Provisorio (DINE) vs definitivo (Junta):** declarar cuál se usa por fila; no
  mezclar sin marcar. La brecha 0,4–7% es conocida y esperable.
- **Cambio de circuitos 2019:** mitigado con `circuito_padre`; respetarlo al comparar
  series por circuito pre/post 2019.
- **Verificar sección electoral** de cada municipio por año (hubo reordenamientos).

## 10. Roadmap corto

1. **Hecho:** dataset 2003–2025 Pilar + San Fernando (DINE + Junta), curated + docs.
2. **Siguiente (cierra el contrato original):** sumar **1983–2002 vía Andy Tow**;
   migrar a **Parquet particionado**; **habilitar versionado** S3.
3. Capa de consulta (API read-only) sobre `vista_mapa` / Parquet.
4. Features de Inteligencia; luego Defensa.
