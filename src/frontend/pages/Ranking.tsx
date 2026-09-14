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
import Typography from "@mui/material/Typography";
import { useCallback, useEffect, useState } from "react";

import { Miembro } from "../api/casasClient";
import { esApiError, obtenerRanking, RankingEntry } from "../api/tareasClient";

export interface RankingProps {
  casaId: string;
  miembros: Miembro[];
}

const MEDALLAS = ["#FFD700", "#C0C0C0", "#CD7F32"];

/** Pantalla "Ranking" (REQ-006): tabla de miembros ordenada por puntos
 * totales de mayor a menor, tal como la devuelve `calcular_ranking` — no
 * se reordena en el cliente para no divergir del criterio del servicio.
 * Spec `usuarios-auth`: el actor se resuelve del JWT en el backend — ya
 * no recibe `usuarioId` como prop. Spec
 * `fix-nombres-miembro-ranking-dashboard`: recibe `miembros` para
 * resolver el nombre del miembro por id — mismo patrón que
 * `Gastos.tsx`/`Balance.tsx`, con el id crudo como fallback. */
export function Ranking({ casaId, miembros }: RankingProps) {
  const [ranking, setRanking] = useState<RankingEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);

  const cargar = useCallback(async () => {
    setCargando(true);
    try {
      setRanking(await obtenerRanking(casaId));
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo cargar el ranking.");
    } finally {
      setCargando(false);
    }
  }, [casaId]);

  useEffect(() => {
    void cargar();
  }, [cargar]);

  function nombreDe(miembroId: string): string {
    return miembros.find((m) => m.id === miembroId)?.nombre ?? miembroId;
  }

  return (
    <Box component="section" aria-label="Ranking" sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      <Typography variant="h5" component="h2">
        Ranking
      </Typography>

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
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}
