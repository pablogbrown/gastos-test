import { esES } from "@mui/material/locale";
import { createTheme } from "@mui/material/styles";
import type { SxProps, Theme } from "@mui/material/styles";

/** Tema "Cálido minimal" de taskia (spec `rediseno-ux-ui/sistema-visual`,
 * REQ-001, D-01): reemplaza el índigo/teal genérico de MUI (y los
 * valores previos de `ui-modernization`) por una identidad propia — un
 * primario verde/teal profundo que evoca "hogar" sin perder seriedad
 * financiera, un acento secundario cálido (terracota) para CTAs
 * secundarios, fondo off-white cálido, tipografía con jerarquía
 * explícita, esquinas generosas (16px) y sombra suave de elevación en
 * las tarjetas. Los colores semánticos de estado (pagado/a_pagar/
 * pendiente/rechazado) reutilizan los slots estándar de MUI
 * (success/warning/info/error) en vez de definirse ad-hoc por pantalla.
 * Los ítems de `BottomNavigationAction` mantienen la altura mínima de
 * 44px (`ui-modernization`, REQ-004) sin cambios. `esES` (segundo
 * argumento) localiza los textos internos en inglés de componentes MUI
 * como `TablePagination` ("Next page", "Rows per page:") — toda la app
 * está en español, esto evita que un componente nuevo introduzca el
 * único texto en inglés de la pantalla. */
export const theme = createTheme(
  {
    palette: {
      mode: "light",
      primary: {
        main: "#1b6b5c",
      },
      secondary: {
        main: "#c1652f",
      },
      background: {
        default: "#faf6f1",
      },
      // Estados semánticos (pagado/a_pagar/pendiente/rechazado): se
      // reutilizan los 4 slots estándar de MUI en vez de colores ad-hoc
      // por pantalla — success (pagado), warning (a_pagar), info
      // (pendiente), error (rechazado).
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
      h1: { fontSize: "2.5rem", fontWeight: 700 },
      h2: { fontSize: "2rem", fontWeight: 700 },
      h3: { fontSize: "1.75rem", fontWeight: 600 },
      h4: { fontSize: "1.5rem", fontWeight: 600 },
      h5: { fontSize: "1.25rem", fontWeight: 600 },
      h6: { fontSize: "1.1rem", fontWeight: 600 },
      body1: { fontSize: "1rem", fontWeight: 400 },
      body2: { fontSize: "0.875rem", fontWeight: 400 },
      caption: { fontSize: "0.75rem", fontWeight: 400 },
    },
    shape: {
      borderRadius: 16,
    },
    components: {
      MuiCard: {
        styleOverrides: {
          root: {
            boxShadow: "0 2px 8px rgba(27, 42, 37, 0.12)",
          },
        },
      },
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
  },
  esES
);

/** Estilo compartido para valores monetarios (REQ-001): alinea los
 * dígitos en columnas vía `font-variant-numeric: tabular-nums`, definido
 * una sola vez acá en vez de que cada pantalla lo repita inline. Usado
 * por `StatCard` (spec `sistema-visual`, T2) y reutilizable por
 * cualquier pantalla que muestre un importe. */
export const monetaryValueSx: SxProps<Theme> = {
  fontVariantNumeric: "tabular-nums",
};
