# 06 · Estado real del bucket S3 (inventario 19-jul-2026)

Snapshot del bucket fuente de verdad, para que cualquiera entienda qué hay sin tener
que volver a inspeccionar. Inspección hecha en modo lectura (profile `fsc`).

## Coordenadas
- **Bucket:** `s3://electoral-data-851679891137`
- **Cuenta:** 851679891137 · **Región:** us-east-1
- **Cifrado:** SSE-S3 (AES256) · **Versionado:** DESHABILITADO
- **Objetos:** 180 · **Tamaño:** 374,3 MB · **Carga:** batch único 19-jul-2026
- Consola: https://us-east-1.console.aws.amazon.com/s3/buckets/electoral-data-851679891137

## Árbol (prefijo raíz `electoral/`)
```
electoral/
├── docs/
│   ├── README_datos.md            (contrato de datos del dataset)
│   └── resumen_exploratorio.md    (hallazgos + argumento del nivel circuito)
├── procesados/                    (= curated)
│   ├── consolidado.csv            (19 col, hechos nivel mesa, ~150 MB)
│   └── vista_mapa.csv             (11 col, agregado para el mapa)
├── raw/
│   ├── dine/<municipio>/          (por mesa, 2011-2025)
│   │   └── <año>_<paso|generales>_<cargo>.csv
│   └── junta_pba/<municipio>/     (definitivo por municipio, 2003-2025)
│       └── <año>.csv
```

## Cobertura raw DINE (archivos por año)
| Año | Pilar | S. Fernando | Cargos típicos |
|-----|-------|-------------|----------------|
| 2011 | 11 | 11 | pres, gob, int, dip/sen nac+prov |
| 2013 | 6 | 6 | legislativas |
| 2015 | 15 | 15 | + mercosur + 2ª vuelta pres |
| 2017 | 8 | 8 | legislativas |
| 2019 | 10 | 10 | ejecutivas + legislativas |
| 2021 | 6 | 6 | legislativas |
| 2023 | 17 | 17 | todo + mercosur + 2ª vuelta |
| 2025 | 1 | 1 | dip nac (resto vía Junta) |

Junta PBA: 2003-2025 a nivel municipio (hueco 2009 = solo concejales).

## Limitaciones ya documentadas en el dataset
- **DINE es provisorio:** queda 0,4-7% por debajo del definitivo de la Junta.
- **Cambio de circuitos 2019:** mitigado con `circuito_padre` en `vista_mapa`.
- **Sept-2025:** solo a nivel municipio para lo no cubierto por DINE.

## Hallazgo de valor (del resumen exploratorio)
El nivel circuito cambia la lectura: p.ej. en **Pilar 2025, Fuerza Patria ganó el
municipio pero LLA ganó 13 de 21 circuitos**, con brechas internas de hasta 44 puntos.
Esto justifica que la unidad analítica del producto sea el **circuito**, no el municipio.

## Cumplimiento del contrato POLITEIA
| Convención | En el bucket | ¿OK? |
|---|---|---|
| `raw/` | `electoral/raw/` (por fuente→municipio) | ✔ |
| `curated/` | `electoral/procesados/` | ✔ (alias, solo cambia el nombre) |
| `docs/` | `electoral/docs/` | ✔ |
| Trazabilidad por fila | columna `fuente` | ~ (falta linaje fino) |
| Provisorio vs definitivo declarado | sí | ✔ |
| Cobertura y limitaciones documentadas | sí | ✔ |

## Recomendaciones (no aplicadas — requieren decisión)
1. **Alias `procesados/` ↔ `curated/`:** dejar una línea en `docs/` que lo fije, o
   renombrar. Evita ambigüedad entre repos. (Registrado como alias oficial acá.)
2. **Parquet particionado:** `consolidado.csv` (150 MB, 1 archivo) → Parquet por
   `distrito/anio/categoria`. Mayor impacto en costo de consulta. Mantener CSV espejo.
3. **Versionado S3:** activar para proteger el "fuente de verdad" de sobrescrituras.
4. **Referenciar scripts:** `descarga_dine.py`, `descarga_junta_pba.py`,
   `etl_consolidar.py` y `CONTEXTO.md` viven en el repo, no en el bucket → citar
   repo/commit en `docs/` para cerrar la reproducibilidad.
5. **Cerrar 1983-2002** con Andy Tow (ver `docs/03` y `docs/05`).
