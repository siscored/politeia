# analytics/internas — Internas de las PASO (dimensión latente del bucket)

Expone algo que ya estaba en el consolidado y nadie miraba: las **listas internas**
de cada partido en las PASO (`lista_numero`/`lista_nombre`). El mapa suma las listas
de un partido y las esconde; acá se ve **quién ganó la interna** de cada fuerza.

Produce `procesados/vista_internas/vista_internas.csv`. Sin fuentes nuevas.

## Cómo regenerar

```bash
cd analytics/internas
AWS_PROFILE=idetec ./build.sh
```

Requiere `DataStack` desplegado y `consolidado_parquet` cargada (ver `../parquet/`).

## Esquema

| Columna | Qué es |
|---|---|
| `municipio`, `anio`, `cargo`, `agrupacion_nombre` | partido en una PASO |
| `lista_numero`, `lista_nombre` | la lista interna |
| `votos` | votos de la lista |
| `votos_partido` | total del partido (suma de sus listas) |
| `pct_en_partido` | `100 * votos / votos_partido` |
| `gana_interna` | `true` si es la lista más votada del partido |
| `listas_en_partido` | cuántas listas compitieron |

1147 filas (2026-07-24).

## Ejemplo real

Pilar 2021, interna de **CONCEJALES de JUNTOS** (3 listas):
`B` 38.52% (22.497, **gana**) · `A` 37.55% (21.929) · `DAR EL PASO` 23.92%.

## Cobertura y límites

- **Solo PASO** con voto positivo y lista nombrada (~2011–2025; GENERAL casi no trae
  lista). Partidos que fueron con **lista única** aparecen con `listas_en_partido=1`
  (no hubo interna real).
- Hereda los caveats de la fuente DINE (provisorio) y de `consolidado_parquet`.

## Qué NO hace todavía

- No lo consume el front aún (posible Fase 2: panel de internas al tocar un partido).
