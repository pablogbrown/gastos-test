import { useCallback, useEffect, useState } from "react";

import { esApiError, obtenerRanking, RankingEntry } from "../api/tareasClient";

export interface RankingProps {
  casaId: string;
  usuarioId: string;
}

/** Pantalla "Ranking" (REQ-006): tabla de miembros ordenada por puntos
 * totales de mayor a menor, tal como la devuelve `calcular_ranking` — no
 * se reordena en el cliente para no divergir del criterio del servicio. */
export function Ranking({ casaId, usuarioId }: RankingProps) {
  const [ranking, setRanking] = useState<RankingEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);

  const cargar = useCallback(async () => {
    setCargando(true);
    try {
      setRanking(await obtenerRanking(casaId, usuarioId));
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo cargar el ranking.");
    } finally {
      setCargando(false);
    }
  }, [casaId, usuarioId]);

  useEffect(() => {
    void cargar();
  }, [cargar]);

  return (
    <section aria-label="Ranking">
      {error && <p role="alert">{error}</p>}
      {cargando ? (
        <p>Cargando ranking...</p>
      ) : (
        <table aria-label="Tabla de ranking">
          <thead>
            <tr>
              <th>Miembro</th>
              <th>Puntos</th>
            </tr>
          </thead>
          <tbody>
            {ranking.map((entrada) => (
              <tr key={entrada.miembroId}>
                <td>{entrada.miembroId}</td>
                <td>{entrada.puntos}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
