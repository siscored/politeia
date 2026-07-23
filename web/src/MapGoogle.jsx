import { useEffect, useRef } from "react";
import { eachCoord, centroid, coreFeatures } from "./geoutil.js";

const KEY = import.meta.env.VITE_GOOGLE_MAPS_KEY;

// Estilo oscuro para que combine con la consola (equivalente al mockup).
const DARK = [
  { elementType: "geometry", stylers: [{ color: "#17263c" }] },
  { elementType: "labels.text.stroke", stylers: [{ color: "#0e1a2b" }] },
  { elementType: "labels.text.fill", stylers: [{ color: "#8aa0bd" }] },
  { featureType: "administrative", elementType: "geometry", stylers: [{ color: "#2a3d57" }] },
  { featureType: "administrative.locality", elementType: "labels.text.fill", stylers: [{ color: "#c1d0e6" }] },
  { featureType: "administrative.neighborhood", elementType: "labels.text.fill", stylers: [{ color: "#8296b4" }] },
  { featureType: "poi", stylers: [{ visibility: "off" }] },
  { featureType: "road", elementType: "geometry", stylers: [{ color: "#243654" }] },
  { featureType: "road", elementType: "labels", stylers: [{ visibility: "off" }] },
  { featureType: "road.arterial", elementType: "geometry", stylers: [{ color: "#2b4066" }] },
  { featureType: "road.highway", elementType: "geometry", stylers: [{ color: "#34507d" }] },
  { featureType: "transit", stylers: [{ visibility: "off" }] },
  { featureType: "water", elementType: "geometry", stylers: [{ color: "#0a1424" }] },
];

function loadGoogle() {
  if (window.google && window.google.maps) return Promise.resolve();
  if (!window.__gmapsPromise) {
    window.__gmapsPromise = new Promise((resolve, reject) => {
      const s = document.createElement("script");
      s.src = `https://maps.googleapis.com/maps/api/js?key=${KEY}&v=weekly`;
      s.async = true;
      s.onload = resolve;
      s.onerror = reject;
      document.head.appendChild(s);
    });
  }
  return window.__gmapsPromise;
}

export default function MapGoogle({ coloredGeo, distrito, selected, onSelect }) {
  const boxRef = useRef(null);
  const mapRef = useRef(null);
  const featsRef = useRef([]);
  const markersRef = useRef([]);
  const fitRef = useRef({ sig: null });
  const dataRef = useRef(coloredGeo);
  dataRef.current = coloredGeo;

  useEffect(() => {
    let cancelled = false;
    loadGoogle().then(() => {
      if (cancelled || !boxRef.current) return;
      const g = window.google.maps;
      const map = new g.Map(boxRef.current, {
        center: { lat: -34.45, lng: -58.9 }, zoom: 11,
        disableDefaultUI: true, zoomControl: true,
        // En touch, "greedy" se traga el scroll de la página: arrastrar sobre el
        // mapa paneaba en vez de scrollear y quedabas trabado en el mapa.
        // "cooperative" = un dedo scrollea la página, dos dedos mueven el mapa.
        gestureHandling: window.matchMedia("(pointer: coarse)").matches ? "cooperative" : "greedy",
        backgroundColor: "#0e1a2b", styles: DARK,
      });
      mapRef.current = map;
      map.data.setStyle((feature) => ({
        fillColor: feature.getProperty("fillColor") || "#334155",
        fillOpacity: feature.getProperty("fillOpacity") ?? 0.55,
        strokeColor: "#ffffff", strokeWeight: 1, strokeOpacity: 0.5,
      }));
      map.data.addListener("click", (e) => {
        const cid = e.feature.getProperty("circuito_id");
        if (cid) onSelect(cid);
      });
      map.data.addListener("mouseover", () => { map.setOptions({ draggableCursor: "pointer" }); });
      render();
      // Google Maps a veces tarda en pintar los tiles si el contenedor no tenía
      // tamaño estable al crear; un resize trigger escalonado lo destraba.
      [200, 700, 1600].forEach((t) => setTimeout(() => { try { g.event.trigger(map, "resize"); } catch (_) {} }, t));
    }).catch((err) => console.error("Google Maps no cargó (¿referer/API key?):", err));
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => { render(); /* eslint-disable-next-line */ }, [coloredGeo, selected]);

  function render() {
    const map = mapRef.current;
    if (!map || !window.google) return;
    const g = window.google.maps;
    const data = dataRef.current;

    // reemplazar features
    featsRef.current.forEach((f) => map.data.remove(f));
    featsRef.current = map.data.addGeoJson(data);

    // labels (marker con ícono invisible + texto)
    markersRef.current.forEach((m) => m.setMap(null));
    markersRef.current = data.features.map((f) => {
      const c = centroid(f);
      return new g.Marker({
        position: { lat: c[1], lng: c[0] }, map,
        clickable: false,
        icon: { path: g.SymbolPath.CIRCLE, scale: 0 },
        label: { text: f.properties.circuito_raw, color: "#ffffff", fontSize: "11px", fontWeight: "600" },
      });
    });

    // fit bounds al cambiar de distrito
    // Re-encuadrar cuando cambia el CONJUNTO poblado (distrito nuevo, o cuando
    // llegan los votos y coreFeatures pasa de 16 → 13 excluyendo el delta).
    const core = coreFeatures(data.features);
    const sig = distrito + "|" + core.map((f) => f.properties.circuito_id).sort().join(",");
    if (core.length && sig !== fitRef.current.sig) {
      const b = new g.LatLngBounds();
      core.forEach((f) => eachCoord(f.geometry, (co) => b.extend({ lat: co[1], lng: co[0] })));
      map.fitBounds(b, 48);
      fitRef.current = { sig };
    }

    // selección: resaltar el circuito elegido
    map.data.revertStyle();
    if (selected) {
      const sel = featsRef.current.find((f) => f.getProperty("circuito_id") === selected);
      if (sel) map.data.overrideStyle(sel, { strokeColor: "#ffffff", strokeWeight: 3.5, strokeOpacity: 1, zIndex: 20 });
    }
  }

  return <div className="map" ref={boxRef} />;
}
