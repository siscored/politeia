# ingest/ — Extractores de datos (run plane)

Cada fuente baja su crudo a `raw/<fuente>/...` **antes** de transformar (raw-first),
con linaje por objeto (`fuente_url`, `fecha_extraccion`, `sha256`). Son Lambdas
desplegadas por CDK (`infra/stacks/ingest_stack.py`) y disparadas por EventBridge.

> Los scripts que generaron el dataset actual no se conservaron (HUECO #5). Todo lo
> de acá se reconstruye desde cero.

## Fuentes
| Carpeta | Fuente | Estado |
|---|---|---|
| `dine/` | Dirección Nacional Electoral (provisorio, por mesa) | ✅ Lambda `politeia-ingest-dine` (falta catálogo de URLs) |
| `junta_pba/` | Junta Electoral PBA (definitivo, por municipio) | ⏳ pendiente |
| `andytow/` | Atlas de Andy Tow (1983-2002/2011) | ⏳ pendiente (cierra HUECO #1) |

El contrato de trabajo del repo está en el `CLAUDE.md` de la raíz.
