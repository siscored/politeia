-- HUECO #3 · Tabla Parquet particionada de `consolidado`.
--
-- Crea `consolidado_parquet` (Athena/Glue) sobre Parquet SNAPPY particionado por
-- municipio / anio / categoria(=cargo_nombre), con PARTITION PROJECTION: la tabla
-- deriva sus particiones de la query, sin correr crawler ni MSCK REPAIR.
--
-- Decisiones (docs/DECISIONES.md 2026-07-23): "distrito"=municipio, "categoria"=
-- cargo_nombre. Los datos se cargan con 02_load; se valida con 03_validate.
--
-- Idempotente: DROP + CREATE. NO borra los datos en S3 (solo el metadato Glue);
-- los Parquet viven en procesados/parquet/consolidado/ independientes de la tabla.

DROP TABLE IF EXISTS consolidado_parquet;

CREATE EXTERNAL TABLE consolidado_parquet (
  fuente string,
  eleccion_tipo string,
  cargo_id bigint,
  distrito_id bigint,
  seccion_id bigint,
  seccion_nombre string,
  circuito_id string,
  mesa_id bigint,
  mesa_tipo string,
  mesa_electores bigint,
  agrupacion_id bigint,
  agrupacion_nombre string,
  lista_numero string,
  lista_nombre string,
  votos_tipo string,
  votos_cantidad bigint
)
PARTITIONED BY (municipio string, anio int, categoria string)
STORED AS PARQUET
LOCATION 's3://electoral-data-851679891137/electoral/procesados/parquet/consolidado/'
TBLPROPERTIES (
  'parquet.compression'='SNAPPY',
  'projection.enabled'='true',
  'projection.municipio.type'='enum',
  'projection.municipio.values'='pilar,san_fernando',
  'projection.anio.type'='integer',
  'projection.anio.range'='2003,2025',
  'projection.categoria.type'='enum',
  'projection.categoria.values'='CONCEJALES,DIPUTADOS_NAC,DIPUTADOS_PROV,GOBERNADOR,INTENDENTE,MERCOSUR_NAC,MERCOSUR_REG,PRESIDENTE,SENADORES_NAC,SENADORES_PROV',
  'storage.location.template'='s3://electoral-data-851679891137/electoral/procesados/parquet/consolidado/${municipio}/${anio}/${categoria}/'
);
