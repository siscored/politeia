# Proyecto: App electoral (partidos políticos) — Datos e infraestructura

## Rol
Felipe, freelance, responsable de datos e infra. La app (Amplify, demo: main.d1pthxba9jy105.amplifyapp.com) da diagnósticos y recomendaciones de campaña. Hoy tiene datos estáticos de San Isidro; hay que adaptarla a **San Fernando y Pilar**.

## Tipos de datos de la app
1. Elecciones históricas (esta fase)
2. Comentarios de militantes sobre el territorio
3. Tercera fuente a definir

## Tareas de Felipe
1. **[EN CURSO] Datos históricos para el mapa por circuito con filtro por año** (prioridad; el equipo arma los GeoJSON)
2. Esquema de datos (campos, tablas, joins) — propuesta lista, ver abajo
3. Recomendador de acciones: ¿Amazon Personalize vs. Bedrock con agentes? — pendiente

## Fuente 1: DINE (nacional) — RESUELTA
- Sistema: https://resultados.mininterior.gob.ar/ (buscador + CSV + API). Cobertura **2011–2025**, escrutinio **provisorio**. Años anteriores (1983–2013) existen en otro formato, granularidad municipio, no circuito.
- En años de elección simultánea (ej. 2023) incluye también cargos provinciales y municipales (Gobernador, Intendente, Concejales, legisladores prov.).
- Endpoint CSV: `GET https://resultados.mininterior.gob.ar/api/resultado/totalizadocsv?año={YYYY}&recuento=Provisorio&idEleccion={E}&idCargo={C}&idDistrito=2&idSeccion={S}`
- API JSON: `/api/resultados/getResultados` (OpenAPI en /desarrollo)
- IDs clave: distrito 2 = Buenos Aires; **sección 89 = Pilar (21 circuitos), 105 = San Fernando (15 circuitos)**; idEleccion 1=PASO 2=Generales 3=Segunda vuelta; idCargo 1=Presidente 2=SenNac 3=DipNac 4=Gobernador 5=SenProv 6=DipProv 7=Intendente 8/9=Mercosur 10=Concejales (4 y 7 verificados contra datos).
- Script: `descarga_dine.py` (ex descarga_masiva.py) → baja todo a `datos-electorales/raw/dine/<municipio>/` + `log_descarga.csv`. Reanudable (saltea existentes) y limpia archivos inválidos al arrancar.

### Estructura CSV (granularidad: mesa × agrupación)
`año, eleccion_tipo, recuento_tipo, padron_tipo, distrito_id/nombre, seccionprovincial_id/nombre, seccion_id/nombre, circuito_id(/nombre), mesa_id, mesa_tipo, mesa_electores, cargo_id/nombre, agrupacion_id/nombre, votos_tipo (POSITIVO/EN BLANCO/NULO/RECURRIDO...), votos_cantidad`

### Quirks para el ETL
- Orden de columnas varía entre descargas → parsear por nombre
- Votos no positivos traen `agrupacion = "undefined"`
- 2011 dice `GENERALES`, 2023 `GENERAL` → normalizar
- Espacios colgantes en `circuito_id` ("0768 ") y `agrupacion_nombre` → strip
- Combos inexistentes: API responde 200 con cuerpo "mensaje / Resultados no disponibles."
- Validación hecha: totales Pilar 2023 Presidente coinciden con la web (UxP 90.537)

## Fuente 2: Junta Electoral PBA — INTEGRADA
- "Estadísticas de votos históricos": CSV por año × distrito, **2003–2025**, elecciones provinciales/municipales, escrutinio **definitivo**. Endpoint: `distritoEstadisticasHistoricasAcsv.php` (POST/GET `anio`, `did`). Mismos ids de distrito que DINE (089 Pilar, 105 San Fernando).
- Script: `descarga_junta_pba.py` → `raw/junta_pba/<municipio>/<año>.csv` (24 archivos, hecho).
- Formato: `;` separado, largo (eleccion;distrito;lista;cargo_id;votos), votos con punto de miles, `lista_id 9996`=voto en blanco, cargo por id (04 Gobernador, 06 SenProv, 08 DipProv, 10 Intendente, 11 Concejales; nombre vacío en años viejos).
- **Limitación: solo nivel municipio.** No publica circuito ni mesa.
- Validación cruzada gobernador Pilar 2023: DINE (provisorio) 204.258 vs Junta (definitivo) 210.577 — diferencia ~3%, esperable entre provisorio y definitivo.

