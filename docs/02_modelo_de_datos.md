# 02 · Modelo de datos (esquema REAL + contrato ideal)

Este doc documenta **el esquema que ya existe en el bucket** como contrato efectivo, y
al lado el ideal del proyecto, con la deuda para cerrar la brecha. No inventar un
esquema que contradiga lo que hay cargado.

## Jerarquía geográfica

```
País → Distrito (PBA) → Sección electoral → Municipio (Pilar, San Fernando)
      → Circuito → Mesa
```
- **Circuito** es la unidad analítica clave (features de Inteligencia). `circuito_id`
  es además la **clave de join con el GeoJSON de circuitos de la CNE** para el mapa.
- **Mesa** existe en los crudos DINE; puede no existir en años/fuentes viejas.

## Esquema real: `procesados/consolidado.csv` (tabla de hechos, nivel mesa)

19 columnas. Formato **largo** para votos (una fila por tipo de voto).

```
fuente              str   ("dine" | "junta")            ← linaje mínimo
municipio           str   ("Pilar" | "San Fernando")
año                 int
eleccion_tipo       str   ("paso" | "generales" | "segunda_vuelta" | ...)
cargo_id            str
cargo_nombre        str   (presidente, gobernador, intendente, dip/sen nac/prov, concejal, mercosur, ...)
distrito_id         str
seccion_id          str
seccion_nombre      str
circuito_id         str   ← join con GeoJSON CNE
mesa_id             str
mesa_tipo           str
mesa_electores      int
agrupacion_id       str   (normalizada)
agrupacion_nombre   str   (nombre tal como aparece)
lista_numero        str
lista_nombre        str
votos_tipo          str   ("positivo" | "nulo" | "blanco" | "impugnado" | ...)
votos_cantidad      int
```
Destino declarado: Aurora / Bedrock. Tamaño: ~150 MB (1 solo CSV → ver deuda #3).

## Esquema real: `procesados/vista_mapa.csv` (agregado de consumo, mapa)

11 columnas. Precalculado para el frontend "Comando IA". Resuelve fallback a
municipio y herencia `circuito_padre` pre-2019.

```
municipio           str
año                 int
eleccion_tipo       str
cargo_nombre        str
circuito_id         str
agrupacion_nombre   str
votos               int
porcentaje          float
gana                bool   (ganador en esa unidad)
granularidad        str    ("circuito" | "municipio")   ← declara el fallback
circuito_padre      str    (herencia para comparar pre/post cambio 2019)
```

## Categorías de cargo presentes en el dataset

Ejecutivo: **presidente, gobernador, intendente**.
Legislativo: **diputado/senador nacional, diputado/senador provincial, concejal**,
más **Mercosur (nacional/regional)** y **segunda vuelta presidencial** (2015, 2023).
La Junta cubre 2003-2025 a nivel municipio (hueco 2009 = solo concejales).

Mapeo del pedido del MVP: **ejecutivo** = presidente + gobernador + intendente;
**legislativo** = el resto.

## Contrato ideal del proyecto (objetivo) y DEUDA

El contrato canónico de POLITEIA pide, además de lo anterior:

| Campo ideal | ¿Está en el real? | Acción |
|---|---|---|
| `fecha` (YYYY-MM-DD) | solo `año` | derivar/agregar fecha exacta por elección |
| `vuelta` | vía `eleccion_tipo` | OK (alias) |
| `ambito` (nac/prov/mun) | implícito en cargo/fuente | agregar columna explícita |
| `agrupacion_raw` (texto original preservado) | **no garantizado** | **verificar**: si `agrupacion_nombre` ya es el crudo, documentarlo; si se normalizó pisando el original, recuperarlo de `raw/` |
| `fuente_url`, `fecha_extraccion`, `hash_registro` | solo `fuente` | agregar linaje fino en el próximo ETL |
| `electores`/`padron` por unidad (para calcular **participación %**) | **no está** | **deuda #6**: `vista_mapa` trae `votos`, no el padrón. El mockup mostraba `padron` por circuito (dato de panel). Sumar la columna de electores desde DINE (nº de inscriptos por mesa→circuito) en el próximo ETL. Habilita participación y voto en blanco/nulo como % del padrón. |
| Parquet particionado `distrito/anio/categoria` | es CSV | migrar (deuda #3) |

> **Regla que se mantiene:** `agrupacion_raw` no se pisa. Si el ETL actual ya
> normalizó sin conservar el original, es deuda a saldar leyendo de `raw/`.

## Normalización de agrupaciones (problema central)

40 años de mutaciones y recombinaciones. La resolución `raw → agrupacion_id` vive en
`core/agrupaciones/diccionario.csv` (versionado), y **puede depender de año y
distrito** (misma sigla, distinta cosa). Ejemplos reales del dataset:
peronismo (PJ / FpV / FdT / Fuerza Patria), Cambiemos/JxC, LLA como nuevo eje 2021+.
Toda fusión/herencia se comenta en el diccionario y, si es criterio, en `DECISIONES.md`.

**Estado (2026-07-23):** 13 familias validadas con el usuario. La columna **`familia`
ya está materializada en `vista_mapa.csv`** vía `ingest/normaliza/` (resolver canónico
`core/agrupaciones/familias.py`). **La API la reenvía en cada item y el front dejó de
recalcularla** (`web/src/families.js` ya NO tiene los regex de clasificación: se quedó
solo con la tabla presentación `familia → {label, color}`). Con esto el criterio de
clasificación tiene **una única fuente de verdad** (backend); el front solo pinta.
Pendiente: completar `agrupacion_id` fino en el diccionario (hoy 63 de 236 crudas
mapeadas explícitamente; el resto resuelve a familia por keyword).

## Particionado y consumo

- **Hoy:** `consolidado.csv` (hechos) + `vista_mapa.csv` (mapa), en `procesados/`.
- **Objetivo:** Parquet particionado para Athena/Aurora; CSV como espejo humano.
- **DynamoDB (si se usa para el API):** `PK = MUNI#<municipio>`,
  `SK = ELEC#<año>#<cargo>#<eleccion_tipo>#CIRC#<circuito_id>#AGR#<agrupacion_id>`.
