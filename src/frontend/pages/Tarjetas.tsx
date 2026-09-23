import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import Chip from "@mui/material/Chip";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { Fragment, FormEvent, useCallback, useEffect, useState } from "react";

import {
  Resumen,
  Tarjeta,
  crearTarjeta,
  eliminarTarjeta,
  esApiError,
  importarResumen,
  listarResumenes,
  listarTarjetas,
  pagarResumen,
  actualizarTarjeta,
} from "../api/tarjetasClient";
import { EmptyState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";

export interface TarjetasProps {
  casaId: string;
}

/** Enfoca el primer campo del formulario "Nueva tarjeta" ya renderizado
 * (spec `pantallas-financieras`, REQ-003/TC-005): el formulario nunca
 * estuvo oculto, "abrirlo" desde `PageHeader`/`EmptyState` es llevarle
 * el foco, sin cambiar su comportamiento de envío. */
function enfocarFormularioAlta() {
  document.getElementById("banco-tarjeta")?.focus();
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
  const [mensajeImportacion, setMensajeImportacion] = useState<string | null>(null);
  const [ediciones, setEdiciones] = useState<Record<string, EdicionFila>>({});
  // spec `resumen-tarjeta-pago`, T4: resúmenes importados por tarjeta.
  const [resumenesPorTarjeta, setResumenesPorTarjeta] = useState<Record<string, Resumen[]>>({});

  const cargar = useCallback(async () => {
    try {
      const lista = await listarTarjetas(casaId);
      setTarjetas(lista);
      setEdiciones(
        Object.fromEntries(lista.map((tarjeta) => [tarjeta.id, edicionInicial(tarjeta)]))
      );
      // Se recarga junto con la tarjeta (tras crear/editar/eliminar una
      // tarjeta, importar un resumen, o pagarlo) — un único punto de
      // refresco, mismo criterio que el resto de esta pantalla.
      const entradas = await Promise.all(
        lista.map(
          async (tarjeta) => [tarjeta.id, await listarResumenes(casaId, tarjeta.id)] as const
        )
      );
      setResumenesPorTarjeta(Object.fromEntries(entradas));
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

  /** Marca un resumen y todos sus gastos vinculados como pagados, en
   * una sola acción (spec `resumen-tarjeta-pago`, REQ-004). */
  async function handlePagarResumen(tarjetaId: string, resumenId: string) {
    setError(null);
    try {
      await pagarResumen(casaId, tarjetaId, resumenId);
      await cargar();
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo pagar el resumen.");
    }
  }

  /** REQ-007: sube el PDF de inmediato al seleccionarlo, sin ningún
   * diálogo de confirmación previo — importación 100% automática, mismo
   * criterio que el resto de las acciones de esta pantalla. */
  async function handleImportarResumen(tarjetaId: string, archivo: File) {
    setError(null);
    setMensajeImportacion(null);
    try {
      const resultado = await importarResumen(casaId, tarjetaId, archivo);
      setMensajeImportacion(
        `Resumen importado: ${resultado.gastos_creados} gastos creados ` +
          `(${resultado.cuotas_creadas} en cuotas, ` +
          `${resultado.suscripciones_vinculadas} vinculados a suscripciones).`
      );
      await cargar();
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo importar el resumen.");
    }
  }

  return (
    <Box
      component="section"
      aria-label="Tarjetas"
      sx={{ display: "flex", flexDirection: "column", gap: 3 }}
    >
      <PageHeader
        title="Tarjetas"
        action={{ label: "Nueva tarjeta", onClick: enfocarFormularioAlta }}
      />

      {error && <Alert severity="error">{error}</Alert>}
      {mensajeImportacion && <Alert severity="success">{mensajeImportacion}</Alert>}

      <Card variant="outlined" sx={{ p: 2 }}>
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
      </Card>

      {tarjetas.length === 0 ? (
        <EmptyState
          message="Todavía no registraste ninguna tarjeta"
          action={{ label: "Agregar la primera", onClick: enfocarFormularioAlta }}
        />
      ) : (
      <TableContainer component={Card} variant="outlined">
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
              const resumenes = resumenesPorTarjeta[tarjeta.id] ?? [];
              return (
                <Fragment key={tarjeta.id}>
                <TableRow>
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
                    <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
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
                      <Button type="button" size="small" component="label">
                        Importar resumen
                        <input
                          type="file"
                          accept="application/pdf"
                          hidden
                          aria-label={`Importar resumen ${tarjeta.nombre}`}
                          onChange={(event) => {
                            const archivo = event.target.files?.[0];
                            // Permite volver a seleccionar el mismo archivo
                            // más adelante (el evento `change` no dispara
                            // dos veces seguidas con el mismo valor).
                            event.target.value = "";
                            if (archivo) {
                              void handleImportarResumen(tarjeta.id, archivo);
                            }
                          }}
                        />
                      </Button>
                    </Box>
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell colSpan={9} sx={{ pt: 0, borderTop: "none" }}>
                    <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
                      <Typography variant="subtitle2">Resúmenes importados</Typography>
                      {resumenes.length === 0 && (
                        <Typography variant="body2" color="text.secondary">
                          Todavía no se importó ningún resumen.
                        </Typography>
                      )}
                      {resumenes.map((resumen) => (
                        <Box
                          key={resumen.id}
                          sx={{ display: "flex", alignItems: "center", gap: 1, flexWrap: "wrap" }}
                        >
                          <Typography variant="body2">{resumen.fecha_cierre}</Typography>
                          <Chip
                            label={resumen.estado === "pendiente" ? "Pendiente" : "Pagado"}
                            color={resumen.estado === "pendiente" ? "warning" : "success"}
                            size="small"
                          />
                          {resumen.estado === "pendiente" && (
                            <Button
                              type="button"
                              size="small"
                              onClick={() => handlePagarResumen(tarjeta.id, resumen.id)}
                            >
                              Pagar resumen
                            </Button>
                          )}
                        </Box>
                      ))}
                    </Box>
                  </TableCell>
                </TableRow>
                </Fragment>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
      )}
    </Box>
  );
}
