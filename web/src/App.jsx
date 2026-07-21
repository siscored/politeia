import { useState } from "react";
import Resumen from "./modules/Resumen.jsx";
import Defensa from "./modules/Defensa.jsx";
import Inteligencia from "./modules/Inteligencia.jsx";
import Posicionamiento from "./modules/Posicionamiento.jsx";
import Produccion from "./modules/Produccion.jsx";
import Personalizacion from "./modules/Personalizacion.jsx";

// Iconos SVG inline (estilo lucide, stroke = currentColor · sin dependencias).
const P = {
  activity: <path d="M22 12h-4l-3 9L9 3l-3 9H2" />,
  shield: <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />,
  map: <><path d="M3 6l6-3 6 3 6-3v15l-6 3-6-3-6 3z" /><path d="M9 3v15" /><path d="M15 6v15" /></>,
  target: <><circle cx="12" cy="12" r="9" /><circle cx="12" cy="12" r="5" /><circle cx="12" cy="12" r="1.4" /></>,
  layers: <><path d="M12 2 2 7l10 5 10-5-10-5z" /><path d="M2 12l10 5 10-5" /><path d="M2 17l10 5 10-5" /></>,
  people: <><circle cx="9" cy="7" r="3" /><path d="M3 21v-1a6 6 0 0 1 6-6 6 6 0 0 1 6 6v1" /><path d="M16 3.5a3 3 0 0 1 0 5.7" /><path d="M21 21v-1a6 6 0 0 0-4-5.6" /></>,
};
const Icon = ({ n }) => (
  <svg className="sb-ico" viewBox="0 0 24 24" width="18" height="18" fill="none"
    stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">{P[n]}</svg>
);

// Registro de módulos (estructura del mockup Comando IA). Cada uno es un
// componente propio; Inteligencia tiene el mapa real (Pilar/San Fernando),
// el resto replica el mockup con datos de ejemplo (Vicente López).
const MODULES = [
  { num: "00", name: "Resumen", group: "op", icon: "activity", render: () => <Resumen /> },
  { num: "01", name: "Defensa", group: "op", icon: "shield", render: () => <Defensa /> },
  { num: "02", name: "Inteligencia", group: "op", icon: "map", star: true, render: () => <Inteligencia /> },
  { num: "03", name: "Posicionamiento", group: "op", icon: "target", render: () => <Posicionamiento /> },
  { num: "04", name: "Producción", group: "op", icon: "layers", render: () => <Produccion /> },
  { num: "05", name: "Personalización", group: "addon", icon: "people", render: () => <Personalizacion /> },
];

export default function App() {
  const [active, setActive] = useState(2); // Inteligencia por defecto

  const Item = ({ m }) => {
    const idx = MODULES.indexOf(m);
    return (
      <button className={"sb-item" + (active === idx ? " active" : "")} onClick={() => setActive(idx)}>
        <Icon n={m.icon} />
        <span className="sb-label">{m.name}{m.star && <span className="sb-star">★</span>}</span>
        <span className="num">{m.num}</span>
      </button>
    );
  };

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="sb-brand">
          <div className="sb-logo">C</div>
          <div><h1>Comando IA</h1><div className="v">Consola · v0.1</div></div>
        </div>
        <nav className="sb-nav">
          <div className="sb-group">Módulos operativos</div>
          {MODULES.filter((m) => m.group === "op").map((m) => <Item key={m.num} m={m} />)}
          <div className="sb-group" style={{ marginTop: 14 }}>Add-on</div>
          {MODULES.filter((m) => m.group === "addon").map((m) => <Item key={m.num} m={m} />)}
        </nav>
        <div className="sb-foot">Ventaja táctica<br />Intendencias PBA · 2027</div>
      </aside>

      <main className="main">
        {MODULES[active].render()}
      </main>
    </div>
  );
}
