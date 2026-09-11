import { FormEvent, useState } from "react";

import { Casa, crearCasa, esApiError } from "../api/casasClient";

export interface CrearCasaProps {
  usuarioId: string;
  onCasaCreada: (casa: Casa) => void;
}

/** Formulario "Crear casa" (REQ-001). Al crearse, notifica al padre con la
 * casa nueva para que navegue a la pantalla de miembros (T4 no incluye un
 * router propio; la navegación queda a cargo de quien componga esta
 * pantalla). */
export function CrearCasa({ usuarioId, onCasaCreada }: CrearCasaProps) {
  const [nombre, setNombre] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setEnviando(true);
    try {
      const casa = await crearCasa(nombre, usuarioId);
      setNombre("");
      onCasaCreada(casa);
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo crear la casa.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} aria-label="Crear casa">
      <label htmlFor="nombre-casa">Nombre de la casa</label>
      <input
        id="nombre-casa"
        name="nombre"
        value={nombre}
        onChange={(event) => setNombre(event.target.value)}
        disabled={enviando}
      />
      <button type="submit" disabled={enviando}>
        Crear casa
      </button>
      {error && <p role="alert">{error}</p>}
    </form>
  );
}
