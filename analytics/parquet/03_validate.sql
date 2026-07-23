-- HUECO #3 · Validación: los totales deben CERRAR entre CSV y Parquet (contrato §6/§7).
-- Se corre después de 02_load. Resultado esperado documentado al lado de cada query.

-- 1) Global: filas y suma de votos. Debe coincidir con `consolidado`.
--    Esperado (2026-07-23): 1200301 filas, 27095945 votos, 96 particiones.
SELECT COUNT(*) AS n_filas,
       SUM(votos_cantidad) AS suma_votos,
       COUNT(DISTINCT municipio || CAST(anio AS varchar) || categoria) AS particiones
FROM consolidado_parquet;

-- 2) Reconciliación por partición: cuenta las (municipio,año,cargo) donde CSV y
--    Parquet difieren en n filas o suma de votos. Esperado: 0.
SELECT COUNT(*) AS particiones_con_diferencia
FROM (SELECT municipio AS m, "año" AS a, cargo_nombre AS c,
             COUNT(*) AS n, SUM(votos_cantidad) AS v
      FROM consolidado GROUP BY 1, 2, 3) csv
FULL OUTER JOIN
     (SELECT municipio AS m, anio AS a, categoria AS c,
             COUNT(*) AS n, SUM(votos_cantidad) AS v
      FROM consolidado_parquet GROUP BY 1, 2, 3) pq
  ON csv.m = pq.m AND csv.a = pq.a AND csv.c = pq.c
WHERE csv.n IS DISTINCT FROM pq.n OR csv.v IS DISTINCT FROM pq.v;

-- 3) Prueba del beneficio: bytes escaneados por una consulta típica del mapa.
--    Ver Statistics.DataScannedInBytes de cada ejecución (no en el ResultSet).
--    Esperado (2026-07-23): CSV ~157 MB vs Parquet ~41 KB (~3800x menos).
SELECT agrupacion_nombre, SUM(votos_cantidad) AS votos
FROM consolidado_parquet
WHERE municipio = 'pilar' AND anio = 2023 AND categoria = 'PRESIDENTE'
GROUP BY agrupacion_nombre
ORDER BY votos DESC;
