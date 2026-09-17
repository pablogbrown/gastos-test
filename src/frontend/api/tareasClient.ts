// Cliente HTTP delgado sobre la API de T3 (POST/PATCH/GET de
// /casas/{id}/tareas y /casas/{id}/ranking). No contiene lógica de
// negocio: solo arma requests y tipa las respuestas. Mismo patrón que
// `casasClient.ts` (spec `casas-miembros`).
//
// Spec `usuarios-auth`: usa `fetchAutenticado` (Authorization: Bearer
// <jwt>) en vez de `X-Usuario-Id`.
import { fetchAutenticado } from "./authClient";
import { ApiError, esApiError, parseJsonOrThrow } from "./httpError";

export type { ApiError };
export { esApiError };

export type EstadoTarea = "pendiente" | "en_curso" | "completada";

export interface Tarea {
  id: string;
  casa_id: string;
  nombre: string;
  descripcion?: string | null;
  puntos: number;
  responsableId?: string | null;
  fechaPrevista?: string | null;
  estado: EstadoTarea;
  recurrente: boolean;
  frecuencia?: string | null;
}

export interface HistorialTarea {
  id: string;
  tarea_id: string;
  miembro_id: string;
  completada_en: string;
  puntos_obtenidos: number;
}

export interface RankingEntry {
  miembroId: string;
  puntos: number;
}

export interface CrearTareaInput {
  nombre: string;
  puntos: number | undefined;
  descripcion?: string;
  responsableId?: string;
  fechaPrevista?: string;
  recurrente?: boolean;
  frecuencia?: string;
}

function apiBase(casaId: string): string {
  return `/casas/${casaId}`;
}

export async function crearTarea(casaId: string, input: CrearTareaInput): Promise<Tarea> {
  const resp = await fetchAutenticado(`${apiBase(casaId)}/tareas`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  return parseJsonOrThrow<Tarea>(resp);
}

export async function listarTareas(casaId: string, estado?: EstadoTarea): Promise<Tarea[]> {
  const query = estado ? `?estado=${estado}` : "";
  const resp = await fetchAutenticado(`${apiBase(casaId)}/tareas${query}`);
  return parseJsonOrThrow<Tarea[]>(resp);
}

export async function completarTarea(casaId: string, tareaId: string): Promise<Tarea> {
  const resp = await fetchAutenticado(`${apiBase(casaId)}/tareas/${tareaId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ estado: "completada" }),
  });
  return parseJsonOrThrow<Tarea>(resp);
}

export async function listarHistorial(casaId: string): Promise<HistorialTarea[]> {
  const resp = await fetchAutenticado(`${apiBase(casaId)}/tareas/historial`);
  return parseJsonOrThrow<HistorialTarea[]>(resp);
}

export async function obtenerRanking(casaId: string): Promise<RankingEntry[]> {
  const resp = await fetchAutenticado(`${apiBase(casaId)}/ranking`);
  return parseJsonOrThrow<RankingEntry[]>(resp);
}
