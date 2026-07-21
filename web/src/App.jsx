import { useState } from "react";
import Resumen from "./modules/Resumen.jsx";
import Defensa from "./modules/Defensa.jsx";
import Inteligencia from "./modules/Inteligencia.jsx";
import Posicionamiento from "./modules/Posicionamiento.jsx";
import Produccion from "./modules/Produccion.jsx";
import Personalizacion from "./modules/Personalizacion.jsx";

// Registro de módulos (estructura del mockup Comando IA). Cada uno es un
// componente propio; Inteligencia tiene el mapa real (Pilar/San Fernando),
// el resto replica el mockup con datos de ejemplo (Vicente López).
const MODULES = [
  { num: "00", name: "Resumen", group: "op", render: () => <Resumen /> },
  { num: "01", name: "Defensa", group: "op", render: () => <Defensa /> },
  { num: "02", name: "Inteligencia", group: "op", star: true, render: () => <Inteligencia /> },
  { num: "03", name: "Posicionamiento", group: "op", render: () => <Posicionamiento /> },
  { num: "04", name: "Producción", group: "op", render: () => <Produccion /> },
  { num: "05", name: "Personalización", group: "addon", render: () => <Personalizacion /> },
];

export default function App() {
  const [active, setActive] = useState(2); // Inteligencia por defecto

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="sb-brand"><div className="sb-logo">C</div><div><h1>Comando IA</h1><div className="v">Consola · v0.1</div></div></div>
        <nav className="sb-nav">
          <div className="sb-group">Módulos operativos</div>
          {MODULES.filter((m) => m.group === "op").map((m, i) => {
            const idx = MODULES.indexOf(m);
            return (
              <button key={m.num} className={"sb-item" + (active === idx ? " active" : "")} onClick={() => setActive(idx)}>
                <span className="dot" style={{ background: active === idx ? "var(--brand)" : "transparent" }} />
                {m.name}{m.star ? " ★" : ""}<span className="num">{m.num}</span>
              </button>
            );
          })}
          <div className="sb-group" style={{ marginTop: 10 }}>Add-on</div>
          {MODULES.filter((m) => m.group === "addon").map((m) => {
            const idx = MODULES.indexOf(m);
            return (
              <button key={m.num} className={"sb-item" + (active === idx ? " active" : "")} onClick={() => setActive(idx)}>
                <span className="dot" style={{ background: active === idx ? "var(--brand)" : "transparent" }} />
                {m.name}<span className="num">{m.num}</span>
              </button>
            );
          })}
        </nav>
        <div className="sb-foot">Ventaja táctica<br />Intendencias PBA · 2027</div>
      </aside>

      <main className="main">
        {MODULES[active].render()}
      </main>
    </div>
  );
}
