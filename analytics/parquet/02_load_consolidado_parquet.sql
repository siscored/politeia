-- HUECO #3 · Carga de `consolidado_parquet` desde la tabla CSV `consolidado`.
--
-- INSERT INTO ... SELECT en 4 TANDAS. Athena limita 100 particiones por query;
-- el espacio es 2 municipios × 12 años × 10 cargos = 240 (96 reales). Se batchea
-- por municipio × mitad de años para que cada tanda quede < 100.
--
-- Columnas de partición al final del SELECT y en el orden de PARTITIONED BY:
-- municipio, anio (= "año" casteado a int), categoria (= cargo_nombre).
-- Idempotente sobre tabla recién creada (01_create hace DROP+CREATE antes).

INSERT INTO consolidado_parquet
SELECT fuente, eleccion_tipo, cargo_id, distrito_id, seccion_id, seccion_nombre,
       circuito_id, mesa_id, mesa_tipo, mesa_electores, agrupacion_id,
       agrupacion_nombre, lista_numero, lista_nombre, votos_tipo, votos_cantidad,
       municipio, CAST("año" AS int) AS anio, cargo_nombre AS categoria
FROM consolidado
WHERE municipio = 'pilar' AND "año" <= 2013;

INSERT INTO consolidado_parquet
SELECT fuente, eleccion_tipo, cargo_id, distrito_id, seccion_id, seccion_nombre,
       circuito_id, mesa_id, mesa_tipo, mesa_electores, agrupacion_id,
       agrupacion_nombre, lista_numero, lista_nombre, votos_tipo, votos_cantidad,
       municipio, CAST("año" AS int) AS anio, cargo_nombre AS categoria
FROM consolidado
WHERE municipio = 'pilar' AND "año" >= 2015;

INSERT INTO consolidado_parquet
SELECT fuente, eleccion_tipo, cargo_id, distrito_id, seccion_id, seccion_nombre,
       circuito_id, mesa_id, mesa_tipo, mesa_electores, agrupacion_id,
       agrupacion_nombre, lista_numero, lista_nombre, votos_tipo, votos_cantidad,
       municipio, CAST("año" AS int) AS anio, cargo_nombre AS categoria
FROM consolidado
WHERE municipio = 'san_fernando' AND "año" <= 2013;

INSERT INTO consolidado_parquet
SELECT fuente, eleccion_tipo, cargo_id, distrito_id, seccion_id, seccion_nombre,
       circuito_id, mesa_id, mesa_tipo, mesa_electores, agrupacion_id,
       agrupacion_nombre, lista_numero, lista_nombre, votos_tipo, votos_cantidad,
       municipio, CAST("año" AS int) AS anio, cargo_nombre AS categoria
FROM consolidado
WHERE municipio = 'san_fernando' AND "año" >= 2015;
