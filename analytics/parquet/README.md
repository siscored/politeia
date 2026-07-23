# analytics/parquet — Migración de `consolidado` a Parquet particionado (HUECO #3)

Cierra la deuda de formato analítico del contrato: `consolidado.csv` (1 archivo de
~150 MB, escaneado entero en cada query) → **Parquet SNAPPY particionado** por
`municipio / anio / categoria`, consultable por Athena con **partition projection**.

Decisiones de diseño (por qué `municipio` y no "distrito", etc.): `docs/DECISIONES.md`
(2026-07-23). Contexto del contrato: `docs/03 §migración`, `CLAUDE.md §2` (HUECO #3).

## Resultado (2026-07-23)

| | CSV `consolidado` | Parquet `consolidado_parquet` |
|---|---|---|
| Filas | 1.200.301 | 1.200.301 ✅ |
| Suma de votos | 27.095.945 | 27.095.945 ✅ |
| Tamaño en S3 | 149.7 MB | **3.55 MB** (96 archivos, 1 por partición) |
| Bytes escaneados por "Pilar 2023 PRESIDENTE" | ~157 MB | **~41 KB** (~3800× menos) |

## Cómo regenerar (idempotente)

Requiere `DataStack` desplegado (base Glue `politeia_electoral`, workgroup Athena
`politeia`, bucket de resultados) y perfil AWS con acceso.

```bash
cd analytics/parquet
AWS_PROFILE=idetec ./run.sh 01_create_consolidado_parquet.sql   # tabla + projection
AWS_PROFILE=idetec ./run.sh 02_load_consolidado_parquet.sql     # carga en 4 tandas
AWS_PROFILE=idetec ./run.sh 03_validate.sql                     # totales cierran
```

`01_create` hace `DROP + CREATE` (recrea el metadato Glue sin borrar los Parquet en
S3). `02_load` batchea el `INSERT INTO` porque Athena limita 100 particiones por query.

## Claves S3

| Rol | Ruta |
|---|---|
| Fuente CSV (tabla `consolidado`) | `electoral/procesados/consolidado/consolidado.csv` |
| **Parquet particionado** | `electoral/procesados/parquet/consolidado/${municipio}/${anio}/${categoria}/` |

El prefijo `parquet/` es hermano de `consolidado/` para que el crawler CSV del
`DataStack` no lo levante como tabla de texto.

## Qué NO hace (alcance honesto)

- No toca `vista_mapa` (el API del mapa sigue leyendo su CSV, chico y en el path
  crítico — Athena no va en ese camino).
- No cierra el linaje fino (`fuente_url`/`fecha_extraccion`/`hash` — deuda #3.3).
- El **refresh automático** (correr esto tras cada publicación del pipeline de
  Step Functions) queda como follow-up; hoy es manual con estos scripts.
