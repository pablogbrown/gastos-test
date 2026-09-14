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
import Typography from "@mui/material/Typography";
import { useCallback, useEffect, useState } from "react";

import { BalanceResponse, esApiError, obtenerBalance } from "../api/gastosClient";

export interface BalanceProps {
  casaId: string;
}

/** Pantalla "Balance" (REQ-005, REQ-006): cuánto pagó y le correspondía
 * pagar a cada miembro, más las transferencias sugeridas para saldar
 * cuentas. Spec `usuarios-auth`: el actor se resuelve del JWT en el
 * backend — ya no recibe `usuarioId` como prop. */
export function Balance({ casaId }: BalanceProps) {
  const [balance, setBalance] = useState<BalanceResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const cargar = useCallback(async () => {
    try {
      const data = await obtenerBalance(casaId);
      setBalance(data);
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo cargar el balance.");
    }
  }, [casaId]);

  useEffect(() => {
    void cargar();
  }, [cargar]);

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!balance) {
    return <Typography>Cargando balance...</Typography>;
  }

  function nombreDe(miembroId: string): string {
    return balance?.balances.find((b) => b.miembro_id === miembroId)?.nombre ?? miembroId;
  }

  return (
    <Box component="section" aria-label="Balance" sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      <Typography variant="h5" component="h2">
        Balance
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
            {balance.balances.map((miembro) => (
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
          <Typography variant="h6" component="h3" gutterBottom>
            Transferencias sugeridas
          </Typography>
          {balance.transferencias.length === 0 ? (
            <Typography color="text.secondary">No hay transferencias pendientes.</Typography>
          ) : (
            <List dense>
              {balance.transferencias.map((transferencia, indice) => (
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
}
