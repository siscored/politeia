import { useEffect, useMemo, useRef, useState } from "react";
import geo from "../circuitos.json";
import MapGoogle from "../MapGoogle.jsx";
import { famOf, OTHER, title } from "../families.js";
import { fetchMeta, fetchMapa } from "../api.js";

const SUBTABS = ["Estructura de votos", "Composición del voto", "Issues por circuito", "Sentimiento por fuente", "Recomendador IA"];
const CARGO_ORDER = ["PRESIDENTE", "GOBERNADOR", "INTENDENTE", "SENADORES_NAC", "DIPUTADOS_NAC", "SENADORES_PROV", "DIPUTADOS_PROV", "CONCEJALES", "MERCOSUR_NAC", "MERCOSUR_REG"];
const DIST = { pilar: "Pilar", san_fernando: "San Fernando" };
const niceCargo = (c) => { const s = c.replace("_NAC", " Nac.").replace("_PROV", " Prov.").replace("_REG", " Reg.").replace("_", " "); return s.charAt(0) + s.slice(1).toLowerCase(); };
const padre = (cid) => { const m = String(cid).match(/^(\d+)/); return m ? m[1].padStart(5, "0") : cid; };
const fmt = (n) => n == null ? "—" : n.toLocaleString("es-AR");
// El API deja `porcentaje: null` en blanco/nulo/impugnado/recurrido/comando: no
// son voto positivo y no tienen % sobre válidos. Se excluyen de la composición y
// de los totales (mismo criterio en circuito y en municipio).
const esPositivo = (x) => x != null && Number.isFinite(x.porcentaje);

