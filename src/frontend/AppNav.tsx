import { useState, type SyntheticEvent } from "react";

import ActivityIcon from "@mui/icons-material/History";
import BalanceIcon from "@mui/icons-material/AccountBalanceWallet";
import CarIcon from "@mui/icons-material/DirectionsCar";
import CreditCardIcon from "@mui/icons-material/CreditCard";
import GastosIcon from "@mui/icons-material/Receipt";
import HandshakeIcon from "@mui/icons-material/Handshake";
import HomeIcon from "@mui/icons-material/Home";
import LogoutIcon from "@mui/icons-material/Logout";
import BuildIcon from "@mui/icons-material/Build";
import PeopleIcon from "@mui/icons-material/People";
import PetsIcon from "@mui/icons-material/Pets";
import RankingIcon from "@mui/icons-material/EmojiEvents";
import SuscripcionesIcon from "@mui/icons-material/Subscriptions";
import TareasIcon from "@mui/icons-material/Checklist";
import AppBar from "@mui/material/AppBar";
import BottomNavigation from "@mui/material/BottomNavigation";
import BottomNavigationAction from "@mui/material/BottomNavigationAction";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import IconButton from "@mui/material/IconButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import Paper from "@mui/material/Paper";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import useMediaQuery from "@mui/material/useMediaQuery";
import { alpha, useTheme, type Theme } from "@mui/material/styles";

export type Pantalla =
  | "inicio"
  | "miembros"
  | "gastos"
  | "balance"
  | "tareas"
  | "mantenimiento"
  | "mantenimientoAutos"
  | "ranking"
  | "actividad"
  | "suscripciones"
  | "tarjetas"
  | "prestamos"
  | "miAvatar";

/** Las 13 secciones de navegación (spec `ui-modernization`, REQ-002;
 * `gastos-suscripcion-mensual` agrega "Suscripciones"; `tarjetas-credito`
 * agrega "Tarjetas"; `prestamos-entre-miembros` agrega "Préstamos";
 * `mantenimiento-casa` agrega "Mantenimiento"; `mantenimiento-autos`
 * agrega "Mantenimiento Autos"; `perfil-avatar-ui` agrega "Mi Avatar",
 * REQ-003 — dentro del grupo "Casa" existente, nunca como ítem nuevo de
 * primer nivel), compartidas entre `BottomNavigation` (mobile) y
 * `AppBar`/`Tabs` (desktop) — mismo orden, mismos íconos, mismo estado
 * `pantalla`. */
export const SECCIONES: { value: Pantalla; label: string; icon: JSX.Element }[] = [
  { value: "inicio", label: "Inicio", icon: <HomeIcon /> },
  { value: "miembros", label: "Miembros", icon: <PeopleIcon /> },
  { value: "gastos", label: "Gastos", icon: <GastosIcon /> },
  { value: "balance", label: "Balance", icon: <BalanceIcon /> },
  { value: "tareas", label: "Tareas", icon: <TareasIcon /> },
  { value: "mantenimiento", label: "Mantenimiento", icon: <BuildIcon /> },
  { value: "mantenimientoAutos", label: "Mantenimiento Autos", icon: <CarIcon /> },
  { value: "ranking", label: "Ranking", icon: <RankingIcon /> },
  { value: "actividad", label: "Actividad", icon: <ActivityIcon /> },
  { value: "suscripciones", label: "Suscripciones", icon: <SuscripcionesIcon /> },
  { value: "tarjetas", label: "Tarjetas", icon: <CreditCardIcon /> },
  { value: "prestamos", label: "Préstamos", icon: <HandshakeIcon /> },
  { value: "miAvatar", label: "Mi Avatar", icon: <PetsIcon /> },
];

/** Agrupación del menú superior desktop (spec `nav-agrupada`, REQ-001/002):
 * una entrada `"suelta"` navega directo al hacer clic; una entrada
 * `"grupo"` abre un menú desplegable con sus pantallas. `SECCIONES`
 * arriba sigue siendo la única fuente para `BottomNavigation` (mobile,
 * REQ-004) — esta estructura es exclusiva de la barra superior desktop. */
export type GrupoDesktop =
  | { tipo: "suelta"; pantalla: Pantalla }
  | { tipo: "grupo"; label: string; pantallas: Pantalla[] };

