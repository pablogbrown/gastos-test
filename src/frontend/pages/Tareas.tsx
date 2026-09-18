import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import FormControl from "@mui/material/FormControl";
import FormControlLabel from "@mui/material/FormControlLabel";
import InputLabel from "@mui/material/InputLabel";
import Paper from "@mui/material/Paper";
import Select from "@mui/material/Select";
import Switch from "@mui/material/Switch";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { FormEvent, useCallback, useEffect, useState } from "react";

import { Miembro, Rol, listarMiembros } from "../api/casasClient";
import {
  completarTarea,
  crearTarea,
  EstadoTarea,
  esApiError,
  HistorialTarea,
  listarHistorial,
  listarTareas,
  Tarea,
} from "../api/tareasClient";

export interface TareasProps {
  casaId: string;
  /** Spec `resolver-rol-usuario-en-casa` (REQ-003): el `Miembro.id` propio
   * del Usuario autenticado EN ESTA CASA (resuelto en `App.tsx` cruzando
   * `usuario_id` contra el JWT propio) — usado solo para la lógica local
   * de "¿soy yo el responsable?" (`puedeCompletar`); las llamadas a la
   * API ya no lo necesitan, el actor se resuelve del JWT en el backend.
   * Renombrada desde `usuarioId` (el `Usuario.id` global): ese nombre
   * invitaba a comparar contra `tarea.responsableId` — un id de Miembro
   * por-casa — que nunca coincidía salvo casualidad. */
  miembroIdActual: string;
  rolUsuarioActual: Rol;
}

const FRECUENCIAS = ["diaria", "semanal", "quincenal"] as const;

const ESTADO_COLOR: Record<EstadoTarea, "default" | "warning" | "success"> = {
  pendiente: "warning",
  en_curso: "default",
  completada: "success",
};

/** Fix (reportado en vivo): una tarea recurrente no se puede completar
 * más seguido que su frecuencia — cada instancia nueva recién se puede
 * completar a partir de su propia `fechaPrevista` (hoy inclusive).
 * Comparación de strings "YYYY-MM-DD" (mismo formato que ya devuelve el
 * backend), válida para orden cronológico sin parsear a `Date`. */
function yaLlegoLaFechaPrevista(tarea: Tarea): boolean {
  if (!tarea.recurrente || !tarea.fechaPrevista) return true;
  const hoy = new Date().toISOString().slice(0, 10);
  return tarea.fechaPrevista <= hoy;
}

/** Visible solo para quien puede completar `tarea` (REQ-003, TC-004):
 * cualquiera si no tiene responsable, el propio responsable, o un
 * Administrador — y, si es recurrente, solo a partir de su fecha
 * prevista. Defensa en profundidad — la API vuelve a validar el mismo
 * criterio en `completar_tarea`. */
function puedeCompletar(tarea: Tarea, miembroIdActual: string, rol: Rol): boolean {
  if (tarea.estado === "completada") return false;
  if (!yaLlegoLaFechaPrevista(tarea)) return false;
  if (rol === "admin") return true;
  if (!tarea.responsableId) return true;
  return tarea.responsableId === miembroIdActual;
}

/** Pantallas "Tareas" e "Historial de tareas" (REQ-001 a REQ-004, REQ-007,
 * REQ-008): listado por estado, alta de tareas (incluye recurrencia) y
 * acción "Marcar completada". El responsable se elige de los miembros
 * activos de la casa (id real de Miembro, nunca texto libre). */
