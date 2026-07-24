# data_pipeline — material original del dataset (pendiente de reorganizar)

Esta carpeta contiene los **scripts originales y la documentación** que generaron
el dataset electoral que hoy vive en S3
(`s3://electoral-data-851679891137/electoral/`) y que consume la app en producción.

Hasta ahora este material vivía **solo en la máquina local** del responsable de
datos (fuera de git). Por eso `docs/06_estado_bucket.md` y `docs/DECISIONES.md`
lo daban por perdido (el "HUECO #5" — dataset no reproducible). **No estaba
perdido: estaba sin versionar.** Esto lo sube al repo.

## Estado: SIN RECONCILIAR con el resto del repo

Este es un **landing zone**. El contenido se solapa con carpetas que ya existen
y hay que decidir qué se fusiona y qué se archiva. **No asumir que esta es la
ubicación final de nada.** Solapamientos conocidos:

- `descarga_dine.py`, `descarga_junta_pba.py`, `etl_consolidar.py` se pisan con
  `ingest/` (donde se estaba *reconstruyendo* esta misma ingesta como Lambdas).
  Probablemente se fusionen ahí.
- `README_datos.md` y `resumen_exploratorio.md` se solapan con `docs/02` y
  `docs/06`.
- `CONTEXTO.md` es el documento de contexto de las sesiones de trabajo previas
  (Cowork). Solapa parcialmente con `CLAUDE.md` y los `docs/`.
- `partidos_elecciones.xlsx` alimenta la normalización de agrupaciones; su
  `grupo_canonico` podría volcarse a `core/agrupaciones/diccionario.csv` en vez
  de conservar el xlsx.

## Qué NO está acá (a propósito)

Los **datos** (`consolidado.csv` ~150 MB, `vista_mapa.csv`, `raw/`) NO se suben:
ya tienen lugar canónico en S3. Duplicarlos en git sería peso muerto. Los
scripts los regeneran; el crudo está en el bucket.

## Inventario

| Archivo | Qué es |
|---|---|
| `descarga_dine.py` | Baja crudos DINE (nacional, 2011-2025, por mesa) a `raw/dine/`. |
| `descarga_junta_pba.py` | Baja crudos Junta PBA (2003-2025, por municipio) a `raw/junta_pba/`. |
| `etl_consolidar.py` | Unifica los crudos → `consolidado.csv` + `vista_mapa.csv`. |
| `README_datos.md` | Diccionario de datos (contrato de `vista_mapa.csv`). |
| `resumen_exploratorio.md` | Hallazgos del dataset (participación, corte de boleta, etc.). |
| `CONTEXTO.md` | Contexto completo de las sesiones de trabajo previas. |
| `pedido_informacion_junta.md` | Borrador de pedido de acceso a la info (sept-2025 por circuito). |
| `partidos_elecciones.xlsx` | Listado de agrupaciones para normalización. |

Para reproducir el dataset desde cero, correr en orden: `descarga_dine.py`,
`descarga_junta_pba.py`, `etl_consolidar.py`.
