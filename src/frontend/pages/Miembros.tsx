import Alert from "@mui/material/Alert";
import Avatar from "@mui/material/Avatar";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import Paper from "@mui/material/Paper";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { FormEvent, useCallback, useEffect, useState } from "react";

import {
  actualizarMetaPuntos,
  agregarMiembro,
  desactivarMiembro,
  esApiError,
  listarMiembros,
  Miembro,
  Rol,
} from "../api/casasClient";
import { puedeGestionarMiembros } from "../api/permisos";
import { PageHeader } from "../components/PageHeader";

// Spec `rediseno-ux-ui/pantallas-casa`, REQ-001: mapa centralizado
// id-de-rol -> etiqueta legible, mismo patrón ya establecido para
// catálogos opacos (`NOMBRES_LOGRO`, `FRONP-03`) — nunca hardcodeado
// inline por tarjeta.
const ETIQUETA_ROL: Record<Rol, string> = {
  admin: "Administrador",
  member: "Miembro",
};

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
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);
  // Spec `gamificacion-puntos`, REQ-005: campo "Meta de puntos mensual",
  // gateado por el mismo guard ya usado para alta/desactivación de
  // miembros.
  const [metaPuntos, setMetaPuntos] = useState("");
  const [metaExito, setMetaExito] = useState<string | null>(null);

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
      await agregarMiembro(casaId, nombre, identificacion, email);
      setNombre("");
      setIdentificacion("");
      setEmail("");
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

  async function handleGuardarMeta() {
    setError(null);
    setMetaExito(null);
    try {
      const meta = metaPuntos.trim() === "" ? null : Number(metaPuntos);
      await actualizarMetaPuntos(casaId, meta);
      setMetaExito("Meta actualizada.");
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo actualizar la meta de puntos.");
    }
  }

  return (
    <Box component="section" aria-label="Miembros" sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      <PageHeader title="Miembros" />

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
            <TextField
              id="email-miembro"
              label="Email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              size="small"
              helperText="Si la persona no está registrada, queda invitada hasta que se registre con este email"
            />
            <Button type="submit" variant="contained">
              Agregar miembro
            </Button>
          </Box>
        </Paper>
      )}

      {puedeGestionar && (
        <Paper variant="outlined" sx={{ p: 2 }}>
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 2, alignItems: "flex-start" }}>
            <TextField
              id="meta-puntos-mensual"
              label="Meta de puntos mensual"
              type="number"
              value={metaPuntos}
              onChange={(event) => setMetaPuntos(event.target.value)}
              size="small"
              helperText="Dejar vacío para desactivar la meta de la casa"
            />
            <Button type="button" variant="contained" onClick={handleGuardarMeta}>
              Guardar meta
            </Button>
            {metaExito && <Alert severity="success">{metaExito}</Alert>}
          </Box>
        </Paper>
      )}

      {cargando ? (
        <Box sx={{ display: "flex", flexDirection: "row", alignItems: "center", gap: 1 }}>
          <CircularProgress size={20} />
          <Typography>Cargando miembros...</Typography>
        </Box>
      ) : (
        <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}>
          {miembros.map((miembro) => (
            <Card
              key={miembro.id}
              variant="outlined"
              role="group"
              aria-label={`Miembro ${miembro.nombre}`}
            >
              <CardContent
                sx={{ display: "flex", alignItems: "center", gap: 2, flexWrap: "wrap" }}
              >
                <Avatar aria-label={`Avatar de ${miembro.nombre}`}>
                  {miembro.nombre.charAt(0).toUpperCase()}
                </Avatar>
                <Box sx={{ flexGrow: 1, minWidth: 160 }}>
                  <Typography variant="subtitle1">{miembro.nombre}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {miembro.identificacion}
                  </Typography>
                </Box>
                <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                  <Chip label={ETIQUETA_ROL[miembro.rol]} size="small" variant="outlined" />
                  {miembro.usuario_id == null ? (
                    <Chip label="Pendiente" color="warning" size="small" />
                  ) : (
                    <Chip
                      label={miembro.activo ? "Activo" : "Inactivo"}
                      color={miembro.activo ? "success" : "default"}
                      size="small"
                    />
                  )}
                </Box>
                {puedeGestionar && miembro.usuario_id != null && miembro.activo && (
                  <Button
                    type="button"
                    size="small"
                    color="error"
                    onClick={() => handleDesactivar(miembro.id)}
                  >
                    Desactivar
                  </Button>
                )}
              </CardContent>
            </Card>
          ))}
        </Box>
      )}
    </Box>
  );
}
