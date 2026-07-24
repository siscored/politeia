-- Deuda #6 · Participación electoral por circuito, derivada del bucket (sin fuentes nuevas).
--
-- Una fila por (municipio, anio, eleccion_tipo, cargo, circuito): padrón, votos
-- emitidos, participación %, y desglose positivo/blanco/nulo/otros con sus %.
-- Fuente: `consolidado_parquet` (mesa DINE). `mesa_electores` = padrón por mesa.
--
-- COBERTURA: solo 2011-2025 (DINE trae padrón por mesa). 2003-2009 (Junta, nivel
-- municipio) NO tienen padrón en el bucket → no hay participación ahí.
-- La columna `mesas` (cantidad de mesas agregadas) permite juzgar la robustez de
-- cada fila (circuitos con pocas mesas / PASO pueden dar participación baja; ver README).
--
-- Se ejecuta con build.sh, que copia el resultado a
--   procesados/vista_participacion/vista_participacion.csv

SELECT municipio, anio, eleccion_tipo, cargo, circuito_id, mesas, padron, emitidos,
       participacion, positivos, blancos, nulos, otros,
       pct_positivo, pct_blanco, pct_nulo
FROM (
  WITH mesa AS (
    SELECT municipio, anio, eleccion_tipo, categoria AS cargo, circuito_id, mesa_id,
           MAX(mesa_electores) AS electores,
           SUM(votos_cantidad) AS emitidos,
           SUM(CASE WHEN votos_tipo = 'POSITIVO' THEN votos_cantidad ELSE 0 END) AS positivos,
           SUM(CASE WHEN votos_tipo = 'BLANCO'   THEN votos_cantidad ELSE 0 END) AS blancos,
           SUM(CASE WHEN votos_tipo = 'NULO'     THEN votos_cantidad ELSE 0 END) AS nulos
    FROM consolidado_parquet
    WHERE mesa_electores > 0        -- solo mesas con padrón (DINE 2011+)
    GROUP BY municipio, anio, eleccion_tipo, categoria, circuito_id, mesa_id
  )
  SELECT municipio, anio, eleccion_tipo, cargo, circuito_id,
         COUNT(DISTINCT mesa_id) AS mesas,
         SUM(electores) AS padron,
         SUM(emitidos)  AS emitidos,
         round(100.0 * SUM(emitidos)  / NULLIF(SUM(electores), 0), 2) AS participacion,
         SUM(positivos) AS positivos, SUM(blancos) AS blancos, SUM(nulos) AS nulos,
         SUM(emitidos) - SUM(positivos) - SUM(blancos) - SUM(nulos) AS otros,
         round(100.0 * SUM(positivos) / NULLIF(SUM(emitidos), 0), 2) AS pct_positivo,
         round(100.0 * SUM(blancos)   / NULLIF(SUM(emitidos), 0), 2) AS pct_blanco,
         round(100.0 * SUM(nulos)     / NULLIF(SUM(emitidos), 0), 2) AS pct_nulo
  FROM mesa
  GROUP BY municipio, anio, eleccion_tipo, cargo, circuito_id
)
ORDER BY municipio, anio, cargo, eleccion_tipo, circuito_id
