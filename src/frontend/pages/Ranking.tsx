import EmojiEventsIcon from "@mui/icons-material/EmojiEvents";
import LocalFireDepartmentIcon from "@mui/icons-material/LocalFireDepartment";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import LinearProgress from "@mui/material/LinearProgress";
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
import { AvatarConAccesorios } from "../components/AvatarConAccesorios";
import { PageHeader } from "../components/PageHeader";

// Spec `rediseno-ux-ui/pantallas-casa`, REQ-002: los 4 escalones fijos
// de `ranking_service.NIVELES` (backend) duplicados acá solo para
// calcular el % de avance visual hacia el próximo nivel — mismo
// criterio ya establecido para catálogos opacos del backend
// (`NOMBRES_LOGRO`, `FRONP-03`): la API sigue devolviendo únicamente
// `nivel` (nombre) y `puntos`, sin cambio de contrato.
const NIVELES = [
  { umbral: 0, nombre: "Novato" },
  { umbral: 50, nombre: "Activo" },
  { umbral: 150, nombre: "Comprometido" },
  { umbral: 300, nombre: "Campeón de la casa" },
];

function progresoNivel(nivelActual: string, puntos: number): { porcentaje: number; siguiente: string | null } {
  const indice = NIVELES.findIndex((n) => n.nombre === nivelActual);
  const actual = indice >= 0 ? NIVELES[indice] : NIVELES[0];
  const siguiente = indice >= 0 ? NIVELES[indice + 1] : NIVELES[1];
  if (!siguiente) return { porcentaje: 100, siguiente: null };
  const rango = siguiente.umbral - actual.umbral;
  const avance = Math.max(0, puntos - actual.umbral);
  const porcentaje = rango > 0 ? Math.min(100, Math.round((avance / rango) * 100)) : 100;
  return { porcentaje, siguiente: siguiente.nombre };
}

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
      <PageHeader title="Ranking" />

      <Box sx={{ display: "flex", justifyContent: "flex-end" }}>
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
                      <AvatarConAccesorios
                        casaId={casaId}
                        miembroId={entrada.miembroId}
                        nombre={nombreDe(entrada.miembroId)}
                        size={32}
                      />
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
                    <Box sx={{ display: "flex", flexDirection: "column", gap: 0.5, minWidth: 120 }}>
                      <Chip label={entrada.nivel} size="small" variant="outlined" />
                      <LinearProgress
                        variant="determinate"
                        value={progresoNivel(entrada.nivel, entrada.puntos).porcentaje}
                        aria-label={`Progreso de nivel de ${nombreDe(entrada.miembroId)}`}
                        sx={{ borderRadius: 4 }}
                      />
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                      <LocalFireDepartmentIcon
                        fontSize="small"
                        color={entrada.racha > 0 ? "warning" : "disabled"}
                      />
                      {entrada.racha > 0 ? `${entrada.racha} días` : "—"}
                    </Box>
                  </TableCell>
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
          <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}>
            {Object.entries(
              logros.reduce<Record<string, Logro[]>>((porMiembro, logro) => {
                (porMiembro[logro.miembro_id] ??= []).push(logro);
                return porMiembro;
              }, {})
            ).map(([miembroId, logrosDelMiembro]) => (
              <Box key={miembroId} sx={{ display: "flex", flexDirection: "column", gap: 0.5 }}>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {nombreDe(miembroId)}
                </Typography>
                <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
                  {logrosDelMiembro.map((logro) => (
                    <Chip
                      key={logro.id}
                      icon={<EmojiEventsIcon fontSize="small" />}
                      label={nombreLogro(logro.logro_id)}
                      title={logro.obtenido_en}
                      size="small"
                      variant="outlined"
                    />
                  ))}
                </Box>
              </Box>
            ))}
          </Box>
        )}
      </Box>
    </Box>
  );
}
