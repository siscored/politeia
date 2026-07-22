# Inventario de infraestructura AWS — POLITEIA (OT-001)

> Relevamiento de **solo lectura** ejecutado el 21-jul-2026 con AWS CLI.
> Cuentas: `fsc` = 851679891137 · `personal` = 058264513602.
> **Hallazgo central:** la topología real está **invertida** respecto de lo que
> asume el CLAUDE.md de OT-000: el **MVP vive en `fsc`/us-east-1** y el
> **mockup vive en `personal`/sa-east-1**. Ver §3 Deudas.

---

## 1. Inventario por cuenta / región / servicio

### 1.1 Cuenta `fsc` (851679891137) — us-east-1

| Servicio | Recurso | Detalle |
|---|---|---|
| Amplify | **`d3w3982cnzzi0m` · politeia-web (el MVP)** | Creada 21-jul-2026. `repository: null` (deploy manual, sin repo GitHub conectado). `platform: WEB`, `buildSpec: null`. Branch `main`: stage PRODUCTION, `enableAutoBuild: true`, **`enablePullRequestPreview: false`**, framework null. |
| Amplify | `d29gr7w00yt0yj` idetec-develop · `de16eizfl5ss7` idetec (repo github.com/siscored/idetec) · `d2pb5joy3x4qmd` y `d3b5ole2vktavu` "fsc" | Ajenas a POLITEIA (idetec / web institucional). |
| S3 | `electoral-data-851679891137` | **Versionado: Enabled** (habilitado en este setup, 21-jul-2026). Contenido bajo `electoral/` (181 objetos, ~375 MB): ver tabla abajo. |
| Lambda | **`politeia-api-mapa`** (python3.12) | Handler `handler.lambda_handler`, 512 MB, timeout 30 s. Env: `DATA_BUCKET=electoral-data-851679891137`, `VISTA_MAPA_KEY=electoral/procesados/vista_mapa/vista_mapa.csv`. **Function URL pública (AuthType NONE):** `https://vlcwwo3krujfmwxe735xwppmmq0czzga.lambda-url.us-east-1.on.aws/`. |
| Lambda | **`politeia-ingest-dine`** (python3.12) | Ingesta DINE (reconstrucción del pipeline, HUECO #5 del contrato de datos). |
| Lambda | `PoliteiaGithubOidc-CustomAWSCDKOpenIdConnect...` · `PoliteiaData-CustomS3AutoDeleteObjects...` | Custom resources de CDK de los stacks POLITEIA. |
| Lambda | ~26 funciones `idetec-*`, 5 `*-dev` (moviplay), `getFinalResults-dev`, etc. | Ajenas a POLITEIA. |
| API Gateway v2 | `idetec-api` (avhqole6xe) · `Idetec_Main_API` (dwamys78hk) | Ajenas. **No existe API Gateway de POLITEIA**: el MVP usa Lambda Function URL. |
| API Gateway v1 | `moviplayapi` (9r65z1017l) | Ajena. |
| DynamoDB | 13 tablas `Idetec*` + 3 de moviplay | Ajenas. **Sin tablas POLITEIA.** |
| CloudFormation | **`PoliteiaWeb`, `PoliteiaApi`, `PoliteiaIngest`, `PoliteiaData`, `PoliteiaGithubOidc`**, `CDKToolkit` | Stacks CDK de POLITEIA (deploy por OIDC desde GitHub Actions). Resto: `amplify-fsc-dev-*` (ajenos). |

**S3 `electoral/` resumido por prefijo:**

| Prefijo | Objetos | Tamaño |
|---|---|---|
| `electoral/` (raíz) + `docs/` | 4 | < 0,1 MB |
| `procesados/consolidado/` | 1 | 149,7 MB |
| `procesados/vista_mapa/` (vista_mapa.csv — contrato del mapa) | 1 | 2,6 MB |
| `procesados/geo/` | 1 | 0,3 MB |
| `raw/dine/` | 148 | 221,9 MB |
| `raw/junta_pba/` | 25 | 0,1 MB |

### 1.2 Cuenta `personal` (058264513602) — sa-east-1

| Servicio | Recurso | Detalle |
|---|---|---|
| Amplify | **`d1pthxba9jy105` · politeia (el MOCKUP)** | `repository: null`. Branch `main`: stage NONE, `enableAutoBuild: true`, `enablePullRequestPreview: false`. Congelado como referencia visual. |
| Lambda / API GW / DynamoDB / CloudFormation | — | **Vacío.** No hay más recursos en sa-east-1. |

### 1.3 Cuenta `personal` (058264513602) — us-east-1

| Servicio | Recurso | Detalle |
|---|---|---|
| Amplify | `siscored-web`, `siscored-admin-web`, `evaluador-ideas`, `prompt-qr-web`, `OniraDashboard` | Todas ajenas a POLITEIA. |
| Lambda | 19 funciones (siscored-*, Onira*, evaluador-ideas, prompt-qr-eval, adapters de WhatsApp/Telegram, etc.) | Ajenas. |
| API Gateway v2/v1 | 8 HTTP APIs + 2 REST APIs (siscored/telegram/etc.) | Ajenas. |
| DynamoDB | 14 tablas (siscored-admin-*, Turnos, Pacientes, etc.) | Ajenas. |
| CloudFormation | `siscored-admin` | Ajena. |

**Conclusión:** no hay NINGÚN recurso POLITEIA en la cuenta `personal` fuera del
mockup. Todo el MVP (Amplify + Lambdas + stacks CDK + bucket) está en `fsc`/us-east-1.

---

## 2. Mapa front → endpoint → lambda → origen de datos

Front del MVP: `web/` (React + Vite). Único cliente HTTP: `web/src/api.js`.

| Pantalla / módulo | Endpoint | Lambda | Origen de datos | Clasificación |
|---|---|---|---|---|
| **Inteligencia** (`web/src/modules/Inteligencia.jsx`) — `fetchMeta()` y `fetchMapa(distrito, anio, cargo, tipo)` | Function URL `https://vlcwwo3krujfmwxe735xwppmmq0czzga.lambda-url.us-east-1.on.aws/` (override por `VITE_API_URL`) | `politeia-api-mapa` (fsc/us-east-1) | `s3://electoral-data-851679891137/electoral/procesados/vista_mapa/vista_mapa.csv` | ✅ **DATO REAL** (backend) |
| Capa geográfica del mapa (`web/src/circuitos.json`, 263 KB, bundled) | — (estático en el bundle) | — | Geometrías de circuitos empaquetadas en el front | ⚠️ Estático en front |
| Colores/familias políticas (`web/src/families.js`) | — | — | Hardcodeado en front (duplica `core/agrupaciones/diccionario.csv`) | ⚠️ Hardcodeado |
| **Resumen** (`Resumen.jsx`: KPIS, PULSO, ALERTAS, BRECHA) | — | — | `web/src/data/mock.js` | ❌ MOCK |
| **Defensa** (`Defensa.jsx`: ESCUCHA, PROTOCOLO) | — | — | `web/src/data/mock.js` | ❌ MOCK |
| **Posicionamiento** (`Posicionamiento.jsx`: MOTORES, SHARE_VOICE, AGENDA_MOTORES) | — | — | `web/src/data/mock.js` | ❌ MOCK |
| **Producción** (`Produccion.jsx`: PRODUCCION_FLOW, FUNNEL) | — | — | `web/src/data/mock.js` | ❌ MOCK |
| **Personalización** (`Personalizacion.jsx`: SEGMENTOS, RECLAMOS) | — | — | `web/src/data/mock.js` | ❌ MOCK |

Resumen: **1 de 6 módulos** (Inteligencia/mapa) consume datos reales; los otros 5
son mock de presentación.

---

## 3. Deudas y hallazgos

1. **Topología invertida vs. lo documentado (OT-000).** El CLAUDE.md de OT-000
   dice "MVP → profile `personal` → sa-east-1" y "el MVP quedó en São Paulo por
   accidente". Lo relevado es lo contrario: **MVP en `fsc`/us-east-1**, **mockup
   en `personal`/sa-east-1**. El que quedó en São Paulo es el mockup (aceptable:
   está congelado). Corregir la tabla del CLAUDE.md antes de mergear OT-000, o
   emitir OT correctiva.
2. **Amplify del MVP sin repo GitHub conectado** (`repository: null`, deploy
   manual). "Merge = deploy automático" hoy no se cumple. Conectar
   `github.com/siscored/politeia` (branch `main`) a la app `d3w3982cnzzi0m` es
   una OT pendiente. Nota: existe `PoliteiaGithubOidc` + `.github/workflows/`,
   así que parte del CI/CD ya deploya por OIDC; falta cerrar el circuito del front.
3. **PR previews deshabilitados** en la branch `main` del MVP
   (`enablePullRequestPreview: false`). Habilitarlos requiere además conectar el
   repo (punto 2). Paso manual del owner; no se tocó (regla de solo lectura).
4. **Cognito ausente / API pública.** La Function URL de `politeia-api-mapa` es
   `AuthType: NONE` (cualquiera puede pegarle). Aceptado para demo; para
   producción: auth (Cognito o IAM) + CORS restringido + rate limiting.
5. **Unificación de cuentas.** El único recurso POLITEIA fuera de `fsc` es el
   mockup (cuenta `personal`). Decidir si se migra/archiva; mientras tanto, el
   repo `politeia-mockup` congela el código.
6. **`families.js` duplica el diccionario de agrupaciones en el front**, contra
   la convención "nunca mapear siglas a mano en el front". Deuda: servir
   familia/color desde el backend (deriva de `core/agrupaciones/diccionario.csv`).
7. **Recursos POLITEIA conviven con idetec/moviplay** en la cuenta fsc (misma
   cuenta, sin separación por cuenta/OU). Riesgo de blast radius; evaluar
   separación futura.
8. **`buildSpec: null` y framework sin detectar** en la app Amplify del MVP —
   consistente con deploy manual de artefactos; se regulariza al conectar el repo.
9. **DINE por mesa (raw/dine, 148 objetos, 222 MB) vs consolidado CSV único de
   150 MB** — la migración a Parquet particionado (HUECO #3 del contrato de
   datos) sigue pendiente.
