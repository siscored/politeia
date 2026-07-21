import { ESCUCHA, PROTOCOLO } from "../data/mock.js";

// 01 · Defensa — escucha activa por velocidad + protocolo de respuesta.
// Contenido del mockup "Comando IA" (datos de ejemplo). El motor se cablea post-MVP.
export default function Defensa() {
  return (
    <>
      <div className="topbar">
        <div>
          <div className="eyebrow">01 · Defensa</div>
          <h2>Defensa</h2>
          <div className="desc">Escucha activa y alerta temprana por velocidad · protocolo de respuesta</div>
        </div>
        <div className="right">
          <span className="pill-ghost"><span className="dot" />Vicente López · 1ª</span>
          <span className="pill-ghost">Campaña 2027</span>
        </div>
      </div>

      <div className="module">
        <div className="two-col">
          {/* Escucha social */}
          <div className="card pad">
            <div className="eyebrow">Escucha social <span className="tag" style={{ marginLeft: 8 }}>datos de ejemplo</span></div>
            <div className="sub">Fuentes curadas + canales propios · positivo / neutro / negativo</div>
            <div className="escucha">
              {ESCUCHA.map((f) => (
                <div className="esc-row" key={f.fuente}>
                  <div className="esc-head">
                    <b>{f.fuente}</b>
                    <span className="esc-vol">{f.volumen.toLocaleString("es-AR")} menciones</span>
                  </div>
                  <div className="stacked">
                    <i style={{ width: f.pos + "%", background: "var(--good)" }} />
                    <i style={{ width: f.neu + "%", background: "var(--muted)" }} />
                    <i style={{ width: f.neg + "%", background: "var(--crit)" }} />
                  </div>
                  <div className="esc-foot">
                    {f.temas.map((t) => <span className="chip-mini" key={t}>{t}</span>)}
                    <span className="esc-src">{f.curada ? "curada" : "cruda"} · {f.procesa}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Protocolo de respuesta */}
          <div className="card pad">
            <div className="eyebrow">Protocolo de respuesta</div>
            <div className="sub">Llegar antes del pico — la respuesta la decide el humano</div>
            <ol className="proto">
              {PROTOCOLO.map((p, i) => (
                <li className="proto-row" key={p.paso}>
                  <span className="proto-num">{i + 1}</span>
                  <div>
                    <div className="proto-tit">{p.paso}</div>
                    <div className="proto-det">{p.detalle}</div>
                  </div>
                </li>
              ))}
            </ol>
            <div className="note" style={{ marginTop: 12 }}>
              Prioridad = <b>Alcance × negatividad × credibilidad</b>. El sistema detecta
              y ordena; nunca responde solo.
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
