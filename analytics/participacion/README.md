# analytics/participacion — Participación electoral (deuda #6)

Extrae del bucket un valor que estaba latente y no se usaba: la **participación
electoral** (padrón vs votos emitidos) y el **desglose del voto** (positivo / blanco
/ nulo / otros), por circuito. NO usa ninguna fuente nueva: sale de `mesa_electores`
y `votos_tipo` que ya vivían en el consolidado (nivel mesa, DINE).

Produce el dataset curado `procesados/vista_participacion/vista_participacion.csv`.

## Cómo regenerar

```bash
cd analytics/participacion
AWS_PROFILE=idetec ./build.sh      # corre vista_participacion.sql y copia el CSV curado
```

Requiere `DataStack` desplegado y la tabla `consolidado_parquet` cargada (ver
`../parquet/`). Se apoya en Athena: corre el SELECT y copia su resultado a la clave
curada (no usa CTAS porque el workgroup `politeia` impone la ubicación de salida).

## Esquema (`vista_participacion.csv`)

| Columna | Qué es |
|---|---|
| `municipio`, `anio`, `eleccion_tipo`, `cargo`, `circuito_id` | unidad-elección |
| `mesas` | cantidad de mesas agregadas (señal de robustez de la fila) |
| `padron` | electores registrados (suma de `mesa_electores` por mesa) |
| `emitidos` | votos emitidos (todos los tipos) |
| `participacion` | `100 * emitidos / padron` |
| `positivos`, `blancos`, `nulos`, `otros` | votos por tipo (`otros` = impugnado+recurrido+comando+…) |
| `pct_positivo`, `pct_blanco`, `pct_nulo` | % sobre emitidos |

2114 filas (2026-07-24).

## Cobertura y LIMITACIONES (leer antes de usar)

- **Solo 2011–2025.** El padrón (`mesa_electores`) viene de **DINE por mesa**; los
  años de **Junta (2003–2009) no tienen padrón** en el bucket → sin participación ahí.
- **DINE es provisorio.** Los totales pueden quedar algo por debajo del definitivo.
- **Outliers bajos a nivel circuito.** Un puñado de filas (sobre todo **PASO** y
  **circuitos chicos** de San Fernando, ej. `0882A`, `00881`) dan participación
  anormalmente baja (~30–40%). Verificado que **no** son mesas de extranjeros (son
  NATIVOS). No se pudo fijar una causa única (comportamiento por categoría en PASO,
  circuitos chicos con padrón/voto desalineado). **Recomendación:** para participación
  robusta, leer a **nivel municipio** (agregando circuitos, dominan los grandes y
  completos); a nivel circuito, usar la columna `mesas` para juzgar y tratar los valores
  extremos con cuidado. NO es un dato para publicar sin este contexto.
- **`mesa_tipo` con naming sucio** en el origen (`NATIVOS`/`NATIVO`,
  `EXTRANJEROS`/`EXTRANJERO`, y vacíos) — no afecta este cálculo (se agrega por mesa),
  pero queda anotado como deuda de limpieza del consolidado.

## Qué NO hace todavía

- No lo consume el mapa/API aún (Fase 2: capa "mapa de participación" = endpoint +
  front). Este entregable es el **dato**, listo para esa capa.
- No cubre 2003–2009 (falta padrón). Para eso haría falta el padrón histórico (otra fuente).
