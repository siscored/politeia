import { MOTORES, SHARE_VOICE, AGENDA_MOTORES } from "../data/mock.js";

// 03 · Posicionamiento — share of answer en motores de IA (narrativa + benchmark).
// Contenido del mockup "Comando IA" (datos de ejemplo).
export default function Posicionamiento() {
  const maxSov = Math.max(...SHARE_VOICE.map((s) => s.val));
  return (
    <>
      <div className="topbar">
        <div>
          <div className="eyebrow">03 · Posicionamiento</div>
          <h2>Posicionamiento</h2>
          <div className="desc">Narrativa, benchmark y share of answer en motores de IA</div>
        </div>
        <div className="right">
          <span className="pill-ghost"><span className="dot" />Vicente López · 1ª</span>
          <span className="pill-ghost">Campaña 2027</span>
        </div>
      </div>

      <div className="module">
        {/* Presencia en motores */}
        <div className="card pad" style={{ marginBottom: 16 }}>
          <div className="eyebrow">Presencia en motores de IA <span className="tag" style={{ marginLeft: 8 }}>datos de ejemplo</span></div>
          <div className="sub">Consulta <b>“obras Vicente López”</b> · ¿aparece el candidato en la respuesta?</div>
          <div className="motores">
            {MOTORES.map((m) => (
              <div className={"motor " + (m.pres ? "on" : "off")} key={m.motor}>
                <span className="motor-dot">{m.pres ? "●" : "○"}</span>{m.motor}
              </div>
            ))}
          </div>
          <div className="note" style={{ marginTop: 10 }}>
            Aparece en <b>2 / 5</b> motores. Oportunidad de contenido optimizado para
            respuestas generativas · blindado contra prompt injection (CLAUDE.md §4).
          </div>
        </div>

        <div className="two-col">
          {/* Agenda: relevancia vs ocupación */}
          <div className="card pad">
            <div className="eyebrow">Agenda ↔ ocupación en respuestas</div>
            <div className="sub">Lo que le importa al votante vs. cuánto ocupa el candidato la respuesta</div>
            <div className="brecha-grid" style={{ gridTemplateColumns: "1fr" }}>
              {AGENDA_MOTORES.map((t) => (
                <div className="brecha" key={t.tema}>
                  <div className="brecha-head"><b>{t.tema}</b>
                    <span className={"tag " + (t.rel - t.ocup > 20 ? "t-warn" : "t-good")}>
                      {t.rel - t.ocup > 0 ? "brecha +" + (t.rel - t.ocup) : "cubierto"}
                    </span>
                  </div>
                  <div className="brecha-bar"><span>Relevancia</span><div className="track"><i style={{ width: t.rel + "%", background: "var(--brand)" }} /></div><em>{t.rel}</em></div>
                  <div className="brecha-bar"><span>Ocupación</span><div className="track"><i style={{ width: t.ocup + "%", background: "var(--muted)" }} /></div><em>{t.ocup}</em></div>
                </div>
              ))}
            </div>
          </div>

          {/* Share of voice */}
          <div className="card pad">
            <div className="eyebrow">Share of voice entre fuerzas</div>
            <div className="sub">Cuánto ocupa cada espacio la conversación generativa</div>
            <div className="sov">
              {SHARE_VOICE.map((s) => (
                <div className="sov-row" key={s.quien}>
                  <div className="sov-head"><span>{s.quien}</span><b>{s.val}</b></div>
                  <div className="part-track"><i style={{ width: (s.val / maxSov) * 100 + "%" }} /></div>
                </div>
              ))}
            </div>
            <div className="note" style={{ marginTop: 12 }}>
              El principal opositor lidera el <b>share of answer</b>. Nube de conceptos y
              benchmark se cablean sobre la escucha de Defensa.
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
