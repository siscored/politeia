// Utilidades geográficas compartidas por los dos mapas (Google / MapLibre).

export function eachCoord(geom, fn) {
  const rings = geom.type === "Polygon" ? geom.coordinates
    : geom.type === "MultiPolygon" ? geom.coordinates.flat() : [];
  rings.forEach((r) => r.forEach(fn));
}

export function centroid(feature) {
  let sx = 0, sy = 0, n = 0;
  eachCoord(feature.geometry, (c) => { sx += c[0]; sy += c[1]; n++; });
  return [sx / n, sy / n];
}

// Subconjunto "poblado" para el encuadre del mapa: excluye circuitos que son a
// la vez casi vacíos (pocos votos) Y lejanos del centro del voto — típicamente
// las islas del delta (San Fernando). NO los borra: solo no dominan la vista.
// Cada feature debe traer properties.weight = votos válidos del circuito.
export function coreFeatures(features) {
  const items = features.map((f) => ({ f, v: f.properties.weight || 0, c: centroid(f) }));
  const total = items.reduce((a, x) => a + x.v, 0);
  if (total <= 0 || items.length < 5) return features;
  const maxV = Math.max(...items.map((x) => x.v));
  // centro del voto (promedio de centroides pesado por votos)
  const cx = items.reduce((a, x) => a + x.c[0] * x.v, 0) / total;
  const cy = items.reduce((a, x) => a + x.c[1] * x.v, 0) / total;
  const dist = (x) => Math.hypot(x.c[0] - cx, x.c[1] - cy);
  const med = [...items.map(dist)].sort((a, b) => a - b)[Math.floor(items.length / 2)] || 1;
  // excluir del encuadre los outliers geográficos (lejos del centro del voto) que
  // además no son circuitos mayores — típicamente las islas del delta. Se siguen
  // renderizando; solo no dominan la vista por defecto.
  const core = items.filter((x) => !(dist(x) > med * 4 && x.v < maxV * 0.5)).map((x) => x.f);
  return core.length ? core : features;
}
