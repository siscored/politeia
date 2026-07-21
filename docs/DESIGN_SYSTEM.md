# POLITEIA · Design System

Guía visual de la consola "Comando IA". La **fuente de verdad** son los tokens en
`web/src/tokens.css` (variables CSS). Ningún componente usa hex sueltos: todo sale
de un token. Este doc explica el criterio.

## Principios
- **Consola, no documento:** se escanea y se opera. La info de resumen va antes que
  el detalle; el estado se codifica en forma + color (pills, chips), no solo en número.
- **Shell claro + sidebar oscuro + mapa oscuro** (como el mockup). El acento teal se
  usa con moderación (activos, marca); el color fuerte se gasta en el mapa.
- **El color político es semántico del dato**, separado del acento de marca.

## Color
| Token | Uso |
|---|---|
| `--brand` `#0d9488` | acento: pills activos, marca, foco |
| `--app-bg` `#eef1f5` | fondo del área de contenido |
| `--surface` `#fff` | tarjetas / panel derecho |
| `--sidebar` `#0e1a2b` | nav lateral |
| `--map-panel` / `--map-overlay` | panel del mapa y barra de filtros sobre el mapa |
| `--ink` / `--muted` / `--line` | texto principal / secundario / bordes |
| `--good` `--warn` `--crit` | estado (no es el acento) |

### Fuerzas políticas (color del dato)
| Familia | Token | Color |
|---|---|---|
| Unión por la Patria / peronismo | `--pol-peronismo` | 🔵 `#2563eb` |
| Juntos por el Cambio | `--pol-jxc` | 🟢 `#16a34a` |
| La Libertad Avanza | `--pol-lla` | 🟡 `#eab308` |
| Frente de Izquierda | `--pol-izquierda` | 🟣 `#9333ea` |
| Massismo / frentes | `--pol-massismo` | 🟠 `#ea580c` |
| Radicalismo / UCR | `--pol-ucr` | 🔷 `#0891b2` |
| Otras / blanco | `--pol-otras` | ⚪ `#94a3b8` |

> El mapeo agrupación→familia vive en `web/src/families.js` (hoy por palabra clave;
> a futuro por el `agrupacion_id` normalizado de `core/`).

## Tipografía
- **UI:** system-ui (grotesca del SO). **Datos/mono:** `--f-mono` con `tabular-nums`.
- Escala: eyebrow 10.5 · label 11 · sm 12.5 · body 13.5 · h3 16 · h2 20 · stat 26.
- Eyebrows y labels en mayúscula con `letter-spacing` (`--ls-eyebrow`/`--ls-label`).

## Espaciado y forma
- Escala 4→28 (`--sp-1..6`). Layout con flex/grid + `gap` (no márgenes sueltos).
- Radios: `--r-sm` 8 (controles) · `--r-md` 12 · `--r-lg` 14 (tarjetas) · `--r-pill`.
- Sombra: `--shadow-sm` (controles), `--shadow` (tarjetas).

## Componentes
- **Pill/segmento:** filtros (nivel, modo de color, elección, cargo). Activo = `--brand`.
- **Tarjeta:** `--surface` + `--line` + `--r-lg` + `--shadow`.
- **Chip de fuerza:** cuadradito de color (`swatch`) + label. Para leyenda y composición.
- **Barra de composición:** track `--line` + relleno con el color de la fuerza.

## Temas
Hoy la consola es de tema único (claro con sidebar/mapa oscuros), decisión deliberada
que replica el mockup. Si se agrega modo oscuro, se redefinen los tokens bajo
`:root[data-theme="dark"]` — los componentes no cambian.
