# 05 · Fuentes de datos (catálogo)

Toda fuente usada se registra acá con: `fuente_id`, URL, cobertura, formato y cómo se
baja. Este catálogo es parte del contrato: un dato sin fuente en este archivo no entra.

> Verificar disponibilidad al momento de usar: algunos sitios estatales cambian de
> URL o quedan intermitentes. Siempre guardar el crudo en `raw/<fuente_id>/`.

## Estado de uso (según bucket real)

| Fuente | Estado | Cubre en el dataset actual |
|---|---|---|
| `dine` | **USADA** | nacional/provincial 2011-2025, por mesa |
| `junta_pba` | **USADA** | municipal/provincial 2003-2025, por municipio |
| `andytow` | **PENDIENTE** | 1983-2002/2011 (el hueco #1) — no integrada aún |
| `datacp` | opcional | validación legislativo nacional |
| `wikipedia` | opcional | cross-check de totales |

**Prioridad para cerrar el contrato: integrar `andytow` (1983-2002).**

---

## `dine` — Dirección Nacional Electoral (oficial)
- **URLs:**
  - Micrositio resultados históricos: `https://resultados.mininterior.gob.ar/`
  - API pública: `https://datos.gob.ar/dataset/dine-api-publicacion-resultados-electorales`
  - Datasets por año (nivel mesa): `https://datos.gob.ar/dataset?tags=elecciones`
- **Cobertura:** elecciones **nacionales 2011–2023/2025**; incluye **provinciales/
  locales bajo ley de simultaneidad**. Granularidad hasta **mesa**. Escrutinio
  provisorio.
- **Formato:** CSV descargable + **API REST** (hay sección para desarrolladores).
- **Cómo bajar:** API para consulta filtrada (año, tipo, categoría, distrito,
  sección) o CSV completo por año. Filtrar por distrito Buenos Aires y por los
  circuitos/mesas de Pilar y San Fernando.
- **Límite:** **no cubre 1983–2009**; municipal puro (intendente/concejal) solo si
  fue simultáneo. Usar Andy Tow para lo que falte.

## `andytow` — Atlas Electoral de Andy Tow
- **URL:** `https://www.andytow.com/atlas/totalpais/`
  (PBA: `.../buenosaires/index.html`)
- **Cobertura:** **desde 1983** — presidente, Congreso, gobernadores, legislaturas
  provinciales y **cargos municipales** por provincia/sección/circuito (histórico
  ~1983–2011/2013). **Es la fuente clave del período viejo y de lo municipal.**
- **Formato:** web (tablas/visualizaciones); requiere scraping/parseo cuidadoso.
- **Cómo bajar:** navegar por distrito → sección → municipio → cargo → año. Guardar
  HTML/tablas crudas. Cruzar con Wikipedia para validar totales.
- **Crédito:** citar la fuente (Andy Tow) en `fuente_url` por fila.

## `junta_pba` — Junta Electoral de la Provincia de Buenos Aires
- **Uso:** resultados **provinciales y municipales oficiales**, especialmente
  recientes (intendente, concejales, consejeros escolares).
- **Formato:** suele ser PDF/planillas; puede requerir OCR/parseo de PDF.
- **Cómo bajar:** buscar el portal vigente de la Junta Electoral PBA para el año;
  guardar los PDF originales en `raw`. Verificar sección electoral por año acá.

## `datacp` — Data CP (datos electorales abiertos)
- **URL:** `https://www.datacp.ar/`
- **Cobertura:** resultados presidenciales y **legislativos nacionales**,
  composición del Congreso, series históricas; descargas por provincia y sección.
- **Formato:** **CSV / Excel** + **GeoJSON** (útil para mapas de circuito/sección).
- **Uso:** fuente secundaria y de **validación** del legislativo nacional; los
  GeoJSON ayudan a la feature "estructura del voto".

## `wikipedia` — Wikipedia (validación)
- **URLs:** artículos por elección, ej.
  `https://es.wikipedia.org/wiki/Elecciones_provinciales_de_Buenos_Aires_de_1983`
- **Uso:** **solo cross-check de totales y contexto** (fórmulas, alianzas, %
  provinciales). **Nunca** como única fuente de un dato fino por circuito.
- **Cuidado:** citar; no copiar texto; usar para desempatar y contextualizar.

## `agn` — Archivo General de la Nación / DINE histórico (respaldo profundo)
- **URL:** `https://atom.mininterior.gob.ar/` (fondo Dirección Nacional Electoral)
- **Uso:** respaldo documental para huecos muy viejos; documentación en papel
  digitalizada. Último recurso, alta fricción.

---

## Matriz período × fuente (guía rápida)

| Necesito… | Fuente primaria | Validar con |
|---|---|---|
| Nacional/provincial 2011→hoy, hasta mesa | `dine` | `datacp`, `wikipedia` |
| Presidente/gobernador 1983–2009 | `andytow` | `wikipedia` |
| Intendente/concejales 1983–2011 | `andytow` | `junta_pba`, `wikipedia` |
| Intendente/concejales recientes | `junta_pba` | `dine` (si simultáneo), `andytow` |
| Legislativo nacional (serie/geo) | `datacp` | `dine` |

## Recordatorio de linaje

Cada fila cargada lleva `fuente_id` + `fuente_url` + `fecha_extraccion`. Si un dato
salió de cruzar dos fuentes, se anota el criterio de desempate en el commit y, si es
recurrente, en `docs/DECISIONES.md`.