## Sept 2025 por circuito — INVESTIGADO A FONDO (jul 2026): no hay fuente pública
Vías agotadas: (1) sitio oficial de provisorios dado de baja (era una app `backend-difu`, el software estándar de difusión; API en `/backend-difu/scope/data/...`); (2) Wayback Machine: solo 38 URLs capturadas — el nomenclador completo (11,8 MB, jerarquía hasta circuito) pero apenas 2 respuestas de datos a nivel provincia — insuficiente; (3) portal datos abiertos PBA (`catalogo.datos.gba.gob.ar`): Error 500, roto; (4) GitHub: muchos scrapers de `backend-difu` pero todos del sistema nacional (resultados.gob.ar), ninguno archivó el bonaerense; (5) DataCP (datacp.ar): descarga solo hasta nivel sección electoral; (6) Atlas Andy Tow: acceso con login de Twitter, sin descarga masiva pública.
El dato existe (la Junta escrutó el definitivo por mesa) pero no está publicado desagregado. **Vía recomendada: pedido de acceso a la información pública a la Junta Electoral PBA** (borrador en `pedido_informacion_junta.md`). Alternativa: contactar a Andy Tow / DataCP que pueden tenerlo archivado.
Decisión interina (documentada en README_datos.md): el mapa pinta sept 2025 uniforme por municipio.

## GeoJSON circuitos (CNE) — PENDIENTE DESCARGA
`https://mapa2.electoral.gov.ar/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&authkey=3ef40a84d1159ddeef2c1776d7156560&typeName=descargas:circuito_02&maxFeatures=2000&outputFormat=application/json` — daba 503, reintentar.

## Estructura de carpetas
```
datos-electorales/
  raw/
    dine/           <- crudos DINE (pilar/, san_fernando/)
    junta_pba/      <- crudos Junta Electoral PBA (pendiente)
  consolidado.csv   <- hechos unificados (columna `fuente` distingue origen)
  vista_mapa.csv    <- agregado por circuito para el mapa
  log_descarga.csv
```
La unificación entre fuentes se hace en el ETL: cada fuente se normaliza al mismo esquema canónico (mismas columnas, mismos ids de circuito) y se apila con su `fuente`.

## GeoJSON de circuitos
La CNE publica polígonos oficiales de circuitos: electoral.gob.ar → "Información geoespacial". **Confirmar con el equipo del mapa que usen los mismos `circuito_id`.**

## Esquema propuesto
- **`resultados`** (hechos): 1 fila = votos de una agrupación en una mesa. Campos del CSV normalizados.
- **`elecciones`** (dim): año, tipo, cargo
- **`circuitos`** (dim): circuito_id, municipio, referencia al polígono GeoJSON ← **join clave con el mapa**
- **`agrupaciones`** (dim): id, nombre (+ color para pintar)
- **`vista_mapa`** (agregada): circuito × elección × agrupación → votos, %, ganador. Es lo que consume la app; el filtro por año es un WHERE.
- Decisión abierta: persistir nivel mesa (recomendado, habilita análisis finos para el recomendador) vs. solo circuito.
- Decisión abierta: dónde vive en AWS (DynamoDB / Aurora / S3+Athena, según lo que ya use el Amplify).

