import AttachMoneyIcon from "@mui/icons-material/AttachMoney";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import PersonAddIcon from "@mui/icons-material/PersonAdd";
import PersonRemoveIcon from "@mui/icons-material/PersonRemove";
import StarIcon from "@mui/icons-material/Star";
import TaskAltIcon from "@mui/icons-material/TaskAlt";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import { useCallback, useEffect, useState } from "react";

import { Actividad, esApiError, obtenerActividad } from "../api/dashboardClient";
import { EmptyState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";

export interface HistorialActividadProps {
  casaId: string;
}

const ETIQUETAS_TIPO: Record<Actividad["tipo"], string> = {
  gasto_registrado: "Gasto",
  tarea_creada: "Tarea creada",
  tarea_completada: "Tarea completada",
  puntos_obtenidos: "Puntos",
  miembro_agregado: "Miembro agregado",
  miembro_desactivado: "Miembro desactivado",
};

const ICONOS_TIPO: Record<Actividad["tipo"], JSX.Element> = {
  gasto_registrado: <AttachMoneyIcon />,
  tarea_creada: <TaskAltIcon />,
  tarea_completada: <CheckCircleIcon />,
  puntos_obtenidos: <StarIcon />,
  miembro_agregado: <PersonAddIcon />,
  miembro_desactivado: <PersonRemoveIcon />,
};

/** Pantalla "Historial de actividad" (REQ-002, REQ-003): lista
 * cronológica descendente de las acciones relevantes de la casa,
 * consultable por cualquier miembro (no requiere rol Administrador).
 * Spec `usuarios-auth`: el actor se resuelve del JWT en el backend — ya
 * no recibe `usuarioId` como prop. */
export function HistorialActividad({ casaId }: HistorialActividadProps) {
  const [actividad, setActividad] = useState<Actividad[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);

  const cargar = useCallback(async () => {
    setCargando(true);
    try {
      setActividad(await obtenerActividad(casaId));
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo cargar el historial de actividad.");
    } finally {
      setCargando(false);
    }
  }, [casaId]);

  useEffect(() => {
    void cargar();
  }, [cargar]);

  return (
    <Box component="section" aria-label="Historial de actividad" sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
      <PageHeader title="Actividad" />

      {error && <Alert severity="error">{error}</Alert>}
      {cargando ? (
        <Typography>Cargando historial...</Typography>
      ) : actividad.length === 0 ? (
        <EmptyState message="Todavía no hay actividad registrada." />
      ) : (
        <List component={Paper} variant="outlined" sx={{ p: 0 }}>
          {actividad.map((entrada) => (
            <ListItem key={entrada.id} divider>
              <ListItemIcon>{ICONOS_TIPO[entrada.tipo]}</ListItemIcon>
              <ListItemText
                primary={`${ETIQUETAS_TIPO[entrada.tipo]} — ${entrada.descripcion} (${entrada.fecha})`}
              />
            </ListItem>
          ))}
        </List>
      )}
    </Box>
  );
}
