import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import Paper from "@mui/material/Paper";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { FormEvent, useCallback, useEffect, useState } from "react";

import {
  Tarjeta,
  crearTarjeta,
  eliminarTarjeta,
  esApiError,
  listarTarjetas,
  actualizarTarjeta,
} from "../api/tarjetasClient";

export interface TarjetasProps {
  casaId: string;
}

interface EdicionFila {
  fechaCierreActual: string;
  fechaVencimientoActual: string;
  saldoActualArs: string;
  saldoActualUsd: string;
}

function edicionInicial(tarjeta: Tarjeta): EdicionFila {
  return {
    fechaCierreActual: tarjeta.fecha_cierre_actual,
    fechaVencimientoActual: tarjeta.fecha_vencimiento_actual,
    saldoActualArs: tarjeta.saldo_actual_ars ?? "",
    saldoActualUsd: tarjeta.saldo_actual_usd ?? "",
  };
}

/** Pantalla "Tarjetas" (spec `tarjetas-credito`, REQ-001/REQ-002/REQ-003):
 * formulario de alta (banco, nombre, últimos 4 dígitos, cierre,
 * vencimiento) + listado con edición inline de cierre/vencimiento/saldo
 * y botón "Eliminar" — mismo patrón visual que `Suscripciones.tsx`. */
