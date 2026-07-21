import { KPIS, PULSO, ALERTAS, BRECHA } from "../data/mock.js";

export default function Resumen() {
  return (
    <>
      <div className="topbar">
        <div>
          <div className="eyebrow">00 · Dashboard</div>
          <h2>Resumen</h2>
          <div className="desc">Pulso de campaña · estado de los cinco frentes</div>
        </div>
        <div className="right">
          <span className="pill-ghost"><span className="dot" />Vicente López · 1ª</span>
          <span className="pill-ghost">Campaña 2027</span>
        </div>
      </div>

      <div className="module">
        {/* KPIs */}
        <div className="kpi-row">
          {KPIS.map((k) => (
            <div className="card pad kpi" key={k.label}>
              <div className="eyebrow">{k.label}</div>
              <div className="kpi-big">{k.value} <small className={"delta " + (k.delta.startsWith("−") ? "down" : "up")}>{k.delta}</small></div>
              <div className="kpi-note">{k.note}</div>
            </div>
          ))}
        </div>

        <div className="two-col">
          {/* Pulso de los 5 frentes */}
          <div className="card pad">
            <div className="eyebrow">Pulso de los cinco frentes</div>
            <div className="sub">Estado del día · clic para abrir el módulo</div>
            <div className="pulso">
              {PULSO.map((p) => (
                <div className="pulso-row" key={p.modulo}>
                  <div className={"pulso-bar t-" + p.tone} />
                  <div className="pulso-body">
                    <div className="pulso-head"><b>{p.modulo}</b><span className={"tag t-" + p.tone}>{p.tag}</span></div>
                    <div className="pulso-det">{p.detalle}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Alertas por velocidad */}
          <div className="card pad">
            <div className="eyebrow">Alertas por velocidad</div>
            <div className="sub">Llegar antes del pico</div>
            <div className="alertas">
              {ALERTAS.map((a) => (
                <div className="alerta" key={a.titulo}>
                  <div className={"alerta-bar t-" + a.tone} />
                  <div>
                    <div className="alerta-tit">{a.titulo}</div>
                    <div className="alerta-src">{a.fuente} · <b className={"t-" + a.tone}>{a.velo}</b></div>
                  </div>
                </div>
              ))}
              <div className="note">Prioridad = alcance × negatividad × credibilidad. La respuesta la decide el humano.</div>
            </div>
          </div>
        </div>

        {/* Brecha agenda ↔ mensaje */}
        <div className="card pad">
          <div className="eyebrow">Brecha agenda ↔ mensaje</div>
          <div className="sub">Lo que le importa al votante vs. lo que dice el candidato (Vicente López)</div>
          <div className="brecha-grid">
            {BRECHA.map((b) => (
              <div className="brecha" key={b.tema}>
                <div className="brecha-head"><b>{b.tema}</b><span className="tag">brecha {b.brecha}</span></div>
                <div className="brecha-bar"><span>Votante</span><div className="track"><i style={{ width: b.votante + "%", background: "var(--brand)" }} /></div><em>{b.votante}</em></div>
                <div className="brecha-bar"><span>Candidato</span><div className="track"><i style={{ width: b.candidato + "%", background: "var(--muted)" }} /></div><em>{b.candidato}</em></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
