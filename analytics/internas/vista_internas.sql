-- Internas de las PASO · dimensión latente del bucket (lista_numero/lista_nombre).
--
-- El mapa suma las listas internas de cada partido y las esconde. Este dataset las
-- expone: una fila por (municipio, anio, cargo, agrupacion, lista) con votos, % de
-- la lista dentro del partido, si ganó la interna, y cuántas listas compitieron.
--
-- Solo PASO y voto POSITIVO con lista nombrada. Cobertura ~2011-2025 (las PASO
-- traen lista_nombre; GENERAL casi no). Se ejecuta con build.sh, que copia el
-- resultado a procesados/vista_internas/vista_internas.csv.

SELECT municipio, anio, cargo, agrupacion_nombre, lista_numero, lista_nombre,
       votos, votos_partido, pct_en_partido, gana_interna, listas_en_partido
FROM (
  WITH base AS (
    SELECT municipio, anio, categoria AS cargo, agrupacion_nombre,
           lista_numero, lista_nombre, SUM(votos_cantidad) AS votos
    FROM consolidado_parquet
    WHERE eleccion_tipo = 'PASO' AND votos_tipo = 'POSITIVO' AND lista_nombre <> ''
    GROUP BY municipio, anio, categoria, agrupacion_nombre, lista_numero, lista_nombre
  )
  SELECT municipio, anio, cargo, agrupacion_nombre, lista_numero, lista_nombre, votos,
         SUM(votos) OVER (PARTITION BY municipio, anio, cargo, agrupacion_nombre) AS votos_partido,
         round(100.0 * votos / NULLIF(SUM(votos) OVER (PARTITION BY municipio, anio, cargo, agrupacion_nombre), 0), 2) AS pct_en_partido,
         (ROW_NUMBER() OVER (PARTITION BY municipio, anio, cargo, agrupacion_nombre ORDER BY votos DESC) = 1) AS gana_interna,
         COUNT(*) OVER (PARTITION BY municipio, anio, cargo, agrupacion_nombre) AS listas_en_partido
  FROM base
)
ORDER BY municipio, anio, cargo, agrupacion_nombre, votos DESC
