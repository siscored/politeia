import { PRODUCCION_FLOW, FUNNEL } from "../data/mock.js";

// 04 · Producción — fábrica de contenido con termómetro orgánico.
// Contenido del mockup "Comando IA" (datos de ejemplo).
export default function Produccion() {
  const base = FUNNEL[0].n;
  return (
    <>
      <div className="topbar">
        <div>
          <div className="eyebrow">04 · Producción</div>
          <h2>Producción</h2>
          <div className="desc">Termómetro de piezas · la IA genera el volumen, el humano decide</div>
        </div>
        <div className="right">
          <span className="pill-ghost"><span className="dot" />Vicente López · 1ª</span>
          <span className="pill-ghost">Campaña 2027</span>
        </div>
      </div>

      <div className="module">
        {/* Flujo de brief a variantes */}
        <div className="card pad" style={{ marginBottom: 16 }}>
          <div className="eyebrow">De brief a variantes <span className="tag" style={{ marginLeft: 8 }}>datos de ejemplo</span></div>
          <div className="sub">Brief → la IA genera variantes → termómetro A/B → decisión humana</div>
          <div className="flow">
            {PRODUCCION_FLOW.map((p, i) => (
              <div className="flow-step" key={p.paso}>
                <div className="flow-num">{i + 1}</div>
                <div className="flow-tit">{p.paso}</div>
                <div className="flow-det">{p.detalle}</div>
              </div>
            ))}
          </div>
          <div className="note" style={{ marginTop: 12 }}>
            Se mide en orgánico; la inversión va solo al contenido que sube. TikTok queda
            en orgánico (no admite pauta política).
          </div>
        </div>

        {/* Embudo de canales propios */}
        <div className="card pad">
          <div className="eyebrow">Canales propios · embudo de mensajes</div>
          <div className="sub">Bots de campo · volumen agregado (ejemplo)</div>
          <div className="funnel">
            {FUNNEL.map((f) => (
              <div className="funnel-row" key={f.paso}>
                <div className="funnel-lbl">{f.paso}</div>
                <div className="funnel-track"><i style={{ width: (f.n / base) * 100 + "%" }} /></div>
                <div className="funnel-n">{f.n.toLocaleString("es-AR")}</div>
              </div>
            ))}
          </div>
          <div className="note" style={{ marginTop: 12 }}>
            <b>{FUNNEL[FUNNEL.length - 1].n.toLocaleString("es-AR")}</b> derivados a humano:
            la IA genera el volumen, el humano cierra.
          </div>
        </div>
      </div>
    </>
  );
}
