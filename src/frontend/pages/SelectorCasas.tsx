import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import Container from "@mui/material/Container";
import Divider from "@mui/material/Divider";
import List from "@mui/material/List";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import { useCallback, useEffect, useState } from "react";

import { Casa, esApiError, listarCasasMias } from "../api/casasClient";
import { CrearCasa } from "./CrearCasa";

export interface SelectorCasasProps {
  onCasaElegida: (casa: Casa) => void;
}

/** Pantalla "Selector de casas" (REQ-004): lista las Casas donde el
 * Usuario autenticado tiene un Miembro activo (`GET /casas/mias`) y deja
 * elegir con cuál entrar al shell existente, o crear una nueva
 * (reutiliza `CrearCasa.tsx` de `ui-modernization` en vez de duplicar su
 * formulario). */
export function SelectorCasas({ onCasaElegida }: SelectorCasasProps) {
  const [casas, setCasas] = useState<Casa[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [creandoCasa, setCreandoCasa] = useState(false);

  const cargar = useCallback(async () => {
    setCargando(true);
    try {
      setCasas(await listarCasasMias());
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudieron cargar tus casas.");
    } finally {
      setCargando(false);
    }
  }, []);

  useEffect(() => {
    void cargar();
  }, [cargar]);

  if (creandoCasa) {
    return <CrearCasa onCasaCreada={onCasaElegida} />;
  }

  return (
    <Container maxWidth="sm" sx={{ display: "flex", minHeight: "100vh", alignItems: "center" }}>
      <Paper elevation={2} sx={{ p: { xs: 3, sm: 4 }, width: "100%" }}>
        <Typography variant="h5" component="h1" gutterBottom>
          Tus casas
        </Typography>

        {error && <Alert severity="error">{error}</Alert>}

        {cargando ? (
          <CircularProgress size={28} />
        ) : casas.length === 0 ? (
          <Typography color="text.secondary" sx={{ mb: 2 }}>
            Todavía no pertenecés a ninguna casa.
          </Typography>
        ) : (
          <List aria-label="Casas">
            {casas.map((casa) => (
              <ListItemButton key={casa.id} onClick={() => onCasaElegida(casa)}>
                <ListItemText primary={casa.nombre} />
              </ListItemButton>
            ))}
          </List>
        )}

        <Divider sx={{ my: 2 }} />

        <Button variant="outlined" fullWidth onClick={() => setCreandoCasa(true)}>
          Crear nueva casa
        </Button>
      </Paper>
    </Container>
  );
}