/** Agrupación fija de las pantallas para el menú superior desktop (spec
 * `nav-agrupada`, REQ-001/REQ-002; `mantenimiento-casa` convierte
 * "Tareas" de suelta a grupo; `mantenimiento-autos` agrega
 * "Mantenimiento Autos" al mismo grupo; `perfil-avatar-ui` agrega "Mi
 * Avatar" al grupo "Casa", REQ-003 — el bottom nav mobile sigue
 * mostrando exactamente 4 ítems de primer nivel, sin reintroducir el
 * overflow ya corregido por `fix nav-mobile-agrupada`): "Inicio" suelta,
 * "Casa" agrupa Miembros/Ranking/Actividad/Mi Avatar, "Gastos" agrupa
 * Gastos/Balance/Tarjetas/Suscripciones/Préstamos, "Tareas" agrupa
 * Tareas/Mantenimiento/Mantenimiento Autos. */
export const GRUPOS_DESKTOP: GrupoDesktop[] = [
  { tipo: "suelta", pantalla: "inicio" },
  { tipo: "grupo", label: "Casa", pantallas: ["miembros", "ranking", "actividad", "miAvatar"] },
  {
    tipo: "grupo",
    label: "Gastos",
    pantallas: ["gastos", "balance", "tarjetas", "suscripciones", "prestamos"],
  },
  { tipo: "grupo", label: "Tareas", pantallas: ["tareas", "mantenimiento", "mantenimientoAutos"] },
];

function seccionPorValue(value: Pantalla) {
  const seccion = SECCIONES.find((candidata) => candidata.value === value);
  if (!seccion) {
    throw new Error(`Sección desconocida: ${value}`);
  }
  return seccion;
}

/** Prefijo de los valores sintéticos de `BottomNavigation` que representan
 * un grupo (nunca una pantalla real) — ver `valorNavMobile`/`onChange` del
 * `BottomNavigation` mobile más abajo (fix `nav-mobile-agrupada`). */
const PREFIJO_GRUPO = "grupo:";

/** Ícono por grupo para el bottom nav mobile (fix `nav-mobile-agrupada`,
 * REQ único: agrupar el bottom nav como ya hace `GRUPOS_DESKTOP`, en vez
 * de listar las 12 secciones sueltas). Reutiliza íconos ya importados —
 * ninguno nuevo. El menú superior desktop no necesita esto: sus botones
 * de grupo son texto sin ícono (`Button` sin `startIcon`). */
const ICONOS_GRUPO: Record<string, JSX.Element> = {
  Casa: <PeopleIcon />,
  Gastos: <GastosIcon />,
  Tareas: <TareasIcon />,
};

/** Estilo del ítem seleccionado del `BottomNavigation` mobile — idéntico
 * para una pantalla suelta o un grupo, hoisteado para no recrear el mismo
 * objeto en cada iteración del `.map()`. */
const SX_ITEM_SELECCIONADO = {
  "&.Mui-selected": {
    bgcolor: (t: Theme) => alpha(t.palette.primary.main, 0.12),
    borderRadius: 2,
    "& .MuiBottomNavigationAction-label": {
      fontWeight: 700,
    },
  },
};

/** Valor que identifica, para el `BottomNavigation` mobile, cuál de sus
 * botones (una pantalla suelta o un grupo) corresponde a `pantalla` —
 * mismo criterio "¿la pantalla activa pertenece a este grupo?" que ya usa
 * el botón de grupo desktop (`activo`), aplicado acá para que MUI resalte
 * el botón correcto vía su propio `value`/`Mui-selected`. */
