import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
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

import { agregarMiembro, desactivarMiembro, esApiError, listarMiembros, Miembro, Rol } from "../api/casasClient";
import { puedeGestionarMiembros } from "../api/permisos";

export interface MiembrosProps {
  casaId: string;
  rolUsuarioActual: Rol;
}

/** Pantalla "Miembros" (REQ-002, REQ-003, REQ-004): lista miembros
 * activos/inactivos, permite dar de alta y, solo si el usuario actual es
 * Administrador, desactivar un miembro. La ocultación de la acción es
 * defensa en profundidad — la API ya rechaza la operación por rol.
 * Spec `usuarios-auth`: el actor se resuelve del JWT en el backend — ya
 * no recibe `usuarioId` como prop. */
export function Miembros({ casaId, rolUsuarioActual }: MiembrosProps) {
  const [miembros, setMiembros] = useState<Miembro[]>([]);
  const [nombre, setNombre] = useState("");
  const [identificacion, setIdentificacion] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);

  const puedeGestionar = puedeGestionarMiembros(rolUsuarioActual);

  const cargarMiembros = useCallback(async () => {
    setCargando(true);
    try {
      const lista = await listarMiembros(casaId);
      setMiembros(lista);
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo cargar la lista de miembros.");
    } finally {
      setCargando(false);
    }
  }, [casaId]);

  useEffect(() => {
    void cargarMiembros();
  }, [cargarMiembros]);

  async function handleAlta(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      await agregarMiembro(casaId, nombre, identificacion);
      setNombre("");
      setIdentificacion("");
      await cargarMiembros();
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo agregar el miembro.");
    }
  }

  async function handleDesactivar(miembroId: string) {
    setError(null);
    try {
      await desactivarMiembro(casaId, miembroId);
      await cargarMiembros();
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo desactivar el miembro.");
    }
  }

  return (
    <Box component="section" aria-label="Miembros" sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      <Typography variant="h5" component="h2">
        Miembros
      </Typography>

      {error && <Alert severity="error">{error}</Alert>}

      {puedeGestionar && (
        <Paper variant="outlined" sx={{ p: 2 }}>
          <Box
            component="form"
            onSubmit={handleAlta}
            aria-label="Agregar miembro"
            sx={{ display: "flex", flexWrap: "wrap", gap: 2, alignItems: "flex-start" }}
          >
            <TextField
              id="nombre-miembro"
              label="Nombre"
              value={nombre}
              onChange={(event) => setNombre(event.target.value)}
              size="small"
            />
            <TextField
              id="identificacion-miembro"
              label="Identificación"
              value={identificacion}
              onChange={(event) => setIdentificacion(event.target.value)}
              size="small"
            />
            <Button type="submit" variant="contained">
              Agregar miembro
            </Button>
          </Box>
        </Paper>
      )}

      {cargando ? (
        <Box sx={{ display: "flex", flexDirection: "row", alignItems: "center", gap: 1 }}>
          <CircularProgress size={20} />
          <Typography>Cargando miembros...</Typography>
        </Box>
      ) : (
        <TableContainer component={Paper} variant="outlined">
          <Table sx={{ minWidth: 320 }}>
            <TableHead>
              <TableRow>
                <TableCell>Nombre</TableCell>
                <TableCell>Identificación</TableCell>
                <TableCell>Rol</TableCell>
                <TableCell>Estado</TableCell>
                {puedeGestionar && <TableCell>Acciones</TableCell>}
              </TableRow>
            </TableHead>
            <TableBody>
              {miembros.map((miembro) => (
                <TableRow key={miembro.id}>
                  <TableCell>{miembro.nombre}</TableCell>
                  <TableCell>{miembro.identificacion}</TableCell>
                  <TableCell>{miembro.rol}</TableCell>
                  <TableCell>
                    <Chip
                      label={miembro.activo ? "Activo" : "Inactivo"}
                      color={miembro.activo ? "success" : "default"}
                      size="small"
                    />
                  </TableCell>
                  {puedeGestionar && (
                    <TableCell>
                      {miembro.activo && (
                        <Button
                          type="button"
                          size="small"
                          color="error"
                          onClick={() => handleDesactivar(miembro.id)}
                        >
                          Desactivar
                        </Button>
                      )}
                    </TableCell>
                  )}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}
