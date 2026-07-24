# Datos electorales — Pilar y San Fernando (2003–2025)

## Archivos

| Archivo | Qué es | Para quién |
|---|---|---|
| `vista_mapa.csv` | Agregado por circuito × elección × agrupación. **Es lo que consume el mapa.** | Equipo frontend/mapa |
| `consolidado.csv` | Tabla de hechos completa, nivel mesa × agrupación (1,2M filas) | Análisis / Aurora / Bedrock |
| `raw/` | Archivos originales tal como los publican las fuentes | Reprocesamiento |

## vista_mapa.csv (contrato para el mapa)

Una fila = votos de una agrupación en un circuito para una elección.

- `municipio`: `pilar` | `san_fernando`
- `año`: 2011–2025 (sept 2025 NO está por circuito, ver limitaciones)
- `eleccion_tipo`: `GENERAL` | `PASO` | `SEGUNDA_VUELTA`
- `cargo_nombre`: `PRESIDENTE`, `GOBERNADOR`, `INTENDENTE`, `DIPUTADOS_NAC`, `SENADORES_NAC`, `DIPUTADOS_PROV`, `SENADORES_PROV`, `CONCEJALES`, `MERCOSUR_NAC`, `MERCOSUR_REG`
- `circuito_id`: **clave de join con el GeoJSON**. Canónico: 5 caracteres, sin ceros extra a la izquierda (`00768`, `0768A`). Los polígonos oficiales: CNE, mapa2.electoral.gov.ar
- `agrupacion_nombre`: nombre de la fuerza; filas con `porcentaje` vacío son votos no positivos (`BLANCO`, `NULO`, etc. en esta columna)
- `votos`, `porcentaje` (sobre positivos del circuito), `gana` (true = fuerza más votada del circuito)
- `granularidad`: `circuito` | `municipio` — **regla de render**: si el año/cargo elegido solo tiene filas `municipio` (sept 2025, años 2003–2009), pintar todo el partido uniforme con ese valor. Así el mapa nunca queda vacío.
- `circuito_padre`: para años pre-2019, pintar cada polígono actual con el valor de su `circuito_padre` (los circuitos actuales `0768A/B/C...` heredan del histórico `00768`).

El filtro por año de la UI = `WHERE año = X AND cargo_nombre = Y AND eleccion_tipo = 'GENERAL'`.

## Limitaciones conocidas (leer antes de reportar bugs)

1. **Los circuitos cambiaron en 2019**: Pilar pasó de 6 a 21 (subdivisión 768 → 0768A/B/C...), San Fernando de 16 a 15 (2023). Mitigado con `circuito_padre` (ver arriba): años viejos se pintan al nivel del circuito padre. No existe re-tabulación oficial de años viejos con los circuitos actuales.
2. **Sept 2025 (senadores prov. + concejales) solo existe a nivel municipio** (fuente Junta, definitivo; el sitio por mesa fue dado de baja — investigación completa en CONTEXTO.md; hay pedido de información en curso). Mitigado con `granularidad='municipio'` (ver arriba). Bonus: 2003–2009 también disponibles a nivel municipio.
3. **DINE = escrutinio provisorio**: los totales son 0,4–7% menores que el definitivo (validado contra la Junta en 36 combinaciones año/cargo; la diferencia es siempre en esa dirección y es normal). Para totales municipales exactos usar `fuente=junta_pba` del consolidado.
4. Junta 2009 solo tiene Concejales (hueco de la fuente).

## Fuentes

- **DINE** (resultados.mininterior.gob.ar): nacional + provincial/municipal en años simultáneos, por mesa y circuito, 2011–2025. API documentada. Script: `descarga_dine.py`
- **Junta Electoral PBA** (juntaelectoral.gba.gov.ar): provinciales/municipales 2003–2025, definitivo, nivel municipio. Script: `descarga_junta_pba.py`
- ETL: `etl_consolidar.py` (normaliza 26 variantes de formato, ids de circuito canónicos, cargos unificados)

## QA ejecutado (jul 2026)

Sin duplicados reales (las multi-filas de PASO son listas internas), sin votos negativos ni nulos, participación por mesa mediana 79,8% y ninguna >100%, cobertura completa según calendario electoral, consistencia DINE↔Junta verificada en todos los años solapados.

## Layout S3 sugerido

```
s3://electoral-data-851679891137/electoral/
  raw/dine/<municipio>/<archivo>.csv     (crudos tal como los publica cada fuente)
  raw/junta_pba/<municipio>/<año>.csv
  procesados/consolidado.csv             (→ carga a Aurora)
  procesados/vista_mapa.csv              (→ precalculado para la app / DynamoDB)
  docs/README_datos.md
  docs/resumen_exploratorio.md
```
