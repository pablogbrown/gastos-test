import { useState } from "react";

import { Casa } from "./api/casasClient";
import { CrearCasa } from "./pages/CrearCasa";
import { Miembros } from "./pages/Miembros";

/** Composición mínima de las dos pantallas de esta spec. No hay dominio
 * `auth` todavía (fuera de alcance), así que `usuarioId` se genera al
 * cargar la página — una spec de auth futura lo reemplazará por la
 * identidad de sesión real sin tocar CrearCasa/Miembros. */
function usuarioIdDeSesion(): string {
  return crypto.randomUUID();
}

export function App() {
  const [usuarioId] = useState(usuarioIdDeSesion);
  const [casaActual, setCasaActual] = useState<Casa | null>(null);

  if (!casaActual) {
    return <CrearCasa usuarioId={usuarioId} onCasaCreada={setCasaActual} />;
  }

  return (
    <Miembros casaId={casaActual.id} usuarioId={usuarioId} rolUsuarioActual="admin" />
  );
}
