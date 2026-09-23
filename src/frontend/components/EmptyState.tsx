import type { ReactNode } from "react";

import InboxIcon from "@mui/icons-material/Inbox";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";

/** Acción opcional de un `EmptyState` (ver `EmptyStateProps`). */
export interface EmptyStateAction {
  label: string;
  onClick: () => void;
}

export interface EmptyStateProps {
  icon?: ReactNode;
  message: string;
  action?: EmptyStateAction;
}

/** Estado vacío reutilizable (spec `sistema-visual`, REQ-002): ícono
 * centrado (uno genérico por defecto, sobreescribible por caso), un
 * mensaje y un botón de acción opcional (p.ej. "Agregar el primero") —
 * reemplaza una lista vacía sin ninguna indicación visual. Puramente
 * presentacional: no importa ningún cliente de `src/frontend/api/*`. */
export function EmptyState({ icon, message, action }: EmptyStateProps) {
  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        textAlign: "center",
        gap: 1,
        py: 3,
        color: "text.secondary",
      }}
    >
      <Box sx={{ fontSize: 40, display: "flex", color: "text.disabled" }}>
        {icon ?? <InboxIcon fontSize="inherit" />}
      </Box>
      <Typography color="text.secondary">{message}</Typography>
      {action && (
        <Button size="small" onClick={action.onClick} sx={{ mt: 1 }}>
          {action.label}
        </Button>
      )}
    </Box>
  );
}
