# Log de decisiones (ADR livianas)

Registrar acá toda decisión de diseño/criterio que no esté ya en los docs. Formato:

## AAAA-MM-DD · Título corto de la decisión
- **Contexto:** qué problema apareció.
- **Decisión:** qué se resolvió.
- **Alternativas descartadas:** por qué no.
- **Impacto:** qué docs/módulos toca.

---

## 2026-XX-XX · (ejemplo) Criterio de normalización de frentes municipales
- **Contexto:** los frentes locales de San Fernando cambian de sigla casi cada elección.
- **Decisión:** se mapean a `agrupacion_id` por familia política + año en el diccionario.
- **Alternativas descartadas:** un id por sigla (rompe la serie histórica).
- **Impacto:** `core/agrupaciones/`, `docs/02`.
