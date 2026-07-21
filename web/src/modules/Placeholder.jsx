import { MOCK_NOTE } from "../data/mock.js";

// Módulos aún no cableados (Defensa, Posicionamiento, Producción, Personalización).
// Mantienen la estructura del mockup; el contenido se trabaja post-MVP.
export default function Placeholder({ num, name, desc, star, detalle }) {
  return (
    <>
      <div className="topbar">
        <div>
          <div className="eyebrow">{num} · {name}{star ? " ★" : ""}</div>
          <h2>{name}</h2>
          <div className="desc">{desc}</div>
        </div>
        <div className="right">
          <span className="pill-ghost"><span className="dot" />Vicente López · 1ª</span>
          <span className="pill-ghost">Campaña 2027</span>
        </div>
      </div>
      <div className="module">
        <div className="card pad">
          <span className="tag">datos de ejemplo</span>
          <h3 style={{ margin: "12px 0 6px" }}>{detalle}</h3>
          <div className="note">{MOCK_NOTE}</div>
        </div>
      </div>
    </>
  );
}
