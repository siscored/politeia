import { useState } from "react";
import Resumen from "./modules/Resumen.jsx";
import Inteligencia from "./modules/Inteligencia.jsx";
import Placeholder from "./modules/Placeholder.jsx";

// Registro de módulos (estructura del mockup Comando IA). Cada uno es un
// componente propio; Inteligencia tiene el mapa real, el resto es hardcodeado.
const MODULES = [
  { num: "00", name: "Resumen", group: "op", render: () => <Resumen /> },
  { num: "01", name: "Defensa", group: "op", render: () => <Placeholder num="01" name="Defensa" desc="Escucha en tiempo real · alertas y simulación de impacto" detalle="Escucha activa y simulación de impacto sobre la estructura de voto" /> },
  { num: "02", name: "Inteligencia", group: "op", star: true, render: () => <Inteligencia /> },
  { num: "03", name: "Posicionamiento", group: "op", render: () => <Placeholder num="03" name="Posicionamiento" desc="Share of answer en motores de IA" detalle="Presencia del candidato en las respuestas de los motores de IA" /> },
  { num: "04", name: "Producción", group: "op", render: () => <Placeholder num="04" name="Producción" desc="Termómetro de piezas de contenido" detalle="Termómetro de contenidos: qué variante rinde y a qué velocidad" /> },
  { num: "05", name: "Personalización", group: "addon", render: () => <Placeholder num="05" name="Personalización" desc="CRM de reclamos de campo (consentido)" detalle="CRM de reclamos de campo — consentido, sin PII sensible" /> },
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
