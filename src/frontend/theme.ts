import { createTheme } from "@mui/material/styles";

/** Tema MUI único de taskia (spec `ui-modernization`, REQ-003, REQ-004).
 * Paleta y tipografía consistentes en toda la app; los ítems de
 * `BottomNavigationAction` reciben una altura mínima de 44px vía
 * `components.MuiBottomNavigationAction.styleOverrides` para cumplir el
 * área táctil mínima de accesibilidad (REQ-004) sin depender de que cada
 * pantalla lo repita. */
export const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#3f51b5",
    },
    secondary: {
      main: "#00897b",
    },
    background: {
      default: "#f5f5f7",
    },
  },
  typography: {
    fontFamily: [
      "-apple-system",
      "BlinkMacSystemFont",
      '"Segoe UI"',
      "Roboto",
      "Helvetica",
      "Arial",
      "sans-serif",
    ].join(","),
  },
  components: {
    MuiBottomNavigationAction: {
      styleOverrides: {
        root: {
          minHeight: 44,
        },
      },
    },
    MuiBottomNavigation: {
      styleOverrides: {
        root: {
          minHeight: 56,
        },
      },
    },
  },
});
