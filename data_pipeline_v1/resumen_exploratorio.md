# Resumen exploratorio — Datos electorales Pilar y San Fernando

*Generado sobre `consolidado.csv` (1.200.301 filas) y `vista_mapa.csv` (31.279 filas). Fuente principal: DINE (escrutinio provisorio, nivel mesa); complemento: Junta Electoral PBA (definitivo, nivel municipio).*

## Volumen y cobertura

- **Pilar**: 21 circuitos actuales (6 hasta 2017), ~915 mesas, ~321 mil electores habilitados (2025)
- **San Fernando**: 15 circuitos actuales (16 hasta 2021), ~397 mesas nacionales, ~180 mil electores
- Cobertura por circuito: 2011–2025 (todas las elecciones nacionales y simultáneas). Por municipio: 2003–2025 (agrega provinciales viejas y sept 2025)

## Quién ganó cada elección (cargo testigo del año, elecciones generales)

| Año | Cargo | Pilar 1° | % | San Fernando 1° | % |
|---|---|---|---|---|---|
| 2011 | Presidente | FpV | 60,4 | FpV | 53,9 |
| 2013 | Dip. Nac. | Frente Renovador | 53,5 | Frente Renovador | 62,2 |
| 2015 | Presidente | FpV | 38,8 | UNA (Massa) | 34,7 |
| 2017 | Dip. Nac. | Cambiemos | 43,8 | Cambiemos | 39,4 |
| 2019 | Presidente | Frente de Todos | 53,3 | Frente de Todos | 49,7 |
| 2021 | Dip. Nac. | Frente de Todos | 43,1 | Frente de Todos | 39,9 |
| 2023 | Presidente | Unión por la Patria | 43,3 | Unión por la Patria | 43,7 |
| 2025 | Dip. Nac. | Fuerza Patria | 44,2 | Fuerza Patria | 42,8 |
| 2025 sept | Sen. Prov. | Fuerza Patria | 60,0* | Fuerza Patria | * |

\* nivel municipio (Junta, definitivo). Nota: en San Fernando el massismo local es dominante en municipales.

## Participación (votos emitidos / electores habilitados)

| | 2011 | 2013 | 2015 | 2017 | 2019 | 2021 | 2023 | 2025 |
|---|---|---|---|---|---|---|---|---|
| Pilar | 84,1 | 85,0 | 80,3 | 73,7 | 84,4 | 73,9 | 78,5 | **68,6** |
| San Fernando | 81,7 | 81,2 | 78,5 | 74,9 | 81,9 | 73,5 | 78,0 | **68,8** |

Tendencia clara: la participación viene cayendo; 2025 marcó el piso de la serie (~10 pts menos que elecciones comparables). Dato relevante para estrategia de movilización.

## El valor del nivel circuito (por qué el municipio engaña)

- **2025 Diputados Nac. en Pilar**: Fuerza Patria ganó el municipio (44,2% vs 42,3%)… pero **LLA ganó 13 de los 21 circuitos**. El voto peronista está concentrado en pocos circuitos muy densos; el opositor, distribuido. El mapa por circuito muestra exactamente dónde se pierde y se gana.
- **San Fernando 2025**: empate casi perfecto (42,8 vs 42,0) — LLA 8 circuitos, FP 7.
- **Heterogeneidad interna 2023 (Presidente, % UxP)**: en Pilar va del 12,8% (circuito 0770A) al 57,2% (0770F) — **44 puntos de brecha dentro del mismo municipio**. San Fernando: 23,8% a 59,8% (36 pts).
- **El voto local difiere del nacional**: en 2023 el intendente de Pilar (UxP) ganó 20 de 21 circuitos, mientras Presidente UxP ganó 17. El corte de boleta es medible por circuito.

## Contraste provisorio vs definitivo

DINE (provisorio) subestima 0,4–7% respecto de la Junta (definitivo), siempre en la misma dirección, con pico en 2019. Para tendencias y mapas no cambia conclusiones; para totales exactos usar `fuente=junta_pba`.

## Datos pendientes documentados

Sept 2025 por circuito (pedido de información en curso — mientras tanto, fallback municipio), senadores prov. 2009, y re-tabulación de años pre-2019 con circuitos actuales (no existe oficialmente; mitigado con `circuito_padre`).
