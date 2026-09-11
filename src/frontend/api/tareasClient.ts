// Cliente HTTP delgado sobre la API de T3 (POST/PATCH/GET de
// /casas/{id}/tareas y /casas/{id}/ranking). No contiene lógica de
// negocio: solo arma requests y tipa las respuestas. Mismo patrón que
// `casasClient.ts` (spec `casas-miembros`).

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
  puntos: number;
  descripcion?: string;
  responsableId?: string;
  fechaPrevista?: string;
  recurrente?: boolean;
  frecuencia?: string;
}

export interface ApiError {
  status: number;
  detail: string;
}

function apiBase(casaId: string): string {
  return `/casas/${casaId}`;
}

async function parseJsonOrThrow<T>(resp: Response): Promise<T> {
  if (!resp.ok) {
    let detail = resp.statusText;
    try {
      const body = await resp.json();
      detail = body.detail ?? detail;
    } catch {
      // cuerpo no-JSON o vacío: se mantiene resp.statusText
    }
    const error: ApiError = { status: resp.status, detail };
    throw error;
  }
  return (await resp.json()) as T;
}

export async function crearTarea(
  casaId: string,
  usuarioId: string,
  input: CrearTareaInput
): Promise<Tarea> {
  const resp = await fetch(`${apiBase(casaId)}/tareas`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Usuario-Id": usuarioId },
    body: JSON.stringify(input),
  });
  return parseJsonOrThrow<Tarea>(resp);
}

export async function listarTareas(
  casaId: string,
  usuarioId: string,
  estado?: EstadoTarea
): Promise<Tarea[]> {
  const query = estado ? `?estado=${estado}` : "";
  const resp = await fetch(`${apiBase(casaId)}/tareas${query}`, {
    headers: { "X-Usuario-Id": usuarioId },
  });
  return parseJsonOrThrow<Tarea[]>(resp);
}

export async function completarTarea(
  casaId: string,
  tareaId: string,
  usuarioId: string
): Promise<Tarea> {
  const resp = await fetch(`${apiBase(casaId)}/tareas/${tareaId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", "X-Usuario-Id": usuarioId },
    body: JSON.stringify({ estado: "completada" }),
  });
  return parseJsonOrThrow<Tarea>(resp);
}

export async function listarHistorial(
  casaId: string,
  usuarioId: string
): Promise<HistorialTarea[]> {
  const resp = await fetch(`${apiBase(casaId)}/tareas/historial`, {
    headers: { "X-Usuario-Id": usuarioId },
  });
  return parseJsonOrThrow<HistorialTarea[]>(resp);
}

export async function obtenerRanking(casaId: string, usuarioId: string): Promise<RankingEntry[]> {
  const resp = await fetch(`${apiBase(casaId)}/ranking`, {
    headers: { "X-Usuario-Id": usuarioId },
  });
  return parseJsonOrThrow<RankingEntry[]>(resp);
}

export function esApiError(err: unknown): err is ApiError {
  return typeof err === "object" && err !== null && "status" in err && "detail" in err;
}
