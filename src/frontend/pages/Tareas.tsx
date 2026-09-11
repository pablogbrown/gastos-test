import { FormEvent, useCallback, useEffect, useState } from "react";

import { Rol } from "../api/casasClient";
import {
  completarTarea,
  crearTarea,
  esApiError,
  HistorialTarea,
  listarHistorial,
  listarTareas,
  Tarea,
} from "../api/tareasClient";

export interface TareasProps {
  casaId: string;
  usuarioId: string;
  rolUsuarioActual: Rol;
}

const FRECUENCIAS = ["diaria", "semanal", "quincenal"] as const;

/** Visible solo para quien puede completar `tarea` (REQ-003, TC-004):
 * cualquiera si no tiene responsable, el propio responsable, o un
 * Administrador. Defensa en profundidad — la API vuelve a validar el
 * mismo criterio en `completar_tarea`. */
function puedeCompletar(tarea: Tarea, usuarioId: string, rol: Rol): boolean {
  if (tarea.estado === "completada") return false;
  if (rol === "admin") return true;
  if (!tarea.responsableId) return true;
  return tarea.responsableId === usuarioId;
}

/** Pantallas "Tareas" e "Historial de tareas" (REQ-001 a REQ-004, REQ-007,
 * REQ-008): listado por estado, alta de tareas (incluye recurrencia) y
 * acción "Marcar completada". El responsable se ingresa por id de miembro
 * (texto libre) — un selector con nombres reales queda para la spec
 * `dashboard-actividad`, que integra esta pantalla en la navegación. */
export function Tareas({ casaId, usuarioId, rolUsuarioActual }: TareasProps) {
  const [tareas, setTareas] = useState<Tarea[]>([]);
  const [historial, setHistorial] = useState<HistorialTarea[]>([]);
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
      const [listaTareas, listaHistorial] = await Promise.all([
        listarTareas(casaId, usuarioId),
        listarHistorial(casaId, usuarioId),
      ]);
      setTareas(listaTareas);
      setHistorial(listaHistorial);
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo cargar las tareas.");
    } finally {
      setCargando(false);
    }
  }, [casaId, usuarioId]);

  useEffect(() => {
    void cargar();
  }, [cargar]);

  async function handleCrear(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      await crearTarea(casaId, usuarioId, {
        nombre,
        puntos: Number(puntos),
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
      await completarTarea(casaId, tareaId, usuarioId);
      await cargar();
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo completar la tarea.");
    }
  }

  return (
    <section aria-label="Tareas">
      {error && <p role="alert">{error}</p>}

      <form onSubmit={handleCrear} aria-label="Crear tarea">
        <label htmlFor="nombre-tarea">Nombre</label>
        <input id="nombre-tarea" value={nombre} onChange={(e) => setNombre(e.target.value)} />

        <label htmlFor="puntos-tarea">Puntos</label>
        <input
          id="puntos-tarea"
          type="number"
          value={puntos}
          onChange={(e) => setPuntos(e.target.value)}
        />

        <label htmlFor="descripcion-tarea">Descripción</label>
        <input
          id="descripcion-tarea"
          value={descripcion}
          onChange={(e) => setDescripcion(e.target.value)}
        />

        <label htmlFor="responsable-tarea">Responsable (opcional)</label>
        <input
          id="responsable-tarea"
          value={responsableId}
          onChange={(e) => setResponsableId(e.target.value)}
        />

        <label htmlFor="fecha-tarea">Fecha prevista</label>
        <input
          id="fecha-tarea"
          type="date"
          value={fechaPrevista}
          onChange={(e) => setFechaPrevista(e.target.value)}
        />

        <label htmlFor="recurrente-tarea">
          <input
            id="recurrente-tarea"
            type="checkbox"
            checked={recurrente}
            onChange={(e) => setRecurrente(e.target.checked)}
          />
          Recurrente
        </label>

        {recurrente && (
          <>
            <label htmlFor="frecuencia-tarea">Frecuencia</label>
            <select
              id="frecuencia-tarea"
              value={frecuencia}
              onChange={(e) => setFrecuencia(e.target.value)}
            >
              {FRECUENCIAS.map((f) => (
                <option key={f} value={f}>
                  {f}
                </option>
              ))}
            </select>
          </>
        )}

        <button type="submit">Crear tarea</button>
      </form>

      {cargando ? (
        <p>Cargando tareas...</p>
      ) : (
        <table aria-label="Listado de tareas">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Puntos</th>
              <th>Estado</th>
              <th>Responsable</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {tareas.map((tarea) => (
              <tr key={tarea.id}>
                <td>{tarea.nombre}</td>
                <td>{tarea.puntos}</td>
                <td>{tarea.estado}</td>
                <td>{tarea.responsableId ?? "Cualquiera"}</td>
                <td>
                  {puedeCompletar(tarea, usuarioId, rolUsuarioActual) && (
                    <button type="button" onClick={() => handleCompletar(tarea.id)}>
                      Marcar completada
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <h3>Historial de tareas</h3>
      <table aria-label="Historial de tareas">
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Miembro</th>
            <th>Tarea</th>
            <th>Puntos</th>
          </tr>
        </thead>
        <tbody>
          {historial.map((registro) => (
            <tr key={registro.id}>
              <td>{registro.completada_en}</td>
              <td>{registro.miembro_id}</td>
              <td>{registro.tarea_id}</td>
              <td>{registro.puntos_obtenidos}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
