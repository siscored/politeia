# 03 · MVP — Recopilación de datos (qué está hecho / qué falta)

## Estado: PARCIALMENTE LOGRADO

El objetivo era un dataset histórico limpio, normalizado y trazable de Pilar y San
Fernando, ejecutivo + legislativo, **desde 1983**. Estado real en el bucket:

| Aspecto | Objetivo | Real (bucket) | ✔/✖ |
|---|---|---|---|
| Municipios | Pilar + San Fernando | Pilar + San Fernando | ✔ |
| Cargos ejecutivos | pres/gob/int | pres/gob/int | ✔ |
| Cargos legislativos | dip/sen nac+prov, concejal | presentes (+ Mercosur) | ✔ |
| Rango temporal | **1983 → 2025** | **2003 → 2025** | ✖ falta 1983-2002 |
| Granularidad | circuito | circuito (DINE) / municipio (Junta y 09-2025) | ~ |
| Trazabilidad | fuente por fila | columna `fuente` (dine/junta) | ~ (falta linaje fino) |
| Formato | Parquet particionado | CSV (consolidado 150 MB) | ✖ deuda #3 |
| Curado listo | sí | `consolidado.csv` + `vista_mapa.csv` | ✔ |
| Documentado | sí | `docs/README_datos.md` + `resumen_exploratorio.md` | ✔ |

**Veredicto del auditor:** el trabajo hecho es sólido y bien documentado, pero **no
cierra el contrato original**: falta 1983-2002 y la migración a Parquet. El resto es
deuda menor.

## Lo que FALTA para cerrar el contrato

### 1. Cubrir 1983–2002 (el hueco grande)
- **Fuente:** Atlas Electoral de Andy Tow (`andytow.com`) — es la única con
  presidencial/gobernador/legislativo provincial y **cargos municipales 1983-2011**
  por sección/circuito. Ver `docs/05`.
- **Trabajo:** extractor `ingest/andytow/` → `raw/andytow/<municipio>/` → normalizar
  con el mismo `core/` → agregar a `consolidado` y `vista_mapa`.
- **Riesgo:** verificar continuidad territorial y creación de municipios vecinos en
  los '90 antes de empalmar series largas.

### 2. Migrar a Parquet particionado (deuda #3, mayor impacto en costo de consulta)
- `consolidado.csv` (150 MB, 1 archivo) → Parquet particionado por
  `distrito/anio/categoria`. Mantener el CSV como espejo humano.
- Habilita Athena/Aurora eficiente; hoy cada query escanea el CSV entero.

### 3. Completar linaje fino
- Agregar `fuente_url`, `fecha_extraccion`, `hash_registro` en el próximo ETL.
- Verificar que `agrupacion_raw` (nombre original) esté preservado; si el ETL lo pisó,
  recuperarlo de `raw/`.

### 4. Habilitar S3 Versioning
- Hoy una recarga pisa el histórico sin rastro. Para un "dataset fuente de verdad",
  activar versionado en el bucket.

### 5. Cerrar reproducibilidad
- Los scripts (`descarga_dine.py`, `descarga_junta_pba.py`, `etl_consolidar.py`) y el
  `CONTEXTO.md` viven en el repo original, **no en el bucket**. Referenciar
  repo + commit en `docs/` para que la trazabilidad quede completa.

## Pipeline (idempotente) — el que ya corre + lo pendiente

```
raw/dine/<muni>/<año>_<paso|generales>_<cargo>.csv     (2011-2025, mesa)   [hecho]
raw/junta_pba/<muni>/<año>.csv                          (2003-2025, muni)   [hecho]
raw/andytow/<muni>/...                                  (1983-2011)         [FALTA]
      │  parse + normalizar (core/)  + validar (core/validadores)
      ▼
procesados/consolidado.csv   (hechos, mesa)     → objetivo Parquet
procesados/vista_mapa.csv    (agregado mapa)    → consumo frontend "Comando IA"
```

## Definition of Done del MVP (checklist actualizado)

- [x] Pilar + San Fernando, ejecutivo + legislativo, **2003-2025**, curado + docs.
- [x] Curated consumible (`vista_mapa.csv` con `gana`, `granularidad`, `circuito_padre`).
- [x] Limitaciones documentadas (provisorio↔definitivo, circuitos 2019, 09-2025).
- [ ] **1983-2002** (Andy Tow).
- [ ] Parquet particionado.
- [ ] Linaje fino + `agrupacion_raw` verificado.
- [ ] Versionado S3 activado.
- [ ] Repo/commit de los scripts referenciado en `docs/`.

## Reparto sugerido para cerrar
- **A — Andy Tow 1983-2002/2011** (extractor + normalización + empalme).
- **B — Migración Parquet + partición + validación de totales.**
- **C — `core/`** (esquema, validadores, diccionario de agrupaciones; da soporte a A y B).
- **D — Infra:** versionado S3, referencia de scripts, alias `procesados`↔`curated`.
