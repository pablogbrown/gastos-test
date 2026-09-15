import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import Paper from "@mui/material/Paper";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useCallback, useEffect, useState } from "react";

import {
  BalancePorMiembro,
  BalanceResponse,
  esApiError,
  obtenerBalance,
  Transferencia,
} from "../api/gastosClient";

export interface BalanceProps {
  casaId: string;
}

/** Spec `gastos-multi-moneda`, REQ-002/TC-010: nombre de sección por
 * moneda — "Pesos" se muestra siempre (comportamiento actual); "Dólares"
 * solo si hay al menos una fila en USD. Una fila sin `moneda` explícita
 * (fixtures/backends viejos) se trata como "ARS" — mismo default que el
 * backend. */
const NOMBRE_SECCION: Record<string, string> = { ARS: "Pesos", USD: "Dólares" };

function nombreSeccion(moneda: string): string {
  return NOMBRE_SECCION[moneda] ?? moneda;
}

function agruparPorMoneda<T extends { moneda?: string }>(filas: T[]): Map<string, T[]> {
  const grupos = new Map<string, T[]>();
  for (const fila of filas) {
    const moneda = fila.moneda ?? "ARS";
    const grupo = grupos.get(moneda) ?? [];
    grupo.push(fila);
    grupos.set(moneda, grupo);
  }
  return grupos;
}

/** Pantalla "Balance" (REQ-005, REQ-006): cuánto pagó y le correspondía
 * pagar a cada miembro, más las transferencias sugeridas para saldar
 * cuentas. Spec `usuarios-auth`: el actor se resuelve del JWT en el
 * backend — ya no recibe `usuarioId` como prop. */
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

  function nombreDe(miembroId: string): string {
    return balance?.balances.find((b) => b.miembro_id === miembroId)?.nombre ?? miembroId;
  }

  return (
    <Box component="section" aria-label="Balance" sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 2 }}>
        <Typography variant="h5" component="h2">
          Balance
        </Typography>

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
        // Spec `gastos-multi-moneda` (REQ-002/TC-010): una sección
        // independiente por moneda, cada una con su propia tabla y sus
        // propias transferencias sugeridas — nunca un total combinado.
        // "Pesos" (ARS) se muestra siempre, aunque no tenga filas;
        // "Dólares" (o cualquier otra moneda) solo si tiene actividad.
        const gruposBalances = agruparPorMoneda<BalancePorMiembro>(balance.balances);
        const gruposTransferencias = agruparPorMoneda<Transferencia>(balance.transferencias);
        if (!gruposBalances.has("ARS")) {
          gruposBalances.set("ARS", []);
        }
        const monedas = [
          "ARS",
          ...Array.from(gruposBalances.keys())
            .filter((moneda) => moneda !== "ARS")
            .sort(),
        ];

        return (
          <>
            {monedas.map((moneda) => {
              const filasBalance = gruposBalances.get(moneda) ?? [];
              const filasTransferencias = gruposTransferencias.get(moneda) ?? [];
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

                  <TableContainer component={Paper} variant="outlined">
                    <Table sx={{ minWidth: 320 }}>
                      <TableHead>
                        <TableRow>
                          <TableCell>Miembro</TableCell>
                          <TableCell>Pagó</TableCell>
                          <TableCell>Le correspondía</TableCell>
                          <TableCell>Balance</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {filasBalance.map((miembro) => (
                          <TableRow key={miembro.miembro_id}>
                            <TableCell>{miembro.nombre}</TableCell>
                            <TableCell>{miembro.pago}</TableCell>
                            <TableCell>{miembro.correspondia}</TableCell>
                            <TableCell>{miembro.balance}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>

                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle1" component="h4" gutterBottom>
                        Transferencias sugeridas
                      </Typography>
                      {filasTransferencias.length === 0 ? (
                        <Typography color="text.secondary">
                          No hay transferencias pendientes.
                        </Typography>
                      ) : (
                        <List dense>
                          {filasTransferencias.map((transferencia, indice) => (
                            <ListItem key={indice} disableGutters>
                              <ListItemText
                                primary={`${nombreDe(transferencia.deudor_id)} debe transferir ${transferencia.monto} a ${nombreDe(transferencia.acreedor_id)}`}
                              />
                            </ListItem>
                          ))}
                        </List>
                      )}
                    </CardContent>
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
