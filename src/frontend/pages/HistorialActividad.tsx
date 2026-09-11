import { useCallback, useEffect, useState } from "react";

import { Actividad, esApiError, obtenerActividad } from "../api/dashboardClient";

export interface HistorialActividadProps {
  casaId: string;
  usuarioId: string;
}

const ETIQUETAS_TIPO: Record<Actividad["tipo"], string> = {
  gasto_registrado: "Gasto",
  tarea_creada: "Tarea creada",
  tarea_completada: "Tarea completada",
  puntos_obtenidos: "Puntos",
  miembro_agregado: "Miembro agregado",
};

/** Pantalla "Historial de actividad" (REQ-002, REQ-003): lista
 * cronológica descendente de las acciones relevantes de la casa,
 * consultable por cualquier miembro (no requiere rol Administrador). */
export function HistorialActividad({ casaId, usuarioId }: HistorialActividadProps) {
  const [actividad, setActividad] = useState<Actividad[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);

  const cargar = useCallback(async () => {
    setCargando(true);
    try {
      setActividad(await obtenerActividad(casaId, usuarioId));
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo cargar el historial de actividad.");
    } finally {
      setCargando(false);
    }
  }, [casaId, usuarioId]);

  useEffect(() => {
    void cargar();
  }, [cargar]);

  return (
    <section aria-label="Historial de actividad">
      {error && <p role="alert">{error}</p>}
      {cargando ? (
        <p>Cargando historial...</p>
      ) : actividad.length === 0 ? (
        <p>Todavía no hay actividad registrada.</p>
      ) : (
        <ul>
          {actividad.map((entrada) => (
            <li key={entrada.id}>
              <strong>{ETIQUETAS_TIPO[entrada.tipo]}</strong> — {entrada.descripcion} (
              {entrada.fecha})
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
