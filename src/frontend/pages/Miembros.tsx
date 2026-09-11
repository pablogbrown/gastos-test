import { FormEvent, useCallback, useEffect, useState } from "react";

import { agregarMiembro, desactivarMiembro, esApiError, listarMiembros, Miembro, Rol } from "../api/casasClient";
import { puedeGestionarMiembros } from "../api/permisos";

export interface MiembrosProps {
  casaId: string;
  usuarioId: string;
  rolUsuarioActual: Rol;
}

/** Pantalla "Miembros" (REQ-002, REQ-003, REQ-004): lista miembros
 * activos/inactivos, permite dar de alta y, solo si el usuario actual es
 * Administrador, desactivar un miembro. La ocultación de la acción es
 * defensa en profundidad — la API ya rechaza la operación por rol. */
export function Miembros({ casaId, usuarioId, rolUsuarioActual }: MiembrosProps) {
  const [miembros, setMiembros] = useState<Miembro[]>([]);
  const [nombre, setNombre] = useState("");
  const [identificacion, setIdentificacion] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);

  const puedeGestionar = puedeGestionarMiembros(rolUsuarioActual);

  const cargarMiembros = useCallback(async () => {
    setCargando(true);
    try {
      const lista = await listarMiembros(casaId, usuarioId);
      setMiembros(lista);
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo cargar la lista de miembros.");
    } finally {
      setCargando(false);
    }
  }, [casaId, usuarioId]);

  useEffect(() => {
    void cargarMiembros();
  }, [cargarMiembros]);

  async function handleAlta(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      await agregarMiembro(casaId, nombre, identificacion, usuarioId);
      setNombre("");
      setIdentificacion("");
      await cargarMiembros();
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo agregar el miembro.");
    }
  }

  async function handleDesactivar(miembroId: string) {
    setError(null);
    try {
      await desactivarMiembro(casaId, miembroId, usuarioId);
      await cargarMiembros();
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo desactivar el miembro.");
    }
  }

  return (
    <section aria-label="Miembros">
      {error && <p role="alert">{error}</p>}

      {puedeGestionar && (
        <form onSubmit={handleAlta} aria-label="Agregar miembro">
          <label htmlFor="nombre-miembro">Nombre</label>
          <input
            id="nombre-miembro"
            value={nombre}
            onChange={(event) => setNombre(event.target.value)}
          />
          <label htmlFor="identificacion-miembro">Identificación</label>
          <input
            id="identificacion-miembro"
            value={identificacion}
            onChange={(event) => setIdentificacion(event.target.value)}
          />
          <button type="submit">Agregar miembro</button>
        </form>
      )}

      {cargando ? (
        <p>Cargando miembros...</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Identificación</th>
              <th>Rol</th>
              <th>Estado</th>
              {puedeGestionar && <th>Acciones</th>}
            </tr>
          </thead>
          <tbody>
            {miembros.map((miembro) => (
              <tr key={miembro.id}>
                <td>{miembro.nombre}</td>
                <td>{miembro.identificacion}</td>
                <td>{miembro.rol}</td>
                <td>{miembro.activo ? "Activo" : "Inactivo"}</td>
                {puedeGestionar && (
                  <td>
                    {miembro.activo && (
                      <button type="button" onClick={() => handleDesactivar(miembro.id)}>
                        Desactivar
                      </button>
                    )}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
