import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import CardContent from "@mui/material/CardContent";
import CircularProgress from "@mui/material/CircularProgress";
import Container from "@mui/material/Container";
import Divider from "@mui/material/Divider";
import Typography from "@mui/material/Typography";
import { useCallback, useEffect, useState } from "react";

import { Casa, esApiError, listarCasasMias } from "../api/casasClient";
import { CrearCasa } from "./CrearCasa";

export interface SelectorCasasProps {
  onCasaElegida: (casa: Casa) => void;
}

/** Pantalla "Selector de casas" (REQ-004 de `usuarios-auth`; REQ-002 de
 * `rediseno-ux-ui/auth-onboarding`): lista las Casas donde el Usuario
 * autenticado tiene un Miembro activo (`GET /casas/mias`) y deja elegir
 * con cuál entrar al shell existente, o crear una nueva (reutiliza
 * `CrearCasa.tsx` en vez de duplicar su formulario). Cada casa se
 * muestra como una tarjeta (`Card` + `CardActionArea`) seleccionable —
 * mismo lenguaje visual de tarjeta que `Login.tsx`/`Registro.tsx`, en
 * vez de una lista de texto plano. */
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
      <Card sx={{ width: "100%" }}>
        <CardContent sx={{ p: { xs: 3, sm: 4 } }}>
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
            <Box
              aria-label="Casas"
              sx={{ display: "flex", flexDirection: "column", gap: 1.5, mb: 1 }}
            >
              {casas.map((casa) => (
                <Card key={casa.id} variant="outlined">
                  <CardActionArea onClick={() => onCasaElegida(casa)} sx={{ p: 2 }}>
                    <Typography component="span">{casa.nombre}</Typography>
                  </CardActionArea>
                </Card>
              ))}
            </Box>
          )}

          <Divider sx={{ my: 2 }} />

          <Button variant="outlined" fullWidth onClick={() => setCreandoCasa(true)}>
            Crear nueva casa
          </Button>
        </CardContent>
      </Card>
    </Container>
  );
}
