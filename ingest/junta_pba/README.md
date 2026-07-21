# ingest/junta_pba

Ingesta de la **Junta Electoral de la Provincia de Buenos Aires** (definitivo, por
municipio, 2003-2025). Cubre lo que DINE no tiene por circuito y sept-2025.

> No existe script previo (HUECO #5). **Pendiente de reconstruir.**

## Estado
- **Pendiente:** replicar el patrón de `ingest/dine` como Lambda `politeia-ingest-junta`
  (bajar el crudo a `raw/junta_pba/<municipio>/<año>.csv` con linaje).
- **Ojo:** la Junta suele publicar en PDF/planillas → probablemente requiera parseo/OCR,
  no solo un GET. Hueco conocido: 2009 = solo concejales.

Fuente: ver `docs/05_fuentes_de_datos.md#junta_pba`.
