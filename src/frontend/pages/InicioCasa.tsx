import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import Typography from "@mui/material/Typography";
import { useCallback, useEffect, useState } from "react";

import { Miembro } from "../api/casasClient";
import { DashboardCasa, esApiError, obtenerDashboard } from "../api/dashboardClient";

export interface InicioCasaProps {
  casaId: string;
  miembros: Miembro[];
}

/** Pantalla "Inicio de la casa" (REQ-001): estado general de la casa de
 * un vistazo — miembros, gastos recientes, balance, tareas pendientes,
 * tareas completadas recientes y ranking. Cada sección se muestra vacía,
 * sin error, cuando la casa todavía no tiene gastos ni tareas (TC-002).
 * Spec `usuarios-auth`: el actor se resuelve del JWT en el backend — ya
 * no recibe `usuarioId` como prop. Spec
 * `fix-nombres-miembro-ranking-dashboard`: recibe `miembros` para
 * resolver el nombre del miembro que completó cada tarea reciente —
 * mismo patrón que `Gastos.tsx`/`Balance.tsx`, con el id crudo como
 * fallback. */
export function InicioCasa({ casaId, miembros }: InicioCasaProps) {
  const [dashboard, setDashboard] = useState<DashboardCasa | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);

  const cargar = useCallback(async () => {
    setCargando(true);
    try {
      setDashboard(await obtenerDashboard(casaId));
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo cargar el inicio de la casa.");
    } finally {
      setCargando(false);
    }
  }, [casaId]);

  useEffect(() => {
    void cargar();
  }, [cargar]);

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (cargando || !dashboard) {
    return <Typography>Cargando inicio...</Typography>;
  }

  function nombreDe(miembroId: string): string {
    return miembros.find((m) => m.id === miembroId)?.nombre ?? miembroId;
  }

  return (
    <Box
      component="section"
      aria-label="Inicio de la casa"
      sx={{
        display: "grid",
        gridTemplateColumns: { xs: "1fr", sm: "1fr 1fr", md: "1fr 1fr 1fr" },
        gap: 2,
      }}
    >
      <Card component="section" aria-label="Miembros" variant="outlined">
        <CardContent>
          <Typography variant="h6" component="h3" gutterBottom>
            Miembros
          </Typography>
          {dashboard.miembros.length === 0 ? (
            <Typography color="text.secondary">Todavía no hay miembros activos.</Typography>
          ) : (
            <List dense>
              {dashboard.miembros.map((miembro) => (
                <ListItem key={miembro.id} disableGutters>
                  <ListItemText primary={miembro.nombre} />
                </ListItem>
              ))}
            </List>
          )}
        </CardContent>
      </Card>

      <Card component="section" aria-label="Gastos recientes" variant="outlined">
        <CardContent>
          <Typography variant="h6" component="h3" gutterBottom>
            Gastos recientes
          </Typography>
          {dashboard.gastosRecientes.length === 0 ? (
            <Typography color="text.secondary">Todavía no hay gastos registrados.</Typography>
          ) : (
            <List dense>
              {dashboard.gastosRecientes.map((gasto) => (
                <ListItem key={gasto.id} disableGutters>
                  <ListItemText primary={`${gasto.descripcion} — $${gasto.importe}`} />
                </ListItem>
              ))}
            </List>
          )}
        </CardContent>
      </Card>

      <Card component="section" aria-label="Balance" variant="outlined">
        <CardContent>
          <Typography variant="h6" component="h3" gutterBottom>
            Balance
          </Typography>
          {dashboard.balance.length === 0 ? (
            <Typography color="text.secondary">Todavía no hay balance para mostrar.</Typography>
          ) : (
            <List dense>
              {dashboard.balance.map((entrada) => (
                <ListItem key={entrada.miembro_id} disableGutters>
                  <ListItemText primary={`${entrada.nombre}: ${entrada.balance}`} />
                </ListItem>
              ))}
            </List>
          )}
        </CardContent>
      </Card>

      <Card component="section" aria-label="Tareas pendientes" variant="outlined">
        <CardContent>
          <Typography variant="h6" component="h3" gutterBottom>
            Tareas pendientes
          </Typography>
          {dashboard.tareasPendientes.length === 0 ? (
            <Typography color="text.secondary">No hay tareas pendientes.</Typography>
          ) : (
            <List dense>
              {dashboard.tareasPendientes.map((tarea) => (
                <ListItem key={tarea.id} disableGutters>
                  <ListItemText primary={`${tarea.nombre} (${tarea.puntos} pts)`} />
                </ListItem>
              ))}
            </List>
          )}
        </CardContent>
      </Card>

      <Card component="section" aria-label="Tareas completadas recientes" variant="outlined">
        <CardContent>
          <Typography variant="h6" component="h3" gutterBottom>
            Tareas completadas recientes
          </Typography>
          {dashboard.tareasCompletadasRecientes.length === 0 ? (
            <Typography color="text.secondary">Todavía no se completó ninguna tarea.</Typography>
          ) : (
            <List dense>
              {dashboard.tareasCompletadasRecientes.map((registro) => (
                <ListItem key={registro.id} disableGutters>
                  <ListItemText
                    primary={`${nombreDe(registro.miembro_id)} completó una tarea (+${registro.puntos_obtenidos} pts)`}
                  />
                </ListItem>
              ))}
            </List>
          )}
        </CardContent>
      </Card>

      <Card component="section" aria-label="Ranking" variant="outlined">
        <CardContent>
          <Typography variant="h6" component="h3" gutterBottom>
            Ranking
          </Typography>
          {dashboard.ranking.length === 0 ? (
            <Typography color="text.secondary">Todavía no hay puntos acumulados.</Typography>
          ) : (
            <List dense>
              {dashboard.ranking.map((entrada) => (
                <ListItem key={entrada.miembroId} disableGutters>
                  <ListItemText primary={`${nombreDe(entrada.miembroId)}: ${entrada.puntos} pts`} />
                </ListItem>
              ))}
            </List>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}
