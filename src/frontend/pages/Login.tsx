import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Container from "@mui/material/Container";
import Link from "@mui/material/Link";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { FormEvent, useState } from "react";

import { guardarSesion, login } from "../api/authClient";
import { esApiError } from "../api/httpError";

export interface LoginProps {
  onLoginExitoso: () => void;
  onIrARegistro: () => void;
}

/** Pantalla "Login" (spec `rediseno-ux-ui/auth-onboarding`, REQ-001;
 * REQ-003 de `usuarios-auth`): email + contraseña dentro de una tarjeta
 * (`Card`) centrada — el mismo lenguaje visual de tarjeta que
 * `Registro.tsx`/`SelectorCasas.tsx`/`CrearCasa.tsx`, y que reutiliza la
 * sombra/esquinas definidas una sola vez en `theme.ts` (spec
 * `sistema-visual`, REQ-001) en vez de un `Paper` con elevación por
 * defecto. Un login exitoso guarda el JWT (`guardarSesion`) y notifica a
 * `App.tsx`, que decide a dónde navegar (selector de casas o el shell) —
 * esta pantalla no conoce esa lógica. */
export function Login({ onLoginExitoso, onIrARegistro }: LoginProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setEnviando(true);
    try {
      const { access_token } = await login(email, password);
      guardarSesion(access_token);
      onLoginExitoso();
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo iniciar sesión.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <Container maxWidth="sm" sx={{ display: "flex", minHeight: "100vh", alignItems: "center" }}>
      <Card sx={{ width: "100%" }}>
        <CardContent sx={{ p: { xs: 3, sm: 4 } }}>
          <Typography variant="h5" component="h1" gutterBottom>
            taskia
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Iniciá sesión para ver tus casas.
          </Typography>
          <Box
            component="form"
            onSubmit={handleSubmit}
            aria-label="Iniciar sesión"
            sx={{ display: "flex", flexDirection: "column", gap: 2 }}
          >
            <TextField
              id="email-login"
              name="email"
              label="Email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              disabled={enviando}
              fullWidth
              autoFocus
            />
            <TextField
              id="password-login"
              name="password"
              label="Contraseña"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              disabled={enviando}
              fullWidth
            />
            <Button type="submit" variant="contained" disabled={enviando} size="large">
              Ingresar
            </Button>
            {error && <Alert severity="error">{error}</Alert>}
            <Typography variant="body2" color="text.secondary">
              ¿No tenés cuenta?{" "}
              <Link component="button" type="button" onClick={onIrARegistro}>
                Registrate
              </Link>
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Container>
  );
}
