import { useCallback, useEffect, useState } from "react";

import { BalanceResponse, esApiError, obtenerBalance } from "../api/gastosClient";

export interface BalanceProps {
  casaId: string;
  usuarioId: string;
}

/** Pantalla "Balance" (REQ-005, REQ-006): cuánto pagó y le correspondía
 * pagar a cada miembro, más las transferencias sugeridas para saldar
 * cuentas. */
export function Balance({ casaId, usuarioId }: BalanceProps) {
  const [balance, setBalance] = useState<BalanceResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const cargar = useCallback(async () => {
    try {
      const data = await obtenerBalance(casaId, usuarioId);
      setBalance(data);
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo cargar el balance.");
    }
  }, [casaId, usuarioId]);

  useEffect(() => {
    void cargar();
  }, [cargar]);

  if (error) {
    return <p role="alert">{error}</p>;
  }

  if (!balance) {
    return <p>Cargando balance...</p>;
  }

  function nombreDe(miembroId: string): string {
    return balance?.balances.find((b) => b.miembro_id === miembroId)?.nombre ?? miembroId;
  }

  return (
    <section aria-label="Balance">
      <table>
        <thead>
          <tr>
            <th>Miembro</th>
            <th>Pagó</th>
            <th>Le correspondía</th>
            <th>Balance</th>
          </tr>
        </thead>
        <tbody>
          {balance.balances.map((miembro) => (
            <tr key={miembro.miembro_id}>
              <td>{miembro.nombre}</td>
              <td>{miembro.pago}</td>
              <td>{miembro.correspondia}</td>
              <td>{miembro.balance}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3>Transferencias sugeridas</h3>
      {balance.transferencias.length === 0 ? (
        <p>No hay transferencias pendientes.</p>
      ) : (
        <ul>
          {balance.transferencias.map((transferencia, indice) => (
            <li key={indice}>
              {nombreDe(transferencia.deudor_id)} debe transferir {transferencia.monto} a{" "}
              {nombreDe(transferencia.acreedor_id)}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
