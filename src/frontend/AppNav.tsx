import ActivityIcon from "@mui/icons-material/History";
import BalanceIcon from "@mui/icons-material/AccountBalanceWallet";
import GastosIcon from "@mui/icons-material/Receipt";
import HomeIcon from "@mui/icons-material/Home";
import LogoutIcon from "@mui/icons-material/Logout";
import PeopleIcon from "@mui/icons-material/People";
import RankingIcon from "@mui/icons-material/EmojiEvents";
import TareasIcon from "@mui/icons-material/Checklist";
import AppBar from "@mui/material/AppBar";
import BottomNavigation from "@mui/material/BottomNavigation";
import BottomNavigationAction from "@mui/material/BottomNavigationAction";
import IconButton from "@mui/material/IconButton";
import Paper from "@mui/material/Paper";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import useMediaQuery from "@mui/material/useMediaQuery";
import { useTheme } from "@mui/material/styles";

export type Pantalla =
  | "inicio"
  | "miembros"
  | "gastos"
  | "balance"
  | "tareas"
  | "ranking"
  | "actividad";

/** Las 7 secciones de navegación (spec `ui-modernization`, REQ-002),
 * compartidas entre `BottomNavigation` (mobile) y `AppBar`/`Tabs`
 * (desktop) — mismo orden, mismos íconos, mismo estado `pantalla`. */
export const SECCIONES: { value: Pantalla; label: string; icon: JSX.Element }[] = [
  { value: "inicio", label: "Inicio", icon: <HomeIcon /> },
  { value: "miembros", label: "Miembros", icon: <PeopleIcon /> },
  { value: "gastos", label: "Gastos", icon: <GastosIcon /> },
  { value: "balance", label: "Balance", icon: <BalanceIcon /> },
  { value: "tareas", label: "Tareas", icon: <TareasIcon /> },
  { value: "ranking", label: "Ranking", icon: <RankingIcon /> },
  { value: "actividad", label: "Actividad", icon: <ActivityIcon /> },
];

export interface AppNavProps {
  pantalla: Pantalla;
  onChange: (pantalla: Pantalla) => void;
  /** Spec `usuarios-auth`, REQ-005/TC-006: cuando se pasa, se muestra un
   * botón "Cerrar sesión" — omitido (como en los tests existentes de
   * `ui-modernization`) no cambia el markup anterior a esta spec. */
  onCerrarSesion?: () => void;
}

/** Navegación principal responsiva (spec `ui-modernization`, REQ-002):
 * `BottomNavigation` fija al pie en viewports angostos (< `sm`, 600px por
 * default de MUI), `AppBar` + `Tabs` en viewports anchos — mismas 7
 * secciones, mismo estado `pantalla` recibido por props para no acoplar
 * esta pieza a cómo `App` maneja la casa actual. Extraído como su propio
 * componente (en vez de vivir inline en `App`) para poder verificar
 * TC-001/TC-002/TC-004 sin pasar por el flujo de "crear casa". */
export function AppNav({ pantalla, onChange, onCerrarSesion }: AppNavProps) {
  const theme = useTheme();
  const esDesktop = useMediaQuery(theme.breakpoints.up("sm"));

  if (esDesktop) {
    return (
      <AppBar position="static" component="nav" aria-label="Navegación">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ mr: 4 }}>
            taskia
          </Typography>
          <Tabs
            value={pantalla}
            onChange={(_event, value: Pantalla) => onChange(value)}
            textColor="inherit"
            indicatorColor="secondary"
            variant="scrollable"
            scrollButtons="auto"
            aria-label="Navegación"
            sx={{ flex: 1 }}
          >
            {SECCIONES.map((seccion) => (
              <Tab
                key={seccion.value}
                value={seccion.value}
                label={seccion.label}
                icon={seccion.icon}
                iconPosition="start"
              />
            ))}
          </Tabs>
          {onCerrarSesion && (
            <IconButton
              color="inherit"
              aria-label="Cerrar sesión"
              onClick={onCerrarSesion}
            >
              <LogoutIcon />
            </IconButton>
          )}
        </Toolbar>
      </AppBar>
    );
  }

  return (
    <>
      {onCerrarSesion && (
        <IconButton
          aria-label="Cerrar sesión"
          onClick={onCerrarSesion}
          sx={{
            position: "fixed",
            top: 8,
            right: 8,
            zIndex: theme.zIndex.appBar + 1,
            bgcolor: "background.paper",
            boxShadow: 1,
          }}
        >
          <LogoutIcon />
        </IconButton>
      )}
      <Paper
        component="nav"
        aria-label="Navegación"
        elevation={3}
        sx={{ position: "fixed", bottom: 0, left: 0, right: 0 }}
      >
        <BottomNavigation
          value={pantalla}
          onChange={(_event, value: Pantalla) => onChange(value)}
          showLabels
        >
          {SECCIONES.map((seccion) => (
            <BottomNavigationAction
              key={seccion.value}
              value={seccion.value}
              label={seccion.label}
              icon={seccion.icon}
            />
          ))}
        </BottomNavigation>
      </Paper>
    </>
  );
}
