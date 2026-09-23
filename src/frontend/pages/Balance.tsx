import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useCallback, useEffect, useState } from "react";

import { BalanceResponse, esApiError, obtenerBalance } from "../api/gastosClient";
import { EmptyState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";

export interface BalanceProps {
  casaId: string;
}

/** Spec `gastos-multi-moneda`/`gastos-sin-reparto`: "Pesos" se muestra
 * siempre (comportamiento actual); "Dólares" solo si hay actividad en
 * USD. Una fila sin `moneda` explícita se trata como "ARS" — mismo
 * default que el backend. */
const NOMBRE_SECCION: Record<string, string> = { ARS: "Pesos", USD: "Dólares" };

function nombreSeccion(moneda: string): string {
  return NOMBRE_SECCION[moneda] ?? moneda;
}

/** Pantalla "Balance" (spec `gastos-sin-reparto`, REQ-003/REQ-004): un
 * gasto ya no se reparte entre participantes ni genera ninguna deuda —
 * Balance muestra el total gastado por la casa en el mes (por moneda)
 * más, a modo informativo, cuánto aportó cada miembro. Sin ninguna
 * cifra de deuda ni transferencia sugerida. Spec `usuarios-auth`: el
 * actor se resuelve del JWT en el backend — ya no recibe `usuarioId`
 * como prop. */
export function Balance({ casaId }: BalanceProps) {
  const [balance, setBalance] = useState<BalanceResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  // Spec `balance-mensual` (REQ-004): mes preseleccionado = mes actual,
  // mismo formato `YYYY-MM` que espera el backend.
  const [mes, setMes] = useState<string>(() => new Date().toISOString().slice(0, 7));

  const cargar = useCallback(async () => {
    try {
      const data = await obtenerBalance(casaId, mes);
      setBalance(data);
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo cargar el balance.");
    }
  }, [casaId, mes]);

  useEffect(() => {
    void cargar();
  }, [cargar]);

  return (
    <Box component="section" aria-label="Balance" sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      {/* Sin `action`: Balance es de solo lectura, no tiene flujo de alta
       * propio (spec `pantallas-financieras`, T1). */}
      <PageHeader title="Balance" />

      <Box sx={{ display: "flex", justifyContent: "flex-end" }}>
        <TextField
          id="mes-balance"
          label="Mes"
          type="month"
          value={mes}
          onChange={(event) => setMes(event.target.value)}
          size="small"
          slotProps={{ inputLabel: { shrink: true } }}
        />
      </Box>

      {error && <Alert severity="error">{error}</Alert>}

      {!error && !balance && <Typography>Cargando balance...</Typography>}

      {!error && balance && (() => {
        // Spec `gastos-multi-moneda`/`gastos-sin-reparto`: una sección
        // independiente por moneda, cada una con su propio total y su
        // propia lista de aportes — nunca un total combinado. "Pesos"
        // (ARS) se muestra siempre, aunque no tenga actividad; "Dólares"
        // (o cualquier otra moneda) solo si tuvo actividad ese mes.
        const monedasConAportes = new Set(balance.aportes.map((fila) => fila.moneda));
        const monedas = [
          "ARS",
          ...Array.from(new Set([...balance.totales.map((f) => f.moneda), ...monedasConAportes]))
            .filter((moneda) => moneda !== "ARS")
            .sort(),
        ];

        return (
          <>
            {monedas.map((moneda) => {
              const total = balance.totales.find((fila) => fila.moneda === moneda);
              const aportes = balance.aportes.filter((fila) => fila.moneda === moneda);
              return (
                <Box
                  key={moneda}
                  component="section"
                  aria-label={`Balance en ${nombreSeccion(moneda)}`}
                  sx={{ display: "flex", flexDirection: "column", gap: 2 }}
                >
                  <Typography variant="h6" component="h3">
                    {nombreSeccion(moneda)}
                  </Typography>

                  {/* Nota (spec `pantallas-financieras`, T1, decisión registrada
                   * en decisions.yaml): no se usa `StatCard` acá — su layout
                   * separa `label`/`value` en dos nodos de texto distintos y
                   * rompería la query exacta ya existente
                   * `getByText("Total gastado: 500000")` (REQ-004/TC-006:
                   * cero regresión, queries sin modificar). Se preserva el
                   * texto combinado, solo restyled a `Card`. */}
                  <Card variant="outlined" sx={{ p: 2 }}>
                    <Typography variant="subtitle1" component="p">
                      Total gastado: {total?.total_gastos ?? "0"}
                    </Typography>
                  </Card>

                  <Card variant="outlined">
                    {aportes.length === 0 ? (
                      <EmptyState message="Todavía no hay aportes para mostrar." />
                    ) : (
                      <List dense>
                        {aportes.map((aporte) => (
                          <ListItem key={aporte.miembro_id} disableGutters sx={{ px: 2 }}>
                            <ListItemText primary={`${aporte.nombre} — Aportó $${aporte.total}`} />
                          </ListItem>
                        ))}
                      </List>
                    )}
                  </Card>
                </Box>
              );
            })}
          </>
        );
      })()}
    </Box>
  );
}
