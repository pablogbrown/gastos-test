import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Container from "@mui/material/Container";
import Paper from "@mui/material/Paper";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { FormEvent, useState } from "react";

import { Casa, crearCasa, esApiError } from "../api/casasClient";

export interface CrearCasaProps {
  onCasaCreada: (casa: Casa) => void;
}

/** Formulario "Crear casa" (REQ-001). Al crearse, notifica al padre con la
 * casa nueva para que navegue a la pantalla de miembros (T4 no incluye un
 * router propio; la navegación queda a cargo de quien componga esta
 * pantalla). Spec `usuarios-auth`: el actor se resuelve del JWT en el
 * backend — ya no recibe `usuarioId` como prop. */
export function CrearCasa({ onCasaCreada }: CrearCasaProps) {
  const [nombre, setNombre] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setEnviando(true);
    try {
      const casa = await crearCasa(nombre);
      setNombre("");
      onCasaCreada(casa);
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo crear la casa.");
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
          Creá tu casa para empezar a compartir gastos y tareas.
        </Typography>
        <Box
          component="form"
          onSubmit={handleSubmit}
          aria-label="Crear casa"
          sx={{ display: "flex", flexDirection: "column", gap: 2 }}
        >
          <TextField
            id="nombre-casa"
            name="nombre"
            label="Nombre de la casa"
            value={nombre}
            onChange={(event) => setNombre(event.target.value)}
            disabled={enviando}
            fullWidth
            autoFocus
          />
          <Button type="submit" variant="contained" disabled={enviando} size="large">
            Crear casa
          </Button>
          {error && <Alert severity="error">{error}</Alert>}
        </Box>
      </Paper>
    </Container>
  );
}