function valorNavMobile(pantalla: Pantalla, grupos: GrupoDesktop[]): string {
  for (const entrada of grupos) {
    if (entrada.tipo === "suelta" && entrada.pantalla === pantalla) {
      return entrada.pantalla;
    }
    if (entrada.tipo === "grupo" && entrada.pantallas.includes(pantalla)) {
      return PREFIJO_GRUPO + entrada.label;
    }
  }
  return pantalla;
}

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
  const [menuAbierto, setMenuAbierto] = useState<{
    label: string;
    anchorEl: HTMLElement;
  } | null>(null);

  function abrirMenu(label: string, event: SyntheticEvent) {
    setMenuAbierto({ label, anchorEl: event.currentTarget as HTMLElement });
  }

  function cerrarMenu() {
    setMenuAbierto(null);
  }

  function elegirPantalla(value: Pantalla) {
    onChange(value);
    cerrarMenu();
  }

  if (esDesktop) {
    return (
      <AppBar position="static" component="nav" aria-label="Navegación">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ mr: 4 }}>
            taskia
          </Typography>
          <Box sx={{ display: "flex", flex: 1 }}>
            {GRUPOS_DESKTOP.map((entrada) => {
              if (entrada.tipo === "suelta") {
                const seccion = seccionPorValue(entrada.pantalla);
                const activo = pantalla === entrada.pantalla;
                return (
                  <Button
                    key={entrada.pantalla}
                    onClick={() => onChange(entrada.pantalla)}
                    color="inherit"
                    startIcon={seccion.icon}
                    aria-current={activo ? "true" : undefined}
                    sx={{
                      opacity: activo ? 1 : 0.75,
                      fontWeight: activo ? 700 : 400,
                      borderRadius: 999,
                      bgcolor: activo ? alpha("#ffffff", 0.18) : "transparent",
                    }}
                  >
                    {seccion.label}
                  </Button>
                );
              }

              const activo = entrada.pantallas.includes(pantalla);
              const abierto = menuAbierto?.label === entrada.label;
              const buttonId = `nav-grupo-${entrada.label}`;
              return (
                <Box key={entrada.label} sx={{ display: "inline-flex" }}>
                  <Button
                    id={buttonId}
                    aria-haspopup="menu"
                    aria-expanded={abierto ? "true" : undefined}
                    aria-current={activo ? "true" : undefined}
                    onClick={(event) => abrirMenu(entrada.label, event)}
                    color="inherit"
                    sx={{
                      opacity: activo ? 1 : 0.75,
                      fontWeight: activo ? 700 : 400,
                      borderRadius: 999,
                      bgcolor: activo ? alpha("#ffffff", 0.18) : "transparent",
                    }}
                  >
                    {entrada.label}
                  </Button>
                  <Menu
                    anchorEl={abierto ? menuAbierto.anchorEl : null}
                    open={abierto}
                    onClose={cerrarMenu}
                    slotProps={{ list: { "aria-labelledby": buttonId } }}
                  >
                    {entrada.pantallas.map((value) => {
                      const seccion = seccionPorValue(value);
                      return (
                        <MenuItem key={value} onClick={() => elegirPantalla(value)}>
                          <ListItemIcon>{seccion.icon}</ListItemIcon>
                          <ListItemText>{seccion.label}</ListItemText>
                        </MenuItem>
                      );
                    })}
                  </Menu>
                </Box>
              );
            })}
          </Box>
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
          value={valorNavMobile(pantalla, GRUPOS_DESKTOP)}
          onChange={(event, value: string) => {
            if (value.startsWith(PREFIJO_GRUPO)) {
              abrirMenu(value.slice(PREFIJO_GRUPO.length), event);
            } else {
              onChange(value as Pantalla);
            }
          }}
          showLabels
        >
          {GRUPOS_DESKTOP.map((entrada) => {
            if (entrada.tipo === "suelta") {
              const seccion = seccionPorValue(entrada.pantalla);
              return (
                <BottomNavigationAction
                  key={entrada.pantalla}
                  value={entrada.pantalla}
                  label={seccion.label}
                  icon={seccion.icon}
                  aria-current={pantalla === entrada.pantalla ? "true" : undefined}
                  sx={SX_ITEM_SELECCIONADO}
                />
              );
            }

            const activo = entrada.pantallas.includes(pantalla);
            return (
              <BottomNavigationAction
                key={entrada.label}
                value={PREFIJO_GRUPO + entrada.label}
                label={entrada.label}
                icon={ICONOS_GRUPO[entrada.label]}
                aria-current={activo ? "true" : undefined}
                sx={SX_ITEM_SELECCIONADO}
              />
            );
          })}
        </BottomNavigation>
        {GRUPOS_DESKTOP.filter((entrada) => entrada.tipo === "grupo").map((entrada) => {
          if (entrada.tipo !== "grupo") {
            return null;
          }
          const abierto = menuAbierto?.label === entrada.label;
          return (
            <Menu
              key={entrada.label}
              anchorEl={abierto ? menuAbierto.anchorEl : null}
              open={abierto}
              onClose={cerrarMenu}
              slotProps={{ list: { "aria-label": entrada.label } }}
            >
              {entrada.pantallas.map((value) => {
                const seccion = seccionPorValue(value);
                return (
                  <MenuItem key={value} onClick={() => elegirPantalla(value)}>
                    <ListItemIcon>{seccion.icon}</ListItemIcon>
                    <ListItemText>{seccion.label}</ListItemText>
                  </MenuItem>
                );
              })}
            </Menu>
          );
        })}
      </Paper>
    </>
  );
}
