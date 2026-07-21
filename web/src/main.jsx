import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import "maplibre-gl/dist/maplibre-gl.css";
import "./tokens.css";
import "./styles.css";

// Sin StrictMode: MapLibre no se lleva bien con el doble-montaje de dev.
createRoot(document.getElementById("root")).render(<App />);
