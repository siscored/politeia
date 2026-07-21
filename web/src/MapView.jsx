import React, { useMemo } from "react";
import { famOf } from "./families.js";

function ringsOf(g) {
  if (g.type === "Polygon") return g.coordinates;
  if (g.type === "MultiPolygon") return g.coordinates.flat();
  return [];
}

function makeProjector(features) {
  let lat0 = 0, n = 0;
  features.forEach((f) => ringsOf(f.geometry).forEach((r) => r.forEach((p) => { lat0 += p[1]; n++; })));
  lat0 /= n || 1;
  const k = Math.cos((lat0 * Math.PI) / 180);
  let minx = 1e9, miny = 1e9, maxx = -1e9, maxy = -1e9;
  features.forEach((f) => ringsOf(f.geometry).forEach((r) => r.forEach((p) => {
    const x = p[0] * k, y = p[1];
    if (x < minx) minx = x; if (x > maxx) maxx = x;
    if (y < miny) miny = y; if (y > maxy) maxy = y;
  })));
  const W = 100, H = 100, pad = 6;
  const s = Math.min((W - 2 * pad) / (maxx - minx), (H - 2 * pad) / (maxy - miny));
  const ox = (W - s * (maxx - minx)) / 2, oy = (H - s * (maxy - miny)) / 2;
  return (p) => [ox + (p[0] * k - minx) * s, H - (oy + (p[1] - miny) * s)];
}

function pathD(feature, proj) {
  let d = "";
  ringsOf(feature.geometry).forEach((r) => {
    r.forEach((p, i) => { const q = proj(p); d += (i ? "L" : "M") + q[0].toFixed(2) + " " + q[1].toFixed(2); });
    d += "Z";
  });
  return d;
}

export default function MapView({ features, lookup, selected, onHover }) {
  const paths = useMemo(() => {
    if (!features.length) return [];
    const proj = makeProjector(features);
    return features.map((f) => ({
      cid: f.properties.circuito_id,
      cabecera: f.properties.cabecera,
      d: pathD(f, proj),
    }));
  }, [features]);

  return (
    <svg className="map" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet"
      role="img" aria-label="Mapa electoral por circuito">
      {paths.map((p) => {
        const rec = lookup(p.cid);
        const color = rec ? famOf(rec.g).c : "#3a4a63";
        const cls = "circ" + (selected && selected !== p.cid ? " dim" : "");
        return (
          <path key={p.cid} className={cls} d={p.d} fill={color} fillOpacity="0.92"
            onMouseEnter={() => onHover(p.cid)}
            onClick={() => onHover(p.cid)} />
        );
      })}
    </svg>
  );
}
