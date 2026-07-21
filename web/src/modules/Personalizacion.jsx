import { SEGMENTOS, RECLAMOS } from "../data/mock.js";

// 05 · Personalización (add-on) — CRM de reclamos de campo, consentido y sin PII sensible.
// Contenido del mockup "Comando IA" (datos de ejemplo).
export default function Personalizacion() {
  return (
    <>
      <div className="topbar">
        <div>
          <div className="eyebrow">05 · Personalización</div>
          <h2>Personalización</h2>
          <div className="desc">CRM propio consentido y bots de campo · sin PII sensible</div>
        </div>
        <div className="right">
          <span className="pill-ghost"><span className="dot" />Vicente López · 1ª</span>
          <span className="pill-ghost">Campaña 2027</span>
        </div>
      </div>

      <div className="module">
        <div className="two-col">
          {/* Segmentos por adhesión */}
          <div className="card pad">
            <div className="eyebrow">Segmentos por adhesión <span className="tag" style={{ marginLeft: 8 }}>datos de ejemplo</span></div>
            <div className="sub">Anillos: duro (centro) → imposible (borde). El electorado por adhesión.</div>
            <div className="segs">
              {SEGMENTOS.map((s) => (
                <div className="seg-row" key={s.segmento}>
                  <span className={"seg-dot t-" + s.tone} />
                  <span className="seg-lbl">{s.segmento}</span>
                  <div className="part-track"><i style={{ width: s.pct * 2.5 + "%", background: `var(--${s.tone})` }} /></div>
                  <b className="seg-pct">{s.pct}%</b>
                </div>
              ))}
            </div>
            <div className="note" style={{ marginTop: 12 }}>
              12 meses — tamaño de cada segmento. El monitoreo continuo empieza un año antes.
            </div>
          </div>

          {/* CRM de reclamos */}
          <div className="card pad">
            <div className="eyebrow">Reclamos de campo · CRM consentido</div>
            <div className="sub">Bots de campo · reclamos y relevamiento — 18 sin asignar responsable</div>
            <div className="reclamos">
              {RECLAMOS.map((r) => (
                <div className="reclamo" key={r.t}>
                  <div>
                    <div className="reclamo-tit">{r.t}</div>
                    <div className="reclamo-src">{r.canal}</div>
                  </div>
                  <span className={"tag t-" + r.tone}>{r.estado}</span>
                </div>
              ))}
            </div>
            <div className="note" style={{ marginTop: 12 }}>
              CRM propio consentido: <b>1.240 contactos</b>. Sin PII sensible ni segmentación
              por preferencia política del vecino (CLAUDE.md §4 · privacidad por diseño).
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
