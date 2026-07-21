import { useEffect, useRef } from "react";
import maplibregl from "maplibre-gl";

// Basemap oscuro sin API key (equivalente al Google Maps del mockup).
// Estilo raster inline (tiles oscuros de CARTO): carga siempre, sin depender
// de glyphs/sprite vectoriales. A futuro se cambia por el SDK de Google Maps.
const STYLE = {
  version: 8,
  sources: {
    carto: {
      type: "raster",
      tiles: [
        "https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png",
        "https://b.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png",
        "https://c.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png",
      ],
      tileSize: 256,
      attribution: '© <a href="https://carto.com/">CARTO</a> © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    },
  },
  // raster-fade-duration 0: los tiles aparecen al instante al cargar, sin el
  // fade-in que requiere frames continuos (que no ocurren si el mapa está idle).
  layers: [{ id: "carto-base", type: "raster", source: "carto", paint: { "raster-fade-duration": 0 } }],
};

function eachCoord(geom, fn) {
  const rings = geom.type === "Polygon" ? geom.coordinates
    : geom.type === "MultiPolygon" ? geom.coordinates.flat() : [];
  rings.forEach((r) => r.forEach(fn));
}
function centroid(feature) {
  let sx = 0, sy = 0, n = 0;
  eachCoord(feature.geometry, (c) => { sx += c[0]; sy += c[1]; n++; });
  return [sx / n, sy / n];
}

export default function MapView({ coloredGeo, distrito, selected, onSelect }) {
  const boxRef = useRef(null);
  const mapRef = useRef(null);
  const readyRef = useRef(false);
  const markersRef = useRef([]);
  const distritoRef = useRef(null);
  const selRef = useRef(null);
  const dataRef = useRef(coloredGeo);
  dataRef.current = coloredGeo;

  useEffect(() => {
    const map = new maplibregl.Map({
      container: boxRef.current, style: STYLE,
      center: [-58.9, -34.45], zoom: 10.5, attributionControl: false,
    });
    mapRef.current = map;
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "bottom-right");
    map.addControl(new maplibregl.AttributionControl({ compact: true }), "bottom-right");
    map.on("error", (e) => console.error("MAPLIBRE", e && e.error && e.error.message));

    // Resize+repaint escalonados: el mapa a veces no tiene tamaño estable al
    // crear (queda negro) y hay que patear el render tras cargar los tiles.
    const resizeTimers = [0, 250, 700, 1500, 2600].map((t) => setTimeout(() => { try { map.resize(); map.triggerRepaint(); } catch (_) {} }, t));

    map.on("style.load", () => {
      map.addSource("circuitos", { type: "geojson", data: dataRef.current, promoteId: "circuito_id" });
      map.addLayer({
        id: "fill", type: "fill", source: "circuitos",
        paint: { "fill-color": ["coalesce", ["get", "fillColor"], "#334155"], "fill-opacity": ["coalesce", ["get", "fillOpacity"], 0.62] },
      });
      map.addLayer({
        id: "outline", type: "line", source: "circuitos",
        paint: {
          "line-color": "#ffffff",
          "line-width": ["case", ["boolean", ["feature-state", "selected"], false], 3.2, 1],
          "line-opacity": ["case", ["boolean", ["feature-state", "selected"], false], 1, 0.45],
        },
      });
      map.on("click", "fill", (e) => onSelect(e.features[0].properties.circuito_id));
      map.on("mouseenter", "fill", () => { map.getCanvas().style.cursor = "pointer"; });
      map.on("mouseleave", "fill", () => { map.getCanvas().style.cursor = ""; });
      readyRef.current = true;
      renderData();
      renderSelection();
    });

    const ro = new ResizeObserver(() => map.resize());
    ro.observe(boxRef.current);
    requestAnimationFrame(() => map.resize());

    return () => { resizeTimers.forEach(clearTimeout); ro.disconnect(); map.remove(); readyRef.current = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => { if (readyRef.current) renderData(); /* eslint-disable-next-line */ }, [coloredGeo]);
  useEffect(() => { if (readyRef.current) renderSelection(); /* eslint-disable-next-line */ }, [selected]);

  function renderData() {
    const map = mapRef.current;
    if (!map || !map.getSource("circuitos")) return;
    const data = dataRef.current;
    map.getSource("circuitos").setData(data);

    markersRef.current.forEach((m) => m.remove());
    markersRef.current = data.features.map((f) => {
      const el = document.createElement("div");
      el.className = "clabel";
      el.textContent = f.properties.circuito_raw;
      return new maplibregl.Marker({ element: el }).setLngLat(centroid(f)).addTo(map);
    });

    if (distrito !== distritoRef.current && data.features.length) {
      const b = new maplibregl.LngLatBounds();
      data.features.forEach((f) => eachCoord(f.geometry, (c) => b.extend(c)));
      map.fitBounds(b, { padding: 50, duration: 400 });
      distritoRef.current = distrito;
    }
    map.triggerRepaint();
  }

  function renderSelection() {
    const map = mapRef.current;
    if (!map || !map.getSource("circuitos")) return;
    if (selRef.current) map.setFeatureState({ source: "circuitos", id: selRef.current }, { selected: false });
    if (selected) map.setFeatureState({ source: "circuitos", id: selected }, { selected: true });
    selRef.current = selected;
  }

  return <div className="map" ref={boxRef} />;
}
