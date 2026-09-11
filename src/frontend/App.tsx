import { useCallback, useEffect, useState } from "react";

import { Casa, Miembro, listarMiembros } from "./api/casasClient";
import { Balance } from "./pages/Balance";
import { CrearCasa } from "./pages/CrearCasa";
import { Gastos } from "./pages/Gastos";
import { Miembros } from "./pages/Miembros";

type Pantalla = "miembros" | "gastos" | "balance";

/** Composición mínima de las pantallas de `casas-miembros` y `gastos`. No
 * hay dominio `auth` todavía (fuera de alcance), así que `usuarioId` se
 * genera al cargar la página — una spec de auth futura lo reemplazará
 * por la identidad de sesión real sin tocar las pantallas individuales. */
function usuarioIdDeSesion(): string {
  return crypto.randomUUID();
}

export function App() {
  const [usuarioId] = useState(usuarioIdDeSesion);
  const [casaActual, setCasaActual] = useState<Casa | null>(null);
  const [pantalla, setPantalla] = useState<Pantalla>("miembros");
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
        <button type="button" onClick={() => setPantalla("miembros")}>
          Miembros
        </button>
        <button type="button" onClick={() => setPantalla("gastos")}>
          Gastos
        </button>
        <button type="button" onClick={() => setPantalla("balance")}>
          Balance
        </button>
      </nav>

      {pantalla === "miembros" && (
        <Miembros casaId={casaActual.id} usuarioId={usuarioId} rolUsuarioActual="admin" />
      )}
      {pantalla === "gastos" && (
        <Gastos casaId={casaActual.id} usuarioId={usuarioId} miembros={miembros} />
      )}
      {pantalla === "balance" && <Balance casaId={casaActual.id} usuarioId={usuarioId} />}
    </div>
  );
}