export default function Inteligencia() {
  const [meta, setMeta] = useState(null);
  const [distrito, setDistrito] = useState("pilar");
  const [anio, setAnio] = useState(null);
  const [cargo, setCargo] = useState(null);
  const [combo, setCombo] = useState(null);
  const [selected, setSelected] = useState(null);
  const [colorMode, setColorMode] = useState("ganador");
  const pedido = useRef(null); // última combinación pedida (guard de respuestas fuera de orden)

  useEffect(() => { fetchMeta().then(setMeta); }, []);

  const anios = useMemo(() => meta ? Object.keys(meta.disponibles[distrito] || {}).sort() : [], [meta, distrito]);
  const cargos = useMemo(() => {
    if (!meta || !anio) return [];
    return [...(meta.disponibles[distrito]?.[anio] || [])].sort((a, b) => CARGO_ORDER.indexOf(a) - CARGO_ORDER.indexOf(b));
  }, [meta, distrito, anio]);

  useEffect(() => { if (anios.length && !anios.includes(anio)) setAnio(anios[anios.length - 1]); }, [anios]);
  useEffect(() => { if (cargos.length && !cargos.includes(cargo)) setCargo(cargos.includes("PRESIDENTE") ? "PRESIDENTE" : cargos[0]); }, [cargos]);
  // Al cambiar de año, `cargo` queda un render obsoleto hasta que el efecto de
  // arriba lo reajusta: no pedir esa combinación intermedia (da 404, ej.
  // 2007+DIPUTADOS_NAC) y descartar toda respuesta que ya no sea la vigente —
  // sin el guard la request muerta resolvía última y pisaba la buena.
  useEffect(() => {
    if (!(distrito && anio && cargo) || !cargos.includes(cargo)) return;
    const clave = `${distrito}|${anio}|${cargo}`;
    pedido.current = clave;
    setSelected(null);
    fetchMapa(distrito, anio, cargo)
      .then((r) => { if (pedido.current === clave) setCombo(r); })
      .catch((e) => { if (pedido.current === clave) { console.error("fetchMapa", clave, e); setCombo({ circuitos: [] }); } });
  }, [distrito, anio, cargo, cargos]);

  const features = useMemo(() => geo.features.filter((f) => f.properties.municipio === distrito), [distrito]);

  const model = useMemo(() => {
    const map = new Map();
    (combo?.circuitos || []).forEach((c) => {
      const comp = (c.composicion || []).filter(esPositivo);
      map.set(c.circuito_id, {
        g: c.ganador?.agrupacion, gp: c.ganador?.porcentaje, comp, gran: c.granularidad,
        validos: comp.reduce((a, x) => a + (x.votos || 0), 0),
      });
    });
    const lookup = (cid) => map.get(cid) || map.get(padre(cid)) || null;
    const uniform = features.length > 0 && features.every((f) => !lookup(f.properties.circuito_id));
    const uniVal = uniform ? [...map.values()][0] || null : null;
    const totals = {};
    (combo?.circuitos || []).forEach((c) => c.composicion?.filter(esPositivo).forEach((x) => { totals[x.agrupacion] = (totals[x.agrupacion] || 0) + (x.votos || 0); }));
    const tot = Object.values(totals).reduce((a, b) => a + b, 0);
    const muniComp = Object.entries(totals).map(([agrupacion, votos]) => ({ agrupacion, votos, porcentaje: tot ? votos / tot * 100 : 0 })).sort((a, b) => b.votos - a.votos);
    const muniWinner = muniComp[0] ? { g: muniComp[0].agrupacion, gp: muniComp[0].porcentaje } : uniVal;
    const wins = {}, present = {};
    features.forEach((f) => { const rec = lookup(f.properties.circuito_id) || uniVal; if (rec) { const fm = famOf(rec.g); wins[fm.key] = (wins[fm.key] || 0) + 1; present[fm.key] = { label: fm.label, c: fm.c, n: (present[fm.key]?.n || 0) + 1 }; } });
    return { map, lookup, uniform, uniVal, muniComp, muniWinner, muniValidos: tot, wins, present };
  }, [combo, features]);

  const coloredGeo = useMemo(() => {
    const feats = features.map((f) => {
      const rec = model.lookup(f.properties.circuito_id) || model.uniVal;
      const fam = rec ? famOf(rec.g) : OTHER;
      let fillOpacity = 0.62;
      if (colorMode === "margen" && rec?.comp?.length >= 1) {
        const m = (rec.comp[0].porcentaje || 0) - (rec.comp[1]?.porcentaje || 0);
        fillOpacity = Math.max(0.25, Math.min(0.92, 0.25 + m / 55));
      }
      return { ...f, properties: { ...f.properties, fillColor: rec ? fam.c : "#334155", fillOpacity, weight: rec?.validos || 0 } };
    });
    return { type: "FeatureCollection", features: feats };
  }, [features, model, colorMode]);

  const selRec = selected ? model.lookup(selected) : null;
  const winsSorted = Object.entries(model.wins).sort((a, b) => b[1] - a[1]);
  const legend = Object.entries(model.present).sort((a, b) => b[1].n - a[1].n);
  const compData = selRec ? selRec.comp : model.muniComp;
  const margin = compData?.length >= 2 ? (compData[0].porcentaje - compData[1].porcentaje) : null;
  const winner = selRec ? { g: selRec.g, gp: selRec.gp } : model.muniWinner;
  const sinDatos = !combo?.circuitos?.length;

  return (
    <>
      <div className="topbar">
        <div>
          <div className="eyebrow">02 · Inteligencia ★</div>
          <h2>Inteligencia</h2>
          <div className="desc">Estructura de votos por circuito · foto del territorio</div>
        </div>
        <div className="right">
          <span className="pill-ghost"><span className="dot" />{DIST[distrito]} · 1ª</span>
          <span className="pill-ghost">Campaña {anio || "—"}</span>
        </div>
      </div>

      <div className="subtabs">
        {SUBTABS.map((t, i) => (
          <button key={t} className={"subtab" + (i === 0 ? " active" : "")} disabled={i > 0}>{t}</button>
        ))}
      </div>

      <div className="module">
        <div className="content">
          <div className="mapcard">
            <div className="filterbar">
              <div className="fbrow">
                <div className="seg">
                  {Object.keys(DIST).map((d) => (
                    <button key={d} className={distrito === d ? "on" : ""} onClick={() => setDistrito(d)}>{DIST[d]} · {geo.features.filter(f => f.properties.municipio === d).length} circ.</button>
                  ))}
                </div>
                <div className="spacer" />
                <button className={"chip" + (colorMode === "ganador" ? " on" : "")} onClick={() => setColorMode("ganador")}>Fuerza ganadora</button>
                <button className="chip" disabled style={{ opacity: .5 }}>% de una fuerza</button>
                <button className={"chip" + (colorMode === "margen" ? " on" : "")} onClick={() => setColorMode("margen")}>Margen</button>
                <button className="chip" disabled style={{ opacity: .5 }}>Corte de boleta</button>
              </div>
              <div className="fbrow">
                <span className="lbl">Elección</span>
                <div className="seg">{anios.map((y) => <button key={y} className={anio === y ? "on" : ""} onClick={() => setAnio(y)}>{y}</button>)}</div>
                <span className="lbl" style={{ marginLeft: 8 }}>Cargo</span>
                <div className="seg" style={{ flexWrap: "wrap" }}>{cargos.map((c) => <button key={c} className={cargo === c ? "on" : ""} onClick={() => setCargo(c)}>{niceCargo(c)}</button>)}</div>
              </div>
            </div>
            <MapGoogle coloredGeo={coloredGeo} distrito={distrito} selected={selected} onSelect={setSelected} />
            <div className="map-credit">● Google Maps · capa real</div>
          </div>

          <div className="panel">
            <div className="crumbs">PBA <span style={{ opacity: .5 }}>›</span> 1ª sección <span style={{ opacity: .5 }}>›</span> <b>{DIST[distrito]}</b>{selRec && <> <span style={{ opacity: .5 }}>›</span> <b>Circuito {selected}</b></>}</div>
            <div>
              <div className="p-title">{selRec ? `Circuito ${selected}` : DIST[distrito]}</div>
              <div className="p-meta">
                {selRec ? `Circuito · ${niceCargo(cargo || "")} ${anio} · ${fmt(selRec.validos)} válidos · ` : `${features.length} circuitos · ${niceCargo(cargo || "")} ${anio} · ${fmt(model.muniValidos)} válidos · `}
                <span className="ok">oficial/provisorio</span>
              </div>
            </div>
            <div className="divider" />
            {sinDatos && (
              <div className="note">Sin datos para <b>{niceCargo(cargo || "")} {anio}</b> en {DIST[distrito]}. Probá otro cargo o elección.</div>
            )}
            {!sinDatos && winner && (
              <div>
                <div className="eyebrow" style={{ marginBottom: 9 }}>Composición del voto{selRec ? "" : " · municipio"}</div>
                <div className="stacked">
                  {compData.slice(0, 6).map((x, i) => <i key={i} style={{ width: `${x.porcentaje || 0}%`, background: famOf(x.agrupacion).c }} title={title(x.agrupacion)} />)}
                </div>
                <div className="complist">
                  {compData.slice(0, 5).map((x, i) => (
                    <div className="crow" key={i}><span className="swatch" style={{ background: famOf(x.agrupacion).c }} />{title(x.agrupacion)}<span className="pct">{Number.isFinite(x.porcentaje) ? x.porcentaje.toFixed(1) + "%" : "—"}</span></div>
                  ))}
                </div>
              </div>
            )}
            <div className="kv">
              <div><div className="k">Ganador</div><div className="val"><span className="swatch" style={{ background: famOf(winner?.g).c }} />{famOf(winner?.g).label.split(" / ")[0]}</div></div>
              <div><div className="k">Margen (1°–2°)</div><div className="val">{Number.isFinite(margin) ? margin.toFixed(1) + " pts" : "—"}</div></div>
            </div>
            <div>
              <div className="eyebrow" style={{ marginBottom: 9 }}>Leyenda · fuerza ganadora</div>
              <div className="legend">
                {legend.map(([k, v]) => <div className="crow" key={k}><span className="swatch" style={{ background: v.c }} />{v.label}<span className="n">{v.n}</span></div>)}
              </div>
            </div>
            {!selRec && winsSorted.length > 1 && (
              <div className="note"><b>{DIST[distrito]}:</b> {model.muniWinner && famOf(model.muniWinner.g).label.split(" / ")[0]} ganó el municipio, pero <b>{winsSorted[0][0]}</b> lideró {winsSorted[0][1]} de {features.length} circuitos. Pasá el mouse por el mapa para ver cada circuito.</div>
            )}
            <div className="note" style={{ borderTop: "1px solid var(--line)", paddingTop: 10 }}>
              Cifras DINE (provisorio) + Junta PBA (definitivo). Polígonos: circuitos PBA (CNE / datos.gba.gob.ar), join por <code>circuito_id</code>. Colores por familia (§design system).
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
