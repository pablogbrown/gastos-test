import { useCallback, useEffect, useState } from "react";

import { DashboardCasa, esApiError, obtenerDashboard } from "../api/dashboardClient";

export interface InicioCasaProps {
  casaId: string;
  usuarioId: string;
}

/** Pantalla "Inicio de la casa" (REQ-001): estado general de la casa de
 * un vistazo — miembros, gastos recientes, balance, tareas pendientes,
 * tareas completadas recientes y ranking. Cada sección se muestra vacía,
 * sin error, cuando la casa todavía no tiene gastos ni tareas (TC-002). */
export function InicioCasa({ casaId, usuarioId }: InicioCasaProps) {
  const [dashboard, setDashboard] = useState<DashboardCasa | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);

  const cargar = useCallback(async () => {
    setCargando(true);
    try {
      setDashboard(await obtenerDashboard(casaId, usuarioId));
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo cargar el inicio de la casa.");
    } finally {
      setCargando(false);
    }
  }, [casaId, usuarioId]);

  useEffect(() => {
    void cargar();
  }, [cargar]);

  if (error) {
    return <p role="alert">{error}</p>;
  }

  if (cargando || !dashboard) {
    return <p>Cargando inicio...</p>;
  }

  return (
    <section aria-label="Inicio de la casa">
      <section aria-label="Miembros">
        <h3>Miembros</h3>
        {dashboard.miembros.length === 0 ? (
          <p>Todavía no hay miembros activos.</p>
        ) : (
          <ul>
            {dashboard.miembros.map((miembro) => (
              <li key={miembro.id}>{miembro.nombre}</li>
            ))}
          </ul>
        )}
      </section>

      <section aria-label="Gastos recientes">
        <h3>Gastos recientes</h3>
        {dashboard.gastosRecientes.length === 0 ? (
          <p>Todavía no hay gastos registrados.</p>
        ) : (
          <ul>
            {dashboard.gastosRecientes.map((gasto) => (
              <li key={gasto.id}>
                {gasto.descripcion} — ${gasto.importe}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-label="Balance">
        <h3>Balance</h3>
        {dashboard.balance.length === 0 ? (
          <p>Todavía no hay balance para mostrar.</p>
        ) : (
          <ul>
            {dashboard.balance.map((entrada) => (
              <li key={entrada.miembro_id}>
                {entrada.nombre}: {entrada.balance}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-label="Tareas pendientes">
        <h3>Tareas pendientes</h3>
        {dashboard.tareasPendientes.length === 0 ? (
          <p>No hay tareas pendientes.</p>
        ) : (
          <ul>
            {dashboard.tareasPendientes.map((tarea) => (
              <li key={tarea.id}>
                {tarea.nombre} ({tarea.puntos} pts)
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-label="Tareas completadas recientes">
        <h3>Tareas completadas recientes</h3>
        {dashboard.tareasCompletadasRecientes.length === 0 ? (
          <p>Todavía no se completó ninguna tarea.</p>
        ) : (
          <ul>
            {dashboard.tareasCompletadasRecientes.map((registro) => (
              <li key={registro.id}>
                {registro.miembro_id} completó una tarea (+{registro.puntos_obtenidos} pts)
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-label="Ranking">
        <h3>Ranking</h3>
        {dashboard.ranking.length === 0 ? (
          <p>Todavía no hay puntos acumulados.</p>
        ) : (
          <ol>
            {dashboard.ranking.map((entrada) => (
              <li key={entrada.miembroId}>
                {entrada.miembroId}: {entrada.puntos} pts
              </li>
            ))}
          </ol>
        )}
      </section>
    </section>
  );
}
