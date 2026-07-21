# ingest/dine

Ingesta de la **Dirección Nacional Electoral** (provisorio, por mesa, 2011-2025).

> No existe script previo (HUECO #5). Se reconstruye acá desde cero.

## Estado
- **Implementado:** Lambda `politeia-ingest-dine` (`handler.py`), desplegada por
  `infra/stacks/ingest_stack.py`. Baja una URL y la guarda cruda en
  `raw/dine/<municipio>/<archivo>` con linaje (`fuente_url`, `fecha_extraccion`, `sha256`).
- **Falta:** el **catálogo de URLs** de DINE (qué año/cargo/municipio → qué URL). Sin
  eso, la Lambda es un trabajador genérico que hay que invocar con la URL a mano.
- **Trigger:** regla EventBridge `politeia-ingest-dine-schedule` creada pero
  **deshabilitada** hasta tener el catálogo.

## Invocación (mientras no haya catálogo)
```json
{ "fuente_url": "https://.../resultado.csv",
  "municipio": "pilar",
  "nombre_archivo": "2025_generales_dip_nac.csv" }
```

Fuente/API: ver `docs/05_fuentes_de_datos.md#dine`. DINE es provisorio (queda 0,4-7%
bajo el definitivo de la Junta).
