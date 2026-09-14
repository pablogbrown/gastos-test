import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Container from "@mui/material/Container";
import Link from "@mui/material/Link";
import Paper from "@mui/material/Paper";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { FormEvent, useState } from "react";

import { registrar } from "../api/authClient";
import { esApiError } from "../api/httpError";

export interface RegistroProps {
  onRegistroExitoso: () => void;
  onIrALogin: () => void;
}

/** Pantalla "Registro" (REQ-002): nombre + email + contraseña. Un
 * registro exitoso vuelve a `Login` (TC-002) — no auto-loguea, para no
 * dejar ambiguo si la sesión iniciada corresponde a un login real. */
export function Registro({ onRegistroExitoso, onIrALogin }: RegistroProps) {
  const [nombre, setNombre] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setEnviando(true);
    try {
      await registrar(nombre, email, password);
      onRegistroExitoso();
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo crear la cuenta.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <Container maxWidth="sm" sx={{ display: "flex", minHeight: "100vh", alignItems: "center" }}>
      <Paper elevation={2} sx={{ p: { xs: 3, sm: 4 }, width: "100%" }}>
        <Typography variant="h5" component="h1" gutterBottom>
          taskia
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Creá tu cuenta para empezar a compartir gastos y tareas.
        </Typography>
        <Box
          component="form"
          onSubmit={handleSubmit}
          aria-label="Crear cuenta"
          sx={{ display: "flex", flexDirection: "column", gap: 2 }}
        >
          <TextField
            id="nombre-registro"
            name="nombre"
            label="Nombre"
            value={nombre}
            onChange={(event) => setNombre(event.target.value)}
            disabled={enviando}
            fullWidth
            autoFocus
          />
          <TextField
            id="email-registro"
            name="email"
            label="Email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            disabled={enviando}
            fullWidth
          />
          <TextField
            id="password-registro"
            name="password"
            label="Contraseña"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            disabled={enviando}
            fullWidth
          />
          <Button type="submit" variant="contained" disabled={enviando} size="large">
            Crear cuenta
          </Button>
          {error && <Alert severity="error">{error}</Alert>}
          <Typography variant="body2" color="text.secondary">
            ¿Ya tenés cuenta?{" "}
            <Link component="button" type="button" onClick={onIrALogin}>
              Iniciar sesión
            </Link>
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
}
