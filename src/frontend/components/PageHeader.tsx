import type { ReactNode } from "react";

import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";

/** Acción primaria opcional de un `PageHeader` (ver `PageHeaderProps`). */
export interface PageHeaderAction {
  label: string;
  onClick: () => void;
  icon?: ReactNode;
}

export interface PageHeaderProps {
  title: string;
  subtitle?: string;
  action?: PageHeaderAction;
}

/** Encabezado de pantalla reutilizable (spec `sistema-visual`, REQ-002):
 * título, subtítulo opcional y una acción primaria opcional alineada a
 * la derecha — el patrón que hoy cada pantalla reimplementa a mano.
 * Puramente presentacional (props in, JSX out): no importa ningún
 * cliente de `src/frontend/api/*`, así que `pantallas-financieras`,
 * `pantallas-casa` y `auth-onboarding` pueden reutilizarlo sin
 * acoplarse a un dominio. */
export function PageHeader({ title, subtitle, action }: PageHeaderProps) {
  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "flex-start",
        justifyContent: "space-between",
        gap: 2,
        mb: 2,
      }}
    >
      <Box>
        <Typography variant="h5" component="h1">
          {title}
        </Typography>
        {subtitle && (
          <Typography variant="body2" color="text.secondary">
            {subtitle}
          </Typography>
        )}
      </Box>
      {action && (
        <Button
          variant="contained"
          color="primary"
          startIcon={action.icon}
          onClick={action.onClick}
        >
          {action.label}
        </Button>
      )}
    </Box>
  );
}