export function Tareas({ casaId, miembroIdActual, rolUsuarioActual }: TareasProps) {
  const [tareas, setTareas] = useState<Tarea[]>([]);
  const [historial, setHistorial] = useState<HistorialTarea[]>([]);
  const [miembros, setMiembros] = useState<Miembro[]>([]);
  const [nombre, setNombre] = useState("");
  const [puntos, setPuntos] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [responsableId, setResponsableId] = useState("");
  const [fechaPrevista, setFechaPrevista] = useState("");
  const [recurrente, setRecurrente] = useState(false);
  const [frecuencia, setFrecuencia] = useState<string>(FRECUENCIAS[0]);
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);

  const cargar = useCallback(async () => {
    setCargando(true);
    try {
      const [listaTareas, listaHistorial, listaMiembros] = await Promise.all([
        listarTareas(casaId),
        listarHistorial(casaId),
        listarMiembros(casaId),
      ]);
      setTareas(listaTareas);
      setHistorial(listaHistorial);
      setMiembros(listaMiembros);
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo cargar las tareas.");
    } finally {
      setCargando(false);
    }
  }, [casaId]);

  useEffect(() => {
    void cargar();
  }, [cargar]);

  async function handleCrear(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      await crearTarea(casaId, {
        nombre,
        puntos: puntos === "" ? undefined : Number(puntos),
        descripcion: descripcion || undefined,
        responsableId: responsableId || undefined,
        fechaPrevista: fechaPrevista || undefined,
        recurrente,
        frecuencia: recurrente ? frecuencia : undefined,
      });
      setNombre("");
      setPuntos("");
      setDescripcion("");
      setResponsableId("");
      setFechaPrevista("");
      setRecurrente(false);
      await cargar();
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo crear la tarea.");
    }
  }

  async function handleCompletar(tareaId: string) {
    setError(null);
    try {
      await completarTarea(casaId, tareaId);
      await cargar();
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo completar la tarea.");
    }
  }

  return (
    <Box component="section" aria-label="Tareas" sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      <Typography variant="h5" component="h2">
        Tareas
      </Typography>

      {error && <Alert severity="error">{error}</Alert>}

      <Paper variant="outlined" sx={{ p: 2 }}>
        <Box
          component="form"
          onSubmit={handleCrear}
          aria-label="Crear tarea"
          sx={{ display: "flex", flexDirection: "column", gap: 2 }}
        >
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 2 }}>
            <TextField
              id="nombre-tarea"
              label="Nombre"
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              size="small"
            />

            <TextField
              id="puntos-tarea"
              label="Puntos"
              type="number"
              value={puntos}
              onChange={(e) => setPuntos(e.target.value)}
              size="small"
            />

            <TextField
              id="descripcion-tarea"
              label="Descripción"
              value={descripcion}
              onChange={(e) => setDescripcion(e.target.value)}
              size="small"
            />

            <FormControl size="small" sx={{ minWidth: 200 }}>
              <InputLabel htmlFor="responsable-tarea" shrink>
                Responsable (opcional)
              </InputLabel>
              <Select
                native
                id="responsable-tarea"
                label="Responsable (opcional)"
                value={responsableId}
                onChange={(e) => setResponsableId(e.target.value)}
              >
                <option value="">Cualquiera</option>
                {miembros
                  .filter((m) => m.activo)
                  .map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.nombre}
                    </option>
                  ))}
              </Select>
            </FormControl>

            <TextField
              id="fecha-tarea"
              label={recurrente ? "Fecha prevista (obligatoria si es recurrente)" : "Fecha prevista"}
              type="date"
              value={fechaPrevista}
              onChange={(e) => setFechaPrevista(e.target.value)}
              size="small"
              slotProps={{ inputLabel: { shrink: true } }}
            />
          </Box>

          <FormControlLabel
            control={
              <Switch
                id="recurrente-tarea"
                checked={recurrente}
                onChange={(e) => setRecurrente(e.target.checked)}
              />
            }
            label="Recurrente"
          />

          {recurrente && (
            <FormControl size="small" sx={{ minWidth: 200 }}>
              <InputLabel htmlFor="frecuencia-tarea" shrink>
                Frecuencia
              </InputLabel>
              <Select
                native
                id="frecuencia-tarea"
                label="Frecuencia"
                value={frecuencia}
                onChange={(e) => setFrecuencia(e.target.value)}
              >
                {FRECUENCIAS.map((f) => (
                  <option key={f} value={f}>
                    {f}
                  </option>
                ))}
              </Select>
            </FormControl>
          )}

          <Box>
            <Button type="submit" variant="contained">
              Crear tarea
            </Button>
          </Box>
        </Box>
      </Paper>

      {cargando ? (
        <Typography>Cargando tareas...</Typography>
      ) : (
        <TableContainer component={Paper} variant="outlined">
          <Table aria-label="Listado de tareas" sx={{ minWidth: 320 }}>
            <TableHead>
              <TableRow>
                <TableCell>Nombre</TableCell>
                <TableCell>Puntos</TableCell>
                <TableCell>Estado</TableCell>
                <TableCell>Responsable</TableCell>
                <TableCell>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {tareas.map((tarea) => (
                <TableRow key={tarea.id}>
                  <TableCell>{tarea.nombre}</TableCell>
                  <TableCell>{tarea.puntos}</TableCell>
                  <TableCell>
                    <Chip label={tarea.estado} color={ESTADO_COLOR[tarea.estado]} size="small" />
                  </TableCell>
                  <TableCell>
                    {tarea.responsableId
                      ? miembros.find((m) => m.id === tarea.responsableId)?.nombre ?? tarea.responsableId
                      : "Cualquiera"}
                  </TableCell>
                  <TableCell>
                    {puedeCompletar(tarea, miembroIdActual, rolUsuarioActual) && (
                      <Button type="button" size="small" onClick={() => handleCompletar(tarea.id)}>
                        Marcar completada
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
        <Typography variant="h6" component="h3">
          Historial de tareas
        </Typography>
        <TableContainer component={Paper} variant="outlined">
          <Table aria-label="Historial de tareas" sx={{ minWidth: 320 }}>
            <TableHead>
              <TableRow>
                <TableCell>Fecha</TableCell>
                <TableCell>Miembro</TableCell>
                <TableCell>Tarea</TableCell>
                <TableCell>Puntos</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {historial.map((registro) => (
                <TableRow key={registro.id}>
                  <TableCell>{registro.completada_en}</TableCell>
                  <TableCell>
                    {miembros.find((m) => m.id === registro.miembro_id)?.nombre ??
                      registro.miembro_id}
                  </TableCell>
                  <TableCell>
                    {tareas.find((t) => t.id === registro.tarea_id)?.nombre ?? registro.tarea_id}
                  </TableCell>
                  <TableCell>{registro.puntos_obtenidos}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    </Box>
  );
}