## ETL — HECHO (`etl_consolidar.py`)
Salidas en `datos-electorales/`:
- **`consolidado.csv`** (1.199.485 filas, 152 MB): hechos nivel mesa × agrupación, 148 archivos unificados (26 variantes de encabezado → columnas por nombre), strings limpiados, cargos/elecciones/votos_tipo normalizados (10 cargos canónicos; GENERAL/PASO/SEGUNDA_VUELTA; POSITIVO/BLANCO/NULO/RECURRIDO/IMPUGNADO/COMANDO).
- **`vista_mapa.csv`** (30.749 filas): circuito × año × elección × cargo × agrupación → votos, %, flag `gana`. Es lo que consume el mapa; filtro por año = WHERE.
- `circuito_id` canónico: quitar ceros a la izquierda y rellenar a 5 (`0768`/`00768`/`000768` → `00768`; `00768A` → `0768A`). La fuente varía el formato según el año.
- Validado: totales Pilar 2023 Presidente = web DINE; serie histórica por circuito consistente.

### Hallazgo importante para el mapa
**Los circuitos cambiaron en el tiempo**: Pilar tenía 6 circuitos hasta 2017 y pasó a 21 desde 2019 (subdivisión con sufijos de letra: 768 → 0768A/B/C...). San Fernando: 16 históricos, 15 desde 2023 (desapareció uno). Implicancia: el GeoJSON actual no matchea 1:1 los años viejos. Opciones: (a) mapear circuitos viejos a sus hijos actuales por prefijo, (b) mostrar años viejos agregados al circuito padre, (c) limitar el filtro histórico a 2019+. Decidir con el equipo del mapa.

## Arquitectura AWS acordada con el equipo
- **S3**: datos dinámicos/crudos (raw DINE + Junta, consolidado, vista_mapa). Fuente de verdad reprocesable.
- **Aurora (PostgreSQL)**: capa relacional — esquema resultados + dimensiones. Soporta pgvector para embeddings (comentarios de militantes, futuro).
- **Bedrock**: lee de Aurora (tool/agente para consultas estructuradas) + Knowledge Base sobre S3 (no estructurado). Nota: esta arquitectura favorece Bedrock Agents sobre Personalize para la tarea del recomendador.
- **DynamoDB**: datos estáticos de referencia + sugerencia propia: agregados precalculados (vista_mapa) para lecturas rápidas de la app vía AppSync/Amplify.

## QA del consolidado (hecho, jul 2026)
Sin duplicados reales (multi-filas PASO = listas internas, verificado), sin votos negativos/NaN, participación por mesa sana (mediana 79,8%, ninguna >100%, 21 mesas <30% = mesas especiales), cobertura completa vs calendario electoral, DINE vs Junta consistente en 36 combos (dif. 0,4–7%, siempre definitivo > provisorio; pico en 2019). Hueco de fuente: Junta 2009 solo Concejales.
Diccionario de datos para el equipo: `datos-electorales/README_datos.md`.

## S3 — HECHO (jul 2026)
Bucket creado: **`s3://electoral-data-851679891137/electoral/`** (us-east-1, acceso público bloqueado, SSE-S3), separado de los buckets `idetec-*` existentes (no se confirmó si idetec es el cliente).
```
electoral/
  raw/dine/ + raw/junta_pba/   (173 archivos crudos)
  procesados/                  (consolidado.csv + vista_mapa.csv)
  docs/                        (README_datos.md + resumen_exploratorio.md)
```
Nota: hubo un accidente con una carpeta `electoral ` (espacio al final) — ya migrado todo al prefijo limpio con Trasladar (179 objetos, 374 MB, 0 errores).

## Pendientes inmediatos (al retomar, empezar por acá)
1. **Validación del join** (crítico, coordinar con programadores): los `circuito_id` de sus GeoJSON deben coincidir con los de vista_mapa (canónico: 5 chars, `00768`/`0768A`). Prueba: listar los 21 códigos de Pilar 2023 en ambos lados. Si no matchea, se ajusta en el ETL (5 líneas), no en el mapa. Polígonos oficiales: mapa2.electoral.gov.ar/descargas (GeoJSON circuitos Buenos Aires — daba 503, URL exacta en sección GeoJSON).

