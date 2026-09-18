import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import LinearProgress from "@mui/material/LinearProgress";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import Typography from "@mui/material/Typography";
import { useCallback, useEffect, useState } from "react";

import { Miembro } from "../api/casasClient";
import {
  DashboardCasa,
  ItemMantenimientoAlerta,
  TarjetaAlerta,
  esApiError,
  obtenerDashboard,
} from "../api/dashboardClient";

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

  // Spec `gastos-sin-reparto`: el mini-balance del dashboard muestra el
  // total gastado de la casa en ARS — mismo criterio de "solo ARS en el
  // mini-resumen" ya usado (`gastos-multi-moneda`), ahora aplicado al
  // nuevo contrato `{totales, aportes}` en vez de a la lista de balance
  // por miembro con su cifra de deuda. Vista rápida, no reemplaza a la
  // pantalla Balance completa (que sí muestra las secciones separadas
  // por moneda).
  const totalArs = dashboard.balance.totales.find((fila) => fila.moneda === "ARS");

  /** Spec `tarjetas-credito`, REQ-004: texto del banner de alerta — "vence
   * el {fecha} — quedan {dias} días" para una tarjeta próxima a vencer,
   * "ya venció hace {dias} días" si ya pasó la fecha (`vencida`). */
  function textoAlerta(tarjeta: TarjetaAlerta): string {
    const base = `${tarjeta.nombre} (${tarjeta.banco}) vence el ${tarjeta.fecha_vencimiento_actual}`;
    if (tarjeta.vencida) {
      return `${base} — ya venció hace ${Math.abs(tarjeta.dias_para_vencimiento)} días`;
    }
    return `${base} — quedan ${tarjeta.dias_para_vencimiento} días`;
  }

  /** Spec `mantenimiento-casa`, REQ-005: mismo criterio de texto que
   * `textoAlerta` arriba, aplicado a un ítem de mantenimiento en vez de
   * una tarjeta. Spec `mantenimiento-autos`, REQ-004: cuando el ítem
   * pertenece a un auto (`auto_nombre` presente), el nombre del auto se
   * menciona entre paréntesis junto al nombre del ítem — mismo banner
   * combinado, sin una sección separada (decisión explícita del usuario,
   * ver `00-overview.md`'s Tradeoffs), solo cambia el texto armado acá. */
  function textoAlertaMantenimiento(item: ItemMantenimientoAlerta): string {
    const nombreConAuto = item.auto_nombre ? `${item.nombre} (${item.auto_nombre})` : item.nombre;
    const base = `${nombreConAuto} — fecha estimada ${item.fecha_estimada}`;
    if (item.vencido) {
      return `${base} — ya venció hace ${Math.abs(item.dias_para_vencimiento)} días`;
    }
    return `${base} — quedan ${item.dias_para_vencimiento} días`;
  }

  return (
    <Box
      component="section"
      aria-label="Inicio de la casa"
      sx={{ display: "flex", flexDirection: "column", gap: 2 }}
    >
      {(dashboard.tarjetasConAlerta ?? []).length > 0 && (
        <Box
          component="section"
          aria-label="Alertas de vencimiento de tarjetas"
          sx={{ display: "flex", flexDirection: "column", gap: 1 }}
        >
          {dashboard.tarjetasConAlerta.map((tarjeta) => (
            <Alert key={tarjeta.id} severity={tarjeta.vencida ? "error" : "warning"}>
              {textoAlerta(tarjeta)}
            </Alert>
          ))}
        </Box>
      )}

      {(dashboard.mantenimientoConAlerta ?? []).length > 0 && (
        <Box
          component="section"
          aria-label="Alertas de mantenimiento"
          sx={{ display: "flex", flexDirection: "column", gap: 1 }}
        >
          {dashboard.mantenimientoConAlerta.map((item) => (
            <Alert key={item.id} severity={item.vencido ? "error" : "warning"}>
              {textoAlertaMantenimiento(item)}
            </Alert>
          ))}
        </Box>
      )}

      {dashboard.metaCasa != null && (
        <Card component="section" aria-label="Meta de la casa" variant="outlined">
          <CardContent>
            <Typography variant="h6" component="h3" gutterBottom>
              Meta de la casa
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {dashboard.metaCasa.puntos_acumulados} / {dashboard.metaCasa.meta} puntos
            </Typography>
            <LinearProgress
              variant="determinate"
              value={Math.min(dashboard.metaCasa.porcentaje, 100)}
            />
          </CardContent>
        </Card>
      )}

      <Box
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
          {!totalArs || Number(totalArs.total_gastos) === 0 ? (
            <Typography color="text.secondary">Todavía no hay balance para mostrar.</Typography>
          ) : (
            <Typography>Total gastado: ${totalArs.total_gastos}</Typography>
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
    </Box>
  );
}
