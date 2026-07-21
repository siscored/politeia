# 04 · Módulos Inteligencia y Defensa

Ambos consumen el dataset histórico del MVP (`docs/03`). Acá se define qué hace cada
sub-módulo, qué datos necesita y cómo se sabe que está bien. Se implementan **después**
de que la base de datos exista.

---

## Módulo INTELIGENCIA (analítica sobre datos duros)

### Composición del voto
- **Qué responde:** cómo se reparte el voto entre agrupaciones/familias políticas en
  una elección y unidad dada; ranking, share, y comparación contra elecciones previas.
- **Datos:** `resultado` agregado por `agrupacion_id`/`familia`, por unidad.
- **Depende de:** normalización de agrupaciones sólida (si no, la serie histórica miente).
- **Listo cuando:** reproduce el share por agrupación de una elección conocida contra
  una fuente externa (ej. Wikipedia) dentro de tolerancia.

### Estructura del voto
- **Qué responde:** cómo se distribuye geográficamente el voto (por circuito), dónde
  se gana/pierde, mapas y heterogeneidad intra-municipio.
- **Datos:** `resultado` a nivel **circuito** + `unidad_geografica` con geo.
- **Servicios:** Amazon Location Service (mapas/geocoding de circuitos).
- **Listo cuando:** puede pintar un mapa por circuito de un municipio para una
  elección con datos a nivel circuito.

### Issues por circuito
- **Qué responde:** qué temas/problemas pesan en cada circuito (seguridad, servicios,
  empleo, etc.), cruzando resultado electoral con señales temáticas.
- **Datos:** `resultado` por circuito + fuentes temáticas (relevos, escucha activa).
- **Servicios:** Bedrock (clasificación de temas).
- **Nota:** requiere una taxonomía de issues acordada. Definir antes de codear.

### Sentimiento por fuente
- **Qué responde:** tono/sentimiento de la conversación pública segmentado por fuente
  (medios, redes), y su evolución.
- **Datos:** corpus de escucha (comparte pipeline con Defensa/escucha activa).
- **Servicios:** Bedrock (análisis de sentimiento).
- **Cuidado:** sesgo de fuente; declarar cobertura y limitaciones del corpus.

### Recomendador IA
- **Qué responde:** recomendaciones accionables (dónde reforzar, qué mensaje, qué
  circuito priorizar) a partir de composición + estructura + issues + sentimiento.
- **Datos:** salidas de los sub-módulos anteriores.
- **Servicios:** Bedrock.
- **Regla:** toda recomendación debe poder **explicarse con los datos que la sostienen**
  (trazabilidad también acá; nada de "caja negra" sin evidencia).

---

## Módulo DEFENSA (tiempo real y simulación)

### Escucha activa
- **Qué responde:** qué se está diciendo ahora en la conversación pública relevante
  (menciones, temas emergentes, picos).
- **Datos:** ingesta streaming de fuentes públicas → `S3 raw` → procesamiento.
- **Servicios:** EventBridge (disparadores), Lambda, Bedrock (clasificación/sentimiento).
- **Alcance ético/legal:** solo fuentes públicas y agregadas; sin PII; respetar
  términos de cada plataforma. Registrar qué se recolecta y de dónde.

### Impacto en la estructura de voto
- **Qué responde:** simulación *what-if* — cómo un evento/escenario podría mover la
  estructura de voto, apoyándose en la base histórica (elasticidades, antecedentes).
- **Datos:** dataset histórico (`curated`) como base; escenarios como input.
- **Servicios:** Lambda / Step Functions.
- **Regla:** es un **modelo con supuestos explícitos**, no una predicción con aire de
  certeza. Documentar supuestos y márgenes.

---

## Secuencia de construcción

```
MVP datos (docs/03)
   └─► Composición del voto  ──┐
   └─► Estructura del voto  ───┤─► Recomendador IA
        (Issues por circuito) ─┘
   └─► Escucha activa ─► Sentimiento por fuente ─► (alimenta Issues y Recomendador)
   └─► Impacto en estructura de voto (usa la base histórica)
```

Nada de esto arranca hasta que el dataset histórico cierre validaciones.