export function Tarjetas({ casaId }: TarjetasProps) {
  const [tarjetas, setTarjetas] = useState<Tarjeta[]>([]);
  const [banco, setBanco] = useState("");
  const [nombre, setNombre] = useState("");
  const [ultimosDigitos, setUltimosDigitos] = useState("");
  const [fechaCierre, setFechaCierre] = useState("");
  const [fechaVencimiento, setFechaVencimiento] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [ediciones, setEdiciones] = useState<Record<string, EdicionFila>>({});

  const cargar = useCallback(async () => {
    try {
      const lista = await listarTarjetas(casaId);
      setTarjetas(lista);
      setEdiciones(
        Object.fromEntries(lista.map((tarjeta) => [tarjeta.id, edicionInicial(tarjeta)]))
      );
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo cargar las tarjetas.");
    }
  }, [casaId]);

  useEffect(() => {
    void cargar();
  }, [cargar]);

  async function handleCrearTarjeta(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      await crearTarjeta(casaId, {
        banco,
        nombre,
        ultimosDigitos,
        fechaCierreActual: fechaCierre,
        fechaVencimientoActual: fechaVencimiento,
      });
      setBanco("");
      setNombre("");
      setUltimosDigitos("");
      setFechaCierre("");
      setFechaVencimiento("");
      await cargar();
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo registrar la tarjeta.");
    }
  }

  function actualizarCampoEdicion(
    tarjetaId: string,
    campo: keyof EdicionFila,
    valor: string
  ) {
    setEdiciones((actuales) => ({
      ...actuales,
      [tarjetaId]: { ...actuales[tarjetaId], [campo]: valor },
    }));
  }

  async function handleGuardarEdicion(tarjetaId: string) {
    setError(null);
    const edicion = ediciones[tarjetaId];
    try {
      await actualizarTarjeta(casaId, tarjetaId, {
        fechaCierreActual: edicion.fechaCierreActual,
        fechaVencimientoActual: edicion.fechaVencimientoActual,
        saldoActualArs: edicion.saldoActualArs || undefined,
        saldoActualUsd: edicion.saldoActualUsd || undefined,
      });
      await cargar();
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo actualizar la tarjeta.");
    }
  }

  async function handleEliminar(tarjetaId: string) {
    setError(null);
    try {
      await eliminarTarjeta(casaId, tarjetaId);
      await cargar();
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo eliminar la tarjeta.");
    }
  }

  return (
    <Box
      component="section"
      aria-label="Tarjetas"
      sx={{ display: "flex", flexDirection: "column", gap: 3 }}
    >
      <Typography variant="h5" component="h2">
        Tarjetas
      </Typography>

      {error && <Alert severity="error">{error}</Alert>}

      <Paper variant="outlined" sx={{ p: 2 }}>
        <Box
          component="form"
          onSubmit={handleCrearTarjeta}
          aria-label="Nueva tarjeta"
          sx={{ display: "flex", flexWrap: "wrap", gap: 2, alignItems: "flex-start" }}
        >
          <TextField
            id="banco-tarjeta"
            label="Banco"
            value={banco}
            onChange={(event) => setBanco(event.target.value)}
            size="small"
          />
          <TextField
            id="nombre-tarjeta"
            label="Nombre"
            value={nombre}
            onChange={(event) => setNombre(event.target.value)}
            size="small"
          />
          <TextField
            id="ultimos-digitos-tarjeta"
            label="Últimos 4 dígitos"
            value={ultimosDigitos}
            onChange={(event) => setUltimosDigitos(event.target.value)}
            size="small"
            slotProps={{ htmlInput: { maxLength: 4 } }}
          />
          <TextField
            id="fecha-cierre-tarjeta"
            label="Fecha de cierre"
            type="date"
            value={fechaCierre}
            onChange={(event) => setFechaCierre(event.target.value)}
            size="small"
            slotProps={{ inputLabel: { shrink: true } }}
          />
          <TextField
            id="fecha-vencimiento-tarjeta"
            label="Fecha de vencimiento"
            type="date"
            value={fechaVencimiento}
            onChange={(event) => setFechaVencimiento(event.target.value)}
            size="small"
            slotProps={{ inputLabel: { shrink: true } }}
          />
          <Button type="submit" variant="contained">
            Registrar tarjeta
          </Button>
        </Box>
      </Paper>

      <TableContainer component={Paper} variant="outlined">
        <Table aria-label="Listado de tarjetas" sx={{ minWidth: 320 }}>
          <TableHead>
            <TableRow>
              <TableCell>Nombre</TableCell>
              <TableCell>Banco</TableCell>
              <TableCell>Últimos dígitos</TableCell>
              <TableCell>Cierre</TableCell>
              <TableCell>Vencimiento</TableCell>
              <TableCell>Saldo ARS</TableCell>
              <TableCell>Saldo USD</TableCell>
              <TableCell>Estado</TableCell>
              <TableCell>Acciones</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tarjetas.map((tarjeta) => {
              const edicion = ediciones[tarjeta.id] ?? edicionInicial(tarjeta);
              return (
                <TableRow key={tarjeta.id}>
                  <TableCell>{tarjeta.nombre}</TableCell>
                  <TableCell>{tarjeta.banco}</TableCell>
                  <TableCell>•••• {tarjeta.ultimos_digitos}</TableCell>
                  <TableCell>
                    <TextField
                      type="date"
                      size="small"
                      value={edicion.fechaCierreActual}
                      onChange={(event) =>
                        actualizarCampoEdicion(tarjeta.id, "fechaCierreActual", event.target.value)
                      }
                      slotProps={{ inputLabel: { shrink: true } }}
                    />
                  </TableCell>
                  <TableCell>
                    <TextField
                      type="date"
                      size="small"
                      value={edicion.fechaVencimientoActual}
                      onChange={(event) =>
                        actualizarCampoEdicion(
                          tarjeta.id,
                          "fechaVencimientoActual",
                          event.target.value
                        )
                      }
                      slotProps={{ inputLabel: { shrink: true } }}
                    />
                  </TableCell>
                  <TableCell>
                    <TextField
                      size="small"
                      value={edicion.saldoActualArs}
                      onChange={(event) =>
                        actualizarCampoEdicion(tarjeta.id, "saldoActualArs", event.target.value)
                      }
                    />
                  </TableCell>
                  <TableCell>
                    <TextField
                      size="small"
                      value={edicion.saldoActualUsd}
                      onChange={(event) =>
                        actualizarCampoEdicion(tarjeta.id, "saldoActualUsd", event.target.value)
                      }
                    />
                  </TableCell>
                  <TableCell>
                    <Chip label="Activa" color="success" size="small" />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: "flex", gap: 1 }}>
                      <Button
                        type="button"
                        size="small"
                        onClick={() => handleGuardarEdicion(tarjeta.id)}
                      >
                        Guardar
                      </Button>
                      <Button
                        type="button"
                        size="small"
                        color="error"
                        onClick={() => handleEliminar(tarjeta.id)}
                      >
                        Eliminar
                      </Button>
                    </Box>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}
