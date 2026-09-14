// Cliente HTTP delgado sobre la API de T3 (dashboard y actividad). No
// contiene lógica de negocio: solo arma requests y tipa las respuestas.
// Reutiliza los tipos ya definidos por `casasClient`/`gastosClient`/
// `tareasClient` para las secciones que agrega el dashboard, en vez de
// redefinirlos, para no divergir de los contratos ya fijados por las
// specs `casas-miembros`/`gastos`/`tareas-puntos`.
//
// Spec `usuarios-auth`: usa `fetchAutenticado` (Authorization: Bearer
// <jwt>) en vez de `X-Usuario-Id`.
import { fetchAutenticado } from "./authClient";
import { ApiError, esApiError, formatErrorDetail, Miembro } from "./casasClient";
import { BalancePorMiembro, Gasto } from "./gastosClient";
import { HistorialTarea, RankingEntry, Tarea } from "./tareasClient";

export type { ApiError };
export { esApiError };

export type TipoActividad =
  | "gasto_registrado"
  | "tarea_creada"
  | "tarea_completada"
  | "puntos_obtenidos"
  | "miembro_agregado";

export interface Actividad {
  id: string;
  casa_id: string;
  tipo: TipoActividad;
  miembro_id?: string | null;
  fecha: string;
  descripcion: string;
}

export interface DashboardCasa {
  miembros: Miembro[];
  gastosRecientes: Gasto[];
  balance: BalancePorMiembro[];
  tareasPendientes: Tarea[];
  tareasCompletadasRecientes: HistorialTarea[];
  ranking: RankingEntry[];
}

const API_BASE = "/casas";

async function parseJsonOrThrow<T>(resp: Response): Promise<T> {
  if (!resp.ok) {
    let detail = resp.statusText;
    try {
      const body = await resp.json();
      detail = formatErrorDetail(body.detail) ?? detail;
    } catch {
      // cuerpo no-JSON o vacío: se mantiene resp.statusText
    }
    const error: ApiError = { status: resp.status, detail };
    throw error;
  }
  return (await resp.json()) as T;
}

export async function obtenerDashboard(casaId: string): Promise<DashboardCasa> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/inicio`);
  return parseJsonOrThrow<DashboardCasa>(resp);
}

export async function obtenerActividad(casaId: string): Promise<Actividad[]> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/actividad`);
  return parseJsonOrThrow<Actividad[]>(resp);
}
