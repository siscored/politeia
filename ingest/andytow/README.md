# ingest/andytow  —  PENDIENTE (cierra el hueco 1983-2002)

Extractor del **Atlas Electoral de Andy Tow** (`andytow.com`). Es la fuente para el
tramo que falta: presidencial/gobernador/legislativo provincial y **cargos
municipales 1983-2011** por seccion/circuito.

- Salida cruda objetivo: `raw/andytow/<municipio>/...`
- Normalizar con el mismo `core/` (mismo esquema que DINE/Junta).
- Cuidado: web con tablas/visualizaciones → scraping cuidadoso; cruzar totales con
  Wikipedia; verificar continuidad territorial (municipios creados en los '90).

Estado: NO implementado. Es la prioridad para cerrar el contrato original (docs/03).
