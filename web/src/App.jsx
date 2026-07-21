import React, { useEffect, useMemo, useState } from "react";
import geo from "./circuitos.json";
import MapView from "./MapView.jsx";
import { famOf, OTHER, title } from "./families.js";
import { fetchMeta, fetchMapa } from "./api.js";

const CARGO_ORDER = ["PRESIDENTE", "GOBERNADOR", "INTENDENTE", "SENADORES_NAC", "DIPUTADOS_NAC",
  "SENADORES_PROV", "DIPUTADOS_PROV", "CONCEJALES", "MERCOSUR_NAC", "MERCOSUR_REG"];
const niceCargo = (c) => {
  const s = c.replace("_NAC", " Nac.").replace("_PROV", " Prov.").replace("_REG", " Reg.").replace("_", " ");
  return s.charAt(0) + s.slice(1).toLowerCase();
};
const padre = (cid) => { const m = String(cid).match(/^(\d+)/); return m ? m[1].padStart(5, "0") : cid; };

export default function App() {
  const [meta, setMeta] = useState(null);
  const [distrito, setDistrito] = useState("pilar");
  const [anio, setAnio] = useState(null);
  const [cargo, setCargo] = useState(null);
  const [combo, setCombo] = useState(null);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => { fetchMeta().then(setMeta); }, []);

  // años y cargos disponibles para el distrito elegido
  const anios = useMemo(() => meta ? Object.keys(meta.disponibles[distrito] || {}).sort() : [], [meta, distrito]);
  const cargos = useMemo(() => {
    if (!meta || !anio) return [];
    const cs = [...(meta.disponibles[distrito]?.[anio] || [])];
    cs.sort((a, b) => CARGO_ORDER.indexOf(a) - CARGO_ORDER.indexOf(b));
    return cs;
  }, [meta, distrito, anio]);

  // fijar defaults válidos cuando cambian meta/distrito/anio
  useEffect(() => { if (anios.length && !anios.includes(anio)) setAnio(anios[anios.length - 1]); }, [anios]);
  useEffect(() => {
    if (cargos.length && !cargos.includes(cargo)) setCargo(cargos.includes("PRESIDENTE") ? "PRESIDENTE" : cargos[0]);
  }, [cargos]);

  // traer datos del combo elegido
  useEffect(() => {
    if (!(distrito && anio && cargo)) return;
    setLoading(true); setSelected(null);
    fetchMapa(distrito, anio, cargo).then((d) => { setCombo(d); setLoading(false); });
  }, [distrito, anio, cargo]);

  const features = useMemo(() => geo.features.filter((f) => f.properties.municipio === distrito), [distrito]);

  // normalizar respuesta del API + lookup por circuito (con fallback a circuito_padre)
  const { byCid, uniVal, uniform, muniWinner, wins, present } = useMemo(() => {
    const empty = { byCid: new Map(), uniVal: null, uniform: false, muniWinner: null, wins: {}, present: {} };
    if (!combo || !combo.circuitos) return empty;
    const map = new Map();
    combo.circuitos.forEach((c) => map.set(c.circuito_id, {
      g: c.ganador?.agrupacion, gp: c.ganador?.porcentaje, comp: c.composicion, gran: c.granularidad,
    }));
    const uniform = features.every((f) => !map.has(f.properties.circuito_id) && !map.has(padre(f.properties.circuito_id)));
    const uniVal = uniform ? [...map.values()][0] || null : null;
    // ganador del municipio por votos totales
    const totals = {};
    combo.circuitos.forEach((c) => c.composicion.forEach((x) => { totals[x.agrupacion] = (totals[x.agrupacion] || 0) + x.votos; }));
    let muniWinner = uniVal;
    const tot = Object.values(totals).reduce((a, b) => a + b, 0);
    if (tot) { const w = Object.keys(totals).reduce((a, b) => totals[a] >= totals[b] ? a : b); muniWinner = { g: w, gp: (totals[w] / tot) * 100 }; }
    // circuitos ganados por familia + leyenda
    const wins = {}, present = {};
    features.forEach((f) => {
      const rec = map.get(f.properties.circuito_id) || map.get(padre(f.properties.circuito_id)) || uniVal;
      if (rec) { const fm = famOf(rec.g); wins[fm.key] = (wins[fm.key] || 0) + 1; present[fm.key] = { c: fm.c, n: (present[fm.key]?.n || 0) + 1 }; }
    });
    return { byCid: map, uniVal, uniform, muniWinner, wins, present };
  }, [combo, features]);

  const lookup = (cid) => byCid.get(cid) || byCid.get(padre(cid)) || uniVal;
  const winsSorted = Object.entries(wins).sort((a, b) => b[1] - a[1]);
  const fam = muniWinner ? famOf(muniWinner.g) : OTHER;
  const M = features.length;
  const selRec = selected ? lookup(selected) : null;

  return (
    <div className="wrap">
      <header className="top">
        <div className="brand">
          <div className="logo">P</div>
          <div><h1>POLITEIA</h1><div className="sub">Comando IA · estructura de votos por circuito</div></div>
        </div>
        <div className="spacer" />
        <div className="controls">
          <div className="ctl"><label>Distrito</label>
            <div className="seg">
              {["pilar", "san_fernando"].map((d) => (
                <button key={d} aria-pressed={distrito === d} onClick={() => setDistrito(d)}>
                  {d === "pilar" ? "Pilar" : "San Fernando"}
                </button>
              ))}
            </div>
          </div>
          <div className="ctl"><label>Elección</label>
            <select value={anio || ""} onChange={(e) => setAnio(e.target.value)}>
              {anios.map((y) => <option key={y} value={y}>{y}</option>)}
            </select>
          </div>
          <div className="ctl"><label>Cargo</label>
            <select value={cargo || ""} onChange={(e) => setCargo(e.target.value)}>
              {cargos.map((c) => <option key={c} value={c}>{niceCargo(c)}</option>)}
            </select>
          </div>
        </div>
      </header>

      <div className="grid">
        <div className="mappanel">
          <div className="hint">{selected ? `${selected}${selRec ? "" : " · sin dato"}` : loading ? "Cargando…" : "Pasá el mouse por un circuito"}</div>
          <MapView features={features} lookup={lookup} selected={selected} onHover={setSelected} />
        </div>

        <div className="side">
          <div className="card pad stat">
            <div className="eyebrow">{uniform ? "Ganador (nivel municipio)" : "Ganador del municipio"}</div>
            <div className="big">
              {muniWinner ? (<><span className="swatch" style={{ background: fam.c }} />{title(muniWinner.g)} <small>{muniWinner.gp ? muniWinner.gp.toFixed(1) + "%" : ""}</small></>) : "—"}
            </div>
            <div className="corte">
              {uniform ? (<>Esta elección solo tiene dato a <b>nivel municipio</b> — el mapa se pinta uniforme (años viejos / sept-2025).</>)
                : winsSorted.length ? (<>Circuitos ganados: {winsSorted.map(([k, n], i) => <span key={k}>{i ? " · " : ""}<b>{n}</b> {k}</span>)}. {winsSorted.length > 1 && <>El municipio no cuenta toda la historia: <b>{winsSorted[0][0]}</b> lideró {winsSorted[0][1]} de {M} circuitos.</>}</>) : null}
            </div>
          </div>

          <div className="card pad">
            <div className="eyebrow" style={{ marginBottom: 10 }}>Fuerzas</div>
            <div className="legend">
              {Object.entries(present).sort((a, b) => b[1].n - a[1].n).map(([k, v]) => (
                <div className="row" key={k}><span className="swatch" style={{ background: v.c }} />{k}<span className="n">{v.n}</span></div>
              ))}
              {!Object.keys(present).length && <div className="empty">—</div>}
            </div>
          </div>

          <div className="card pad detail">
            <div className="cid">{selRec ? `CIRCUITO ${selected}${selRec.gran === "municipio" ? " · nivel municipio" : ""}` : "— circuito —"}</div>
            {selRec ? (
              <>
                <h3><span className="swatch" style={{ background: famOf(selRec.g).c }} />{title(selRec.g)} <span className="muted">gana con {selRec.gp ? selRec.gp.toFixed(1) : "—"}%</span></h3>
                <div className="bars">
                  {(() => { const max = Math.max(...selRec.comp.map((x) => x.porcentaje || 0), 1);
                    return selRec.comp.map((x, i) => (
                      <div className="bar" key={i}>
                        <div className="lab"><span>{title(x.agrupacion)}</span><span className="pct">{(x.porcentaje ?? 0).toFixed(1)}%</span></div>
                        <div className="track"><i style={{ width: `${((x.porcentaje || 0) / max * 100).toFixed(1)}%`, background: famOf(x.agrupacion).c }} /></div>
                      </div>)); })()}
                </div>
              </>
            ) : (<><h3>Elegí un circuito</h3><div className="empty">Pasá el mouse por el mapa para ver la composición del voto.</div></>)}
          </div>
        </div>
      </div>

      <footer>
        <span className="tag">datos reales</span>&nbsp; Pilar + San Fernando, 2003–2025 (DINE provisorio + Junta PBA). Colores por familia política.
        El voto por circuito revela lo que el total del municipio esconde. Fuente polígonos: circuitos PBA (CNE / datos.gba.gob.ar).
      </footer>
    </div>
  );
}
