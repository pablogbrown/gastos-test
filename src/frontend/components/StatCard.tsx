import type { ReactNode } from "react";

import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";

import { monetaryValueSx } from "../theme";

export type StatCardColor = "default" | "success" | "warning" | "error";

export interface StatCardProps {
  icon?: ReactNode;
  label: string;
  value: string;
  color?: StatCardColor;
}

/** Tarjeta compacta de estadística (spec `sistema-visual`, REQ-002):
 * ícono opcional, valor destacado (mayor peso/tamaño que la etiqueta) y
 * etiqueta — reutiliza el `Card` ya restyled por T1 (esquinas/sombra
 * definidas una sola vez en `theme.ts`). Puramente presentacional: no
 * importa ningún cliente de `src/frontend/api/*`. */
export function StatCard({ icon, label, value, color = "default" }: StatCardProps) {
  const valueColor = color === "default" ? "text.primary" : `${color}.main`;

  return (
    <Card variant="outlined">
      <CardContent sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
        {icon && (
          <Box sx={{ color: valueColor, display: "flex", fontSize: 28 }}>{icon}</Box>
        )}
        <Box>
          <Typography
            variant="h6"
            component="p"
            sx={{ fontWeight: 700, color: valueColor, ...monetaryValueSx }}
          >
            {value}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {label}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}