Resueltos/descartados (jul 2026): carpeta `electoral ` borrada; README re-subido; S3 verificado OK; acceso programadores y pedido a la Junta descartados por Felipe.

## Listado de partidos para normalización — HECHO (jul 2026)
Pedido del equipo: listado de agrupaciones con elecciones en que participaron (año, cargo, nivel nacional/provincial/municipal) para que un politólogo las unifique (FpV≈FdT≈UxP).
- Salida: **`datos-electorales/partidos_elecciones.xlsx`** (script `gen_partidos.py`). Hojas: `leyenda`, `partidos` (221 filas, 1 por agrupación con nombre normalizado sin ALIANZA/acentos/abreviaturas; columnas variantes_nombre, ids, años, niveles, municipios, votos; `grupo_sugerido` = clustering textual conservador con stopwords PARTIDO/FRENTE/etc.; `grupo_canonico` amarilla vacía para el politólogo), `detalle` (2.134 filas: partido × año × elección × cargo × nivel × municipio × fuente → votos).
- Excluidos pseudo-partidos de la Junta: ids 9995–9999 ("VOTOS NULOS" venía como POSITIVO — ojo, quirk del ETL).
- Validado: totales = consolidado (24.828.945 positivos); UxP Presidente Pilar 2023 = 90.537 ✓.

## Fase siguiente
- Pipeline S3 → Aurora (esquema ya definido; Aurora PostgreSQL + pgvector para futuro).
- Tarea 2 de Felipe: recomendador — la arquitectura acordada (S3→Aurora→Bedrock) favorece **Bedrock Agents** sobre Personalize (Personalize es para recomendación tipo e-commerce, no consulta Aurora).
- Cuando el ETL sea repo con git: pasar a Claude Code usando este archivo como CLAUDE.md.

## Cómo retomar esta conversación (para un Claude nuevo)
Leer este archivo completo + `datos-electorales/README_datos.md`. El trabajo hasta acá fue: descubrir y validar fuentes, descarga masiva automatizada, ETL con normalización (26 variantes de encabezado, ids de circuito canónicos), QA completo, mitigación de limitaciones (granularidad municipio, circuito_padre), investigación exhaustiva de sept 2025 (sin fuente pública), y publicación en S3. Los scripts en la raíz de `free/` son reproducibles: `descarga_dine.py`, `descarga_junta_pba.py`, `etl_consolidar.py` (correr en ese orden para regenerar todo; sumar un municipio = agregar su id de sección en los diccionarios SECCIONES/DISTRITOS).

## Estado y próximos pasos
1. ✅ DINE: descarga completa 2011–2025 (148 archivos, mesa/circuito) — `descarga_dine.py`
2. ✅ Junta PBA: descarga 2003–2025 (24 archivos, municipio, definitivo) — `descarga_junta_pba.py`
3. ✅ ETL unificado: `consolidado.csv` (1,2M filas, columna `fuente`) + `vista_mapa.csv` (con `granularidad` y `circuito_padre` para que el mapa nunca rompa)
4. ✅ QA completo + diccionario (`README_datos.md`) + resumen con hallazgos (`resumen_exploratorio.md`)
5. ✅ Sept 2025 por circuito: investigado, sin fuente pública; pedido de información redactado (`pedido_informacion_junta.md`) — ENVIAR
6. ⏳ **Subir a S3** (Felipe, con sus credenciales; layout en README_datos.md)
7. ⏳ Entregar `vista_mapa.csv` + README al equipo del mapa; confirmar `circuito_id` canónico con sus GeoJSON; reintentar descarga GeoJSON CNE (URL en este doc, daba 503)
8. Pipeline S3 → Aurora (cuando el equipo defina bucket/instancia)
9. Tarea 2: Personalize vs. Bedrock Agents (la arquitectura acordada favorece Bedrock Agents — ver sección Arquitectura)

## Herramientas
- Cowork (este entorno): navegación Chrome, descargas, análisis exploratorio
- Claude Code: cuando el ETL sea repo con git (usar este archivo como CLAUDE.md)
