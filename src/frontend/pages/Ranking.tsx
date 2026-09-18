import EmojiEventsIcon from "@mui/icons-material/EmojiEvents";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Paper from "@mui/material/Paper";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useCallback, useEffect, useState } from "react";

import { Miembro } from "../api/casasClient";
import { esApiError, Logro, listarLogros, obtenerRanking, RankingEntry } from "../api/tareasClient";

export interface RankingProps {
  casaId: string;
  miembros: Miembro[];
}

const MEDALLAS = ["#FFD700", "#C0C0C0", "#CD7F32"];

// Spec `gamificacion-puntos`: mismo catálogo (`logro_service.
// LOGROS_CATALOGO`) duplicado acá solo para el nombre a mostrar — la API
// (`GET /casas/{id}/logros`) devuelve el `logro_id` crudo, no un nombre
// legible; el catálogo real (fijo en código, ver Tradeoffs de
// `00-overview.md`) vive del lado del backend.
const NOMBRES_LOGRO: Record<string, string> = {
  primera_tarea: "Primera tarea",
  diez_tareas: "10 tareas completadas",
  cincuenta_tareas: "50 tareas completadas",
  cien_puntos: "100 puntos",
  quinientos_puntos: "500 puntos",
  racha_siete: "Racha de 7 días",
  racha_treinta: "Racha de 30 días",
};

function nombreLogro(logroId: string): string {
  return NOMBRES_LOGRO[logroId] ?? logroId;
}

/** Pantalla "Ranking" (REQ-006): tabla de miembros ordenada por puntos
 * totales de mayor a menor, tal como la devuelve `calcular_ranking` — no
 * se reordena en el cliente para no divergir del criterio del servicio.
 * Spec `usuarios-auth`: el actor se resuelve del JWT en el backend — ya
 * no recibe `usuarioId` como prop. Spec
 * `fix-nombres-miembro-ranking-dashboard`: recibe `miembros` para
 * resolver el nombre del miembro por id — mismo patrón que
 * `Gastos.tsx`/`Balance.tsx`, con el id crudo como fallback.
 *
 * Spec `gamificacion-puntos` (REQ-001 a REQ-004): selector de mes (mismo
 * patrón que `Balance.tsx`, mes actual preseleccionado), nivel y racha
 * por fila, y una sub-sección "Logros" con los logros ya desbloqueados
 * de cada miembro. */
export function Ranking({ casaId, miembros }: RankingProps) {
  const [ranking, setRanking] = useState<RankingEntry[]>([]);
  const [logros, setLogros] = useState<Logro[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);
  const [mes, setMes] = useState<string>(() => new Date().toISOString().slice(0, 7));

  const cargar = useCallback(async () => {
    setCargando(true);
    try {
      const [listaRanking, listaLogros] = await Promise.all([
        obtenerRanking(casaId, mes),
        listarLogros(casaId),
      ]);
      setRanking(listaRanking);
      setLogros(listaLogros);
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo cargar el ranking.");
    } finally {
      setCargando(false);
    }
  }, [casaId, mes]);

  useEffect(() => {
    void cargar();
  }, [cargar]);

  function nombreDe(miembroId: string): string {
    return miembros.find((m) => m.id === miembroId)?.nombre ?? miembroId;
  }

  return (
    <Box component="section" aria-label="Ranking" sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 2 }}>
        <Typography variant="h5" component="h2">
          Ranking
        </Typography>

        <TextField
          id="mes-ranking"
          label="Mes"
          type="month"
          value={mes}
          onChange={(event) => setMes(event.target.value)}
          size="small"
          slotProps={{ inputLabel: { shrink: true } }}
        />
      </Box>

      {error && <Alert severity="error">{error}</Alert>}
      {cargando ? (
        <Typography>Cargando ranking...</Typography>
      ) : (
        <TableContainer component={Paper} variant="outlined">
          <Table aria-label="Tabla de ranking" sx={{ minWidth: 320 }}>
            <TableHead>
              <TableRow>
                <TableCell>Miembro</TableCell>
                <TableCell>Puntos</TableCell>
                <TableCell>Nivel</TableCell>
                <TableCell>Racha</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {ranking.map((entrada, indice) => (
                <TableRow key={entrada.miembroId}>
                  <TableCell>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                      {indice < 3 && (
                        <EmojiEventsIcon fontSize="small" sx={{ color: MEDALLAS[indice] }} />
                      )}
                      {nombreDe(entrada.miembroId)}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip label={entrada.puntos} size="small" color={indice === 0 ? "primary" : "default"} />
                  </TableCell>
                  <TableCell>
                    <Chip label={entrada.nivel} size="small" variant="outlined" />
                  </TableCell>
                  <TableCell>{entrada.racha > 0 ? `🔥 ${entrada.racha} días` : "—"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
        <Typography variant="h6" component="h3">
          Logros
        </Typography>
        {logros.length === 0 ? (
          <Typography color="text.secondary">Todavía no se desbloqueó ningún logro.</Typography>
        ) : (
          <TableContainer component={Paper} variant="outlined">
            <Table aria-label="Logros desbloqueados" sx={{ minWidth: 320 }}>
              <TableHead>
                <TableRow>
                  <TableCell>Miembro</TableCell>
                  <TableCell>Logro</TableCell>
                  <TableCell>Fecha</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {logros.map((logro) => (
                  <TableRow key={logro.id}>
                    <TableCell>{nombreDe(logro.miembro_id)}</TableCell>
                    <TableCell>{nombreLogro(logro.logro_id)}</TableCell>
                    <TableCell>{logro.obtenido_en}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Box>
    </Box>
  );
}
