import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import Paper from "@mui/material/Paper";
import Select from "@mui/material/Select";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { FormEvent, useCallback, useEffect, useState } from "react";

import { Miembro } from "../api/casasClient";
import {
  Prestamo,
  actualizarEstadoPrestamo,
  crearPrestamo,
  esApiError,
  listarPrestamos,
} from "../api/prestamosClient";

export interface PrestamosProps {
  casaId: string;
  miembros: Miembro[];
}

type Moneda = "ARS" | "USD";

/** Pantalla "Préstamos" (spec `prestamos-entre-miembros`, REQ-001,
 * REQ-003, REQ-004): formulario de alta (prestamista, deudor, importe,
 * moneda, fecha, descripción opcional) + listado con chip de estado
 * clickeable — mismo patrón visual que el chip de estado de `Gastos.tsx`
 * (spec `gastos-estado-pago`): verde "Pagado" / naranja "Pendiente".
 * Completamente separada de Gastos y Balance — nunca los toca. */
export function Prestamos({ casaId, miembros }: PrestamosProps) {
  const [prestamos, setPrestamos] = useState<Prestamo[]>([]);
  const [prestamistaId, setPrestamistaId] = useState("");
  const [deudorId, setDeudorId] = useState("");
  const [importe, setImporte] = useState("");
  const [moneda, setMoneda] = useState<Moneda>("ARS");
  const [fecha, setFecha] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [error, setError] = useState<string | null>(null);

  const cargar = useCallback(async () => {
    try {
      setPrestamos(await listarPrestamos(casaId));
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo cargar los préstamos.");
    }
  }, [casaId]);

  useEffect(() => {
    void cargar();
  }, [cargar]);

  async function handleRegistrarPrestamo(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      // Mismo criterio que `moneda` en `Gastos.tsx`: nunca se fuerza
      // "ARS" explícito en el body cuando el usuario dejó el default.
      const monedaEnviada = moneda === "ARS" ? undefined : moneda;
      await crearPrestamo(casaId, {
        prestamistaId,
        deudorId,
        importe,
        moneda: monedaEnviada,
        fecha,
        descripcion,
      });
      setPrestamistaId("");
      setDeudorId("");
      setImporte("");
      setMoneda("ARS");
      setFecha("");
      setDescripcion("");
      await cargar();
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo registrar el préstamo.");
    }
  }

  /** Alterna el estado del préstamo clickeado al contrario del actual y
   * refresca el listado — mismo patrón que `Gastos.tsx`'s
   * `handleToggleEstado`. */
  async function handleToggleEstado(prestamo: Prestamo) {
    setError(null);
    try {
      const nuevoEstado = prestamo.estado === "pendiente" ? "pagado" : "pendiente";
      await actualizarEstadoPrestamo(casaId, prestamo.id, nuevoEstado);
      await cargar();
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo actualizar el estado del préstamo.");
    }
  }

  /** [FRON-01]: resuelve el nombre de un miembro por id con fallback
   * nullish al propio id, mismo helper que `Gastos.tsx`/`Balance.tsx`. */
  function nombreDe(miembroId: string): string {
    return miembros.find((miembro) => miembro.id === miembroId)?.nombre ?? miembroId;
  }

  function importeConPrefijo(prestamo: Prestamo): string {
    return `${prestamo.moneda === "USD" ? "US$" : "$"}${prestamo.importe}`;
  }

  return (
    <Box
      component="section"
      aria-label="Préstamos"
      sx={{ display: "flex", flexDirection: "column", gap: 3 }}
    >
      <Typography variant="h5" component="h2">
        Préstamos
      </Typography>

      {error && <Alert severity="error">{error}</Alert>}

      <Paper variant="outlined" sx={{ p: 2 }}>
        <Box
          component="form"
          onSubmit={handleRegistrarPrestamo}
          aria-label="Nuevo préstamo"
          sx={{ display: "flex", flexWrap: "wrap", gap: 2, alignItems: "flex-start" }}
        >
          <FormControl size="small" sx={{ minWidth: 180 }}>
            <InputLabel htmlFor="prestamista-prestamo" shrink>
              Prestamista
            </InputLabel>
            <Select
              native
              id="prestamista-prestamo"
              label="Prestamista"
              value={prestamistaId}
              onChange={(event) => setPrestamistaId(event.target.value)}
            >
              <option value="">Seleccionar miembro</option>
              {miembros.map((miembro) => (
                <option key={miembro.id} value={miembro.id}>
                  {miembro.nombre}
                </option>
              ))}
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 180 }}>
            <InputLabel htmlFor="deudor-prestamo" shrink>
              Deudor
            </InputLabel>
            <Select
              native
              id="deudor-prestamo"
              label="Deudor"
              value={deudorId}
              onChange={(event) => setDeudorId(event.target.value)}
            >
              <option value="">Seleccionar miembro</option>
              {miembros.map((miembro) => (
                <option key={miembro.id} value={miembro.id}>
                  {miembro.nombre}
                </option>
              ))}
            </Select>
          </FormControl>

          <TextField
            id="importe-prestamo"
            label="Importe"
            type="number"
            value={importe}
            onChange={(event) => setImporte(event.target.value)}
            size="small"
          />

          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel htmlFor="moneda-prestamo" shrink>
              Moneda
            </InputLabel>
            <Select
              native
              id="moneda-prestamo"
              label="Moneda"
              value={moneda}
              onChange={(event) => setMoneda(event.target.value as Moneda)}
            >
              <option value="ARS">ARS</option>
              <option value="USD">USD</option>
            </Select>
          </FormControl>

          <TextField
            id="fecha-prestamo"
            label="Fecha"
            type="date"
            value={fecha}
            onChange={(event) => setFecha(event.target.value)}
            size="small"
            slotProps={{ inputLabel: { shrink: true } }}
          />

          <TextField
            id="descripcion-prestamo"
            label="Descripción (opcional)"
            value={descripcion}
            onChange={(event) => setDescripcion(event.target.value)}
            size="small"
          />

          <Box>
            <Button type="submit" variant="contained">
              Registrar préstamo
            </Button>
          </Box>
        </Box>
      </Paper>

      <TableContainer component={Paper} variant="outlined">
        <Table aria-label="Listado de préstamos" sx={{ minWidth: 320 }}>
          <TableHead>
            <TableRow>
              <TableCell>Fecha</TableCell>
              <TableCell>Prestamista</TableCell>
              <TableCell>Deudor</TableCell>
              <TableCell>Importe</TableCell>
              <TableCell>Descripción</TableCell>
              <TableCell>Estado</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {prestamos.map((prestamo) => (
              <TableRow key={prestamo.id}>
                <TableCell>{prestamo.fecha}</TableCell>
                <TableCell>{nombreDe(prestamo.prestamista_id)}</TableCell>
                <TableCell>{nombreDe(prestamo.deudor_id)}</TableCell>
                <TableCell>{importeConPrefijo(prestamo)}</TableCell>
                <TableCell>{prestamo.descripcion ?? ""}</TableCell>
                <TableCell>
                  <Chip
                    label={prestamo.estado === "pagado" ? "Pagado" : "Pendiente"}
                    color={prestamo.estado === "pagado" ? "success" : "warning"}
                    size="small"
                    onClick={() => void handleToggleEstado(prestamo)}
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}
