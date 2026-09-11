import { useCallback, useEffect, useState } from "react";

import { Casa, Miembro, listarMiembros } from "./api/casasClient";
import { Balance } from "./pages/Balance";
import { CrearCasa } from "./pages/CrearCasa";
import { Gastos } from "./pages/Gastos";
import { HistorialActividad } from "./pages/HistorialActividad";
import { InicioCasa } from "./pages/InicioCasa";
import { Miembros } from "./pages/Miembros";
import { Ranking } from "./pages/Ranking";
import { Tareas } from "./pages/Tareas";

type Pantalla =
  | "inicio"
  | "miembros"
  | "gastos"
  | "balance"
  | "tareas"
  | "ranking"
  | "actividad";

/** Composición de las pantallas de las cuatro sub-specs de
 * `gestion-domestica` (`casas-miembros`, `gastos`, `tareas-puntos` y
 * `dashboard-actividad`, esta última la que agrega "Inicio" y
 * "Actividad" y termina de cablear "Tareas"/"Ranking" a la navegación).
 * No hay dominio `auth` todavía (fuera de alcance), así que `usuarioId`
 * se genera al cargar la página — una spec de auth futura lo reemplazará
 * por la identidad de sesión real sin tocar las pantallas individuales. */
function usuarioIdDeSesion(): string {
  return crypto.randomUUID();
}

export function App() {
  const [usuarioId] = useState(usuarioIdDeSesion);
  const [casaActual, setCasaActual] = useState<Casa | null>(null);
  const [pantalla, setPantalla] = useState<Pantalla>("inicio");
  const [miembros, setMiembros] = useState<Miembro[]>([]);

  const cargarMiembros = useCallback(async () => {
    if (!casaActual) return;
    setMiembros(await listarMiembros(casaActual.id, usuarioId));
  }, [casaActual, usuarioId]);

  useEffect(() => {
    void cargarMiembros();
  }, [cargarMiembros]);

  if (!casaActual) {
    return <CrearCasa usuarioId={usuarioId} onCasaCreada={setCasaActual} />;
  }

  return (
    <div>
      <nav aria-label="Navegación">
        <button type="button" onClick={() => setPantalla("inicio")}>
          Inicio
        </button>
        <button type="button" onClick={() => setPantalla("miembros")}>
          Miembros
        </button>
        <button type="button" onClick={() => setPantalla("gastos")}>
          Gastos
        </button>
        <button type="button" onClick={() => setPantalla("balance")}>
          Balance
        </button>
        <button type="button" onClick={() => setPantalla("tareas")}>
          Tareas
        </button>
        <button type="button" onClick={() => setPantalla("ranking")}>
          Ranking
        </button>
        <button type="button" onClick={() => setPantalla("actividad")}>
          Actividad
        </button>
      </nav>

      {pantalla === "inicio" && <InicioCasa casaId={casaActual.id} usuarioId={usuarioId} />}
      {pantalla === "miembros" && (
        <Miembros casaId={casaActual.id} usuarioId={usuarioId} rolUsuarioActual="admin" />
      )}
      {pantalla === "gastos" && (
        <Gastos casaId={casaActual.id} usuarioId={usuarioId} miembros={miembros} />
      )}
      {pantalla === "balance" && <Balance casaId={casaActual.id} usuarioId={usuarioId} />}
      {pantalla === "tareas" && (
        <Tareas casaId={casaActual.id} usuarioId={usuarioId} rolUsuarioActual="admin" />
      )}
      {pantalla === "ranking" && <Ranking casaId={casaActual.id} usuarioId={usuarioId} />}
      {pantalla === "actividad" && (
        <HistorialActividad casaId={casaActual.id} usuarioId={usuarioId} />
      )}
    </div>
  );
}
