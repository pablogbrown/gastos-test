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
import { ApiError, esApiError, Miembro } from "./casasClient";
import { AporteMiembro, Gasto, TotalCasa } from "./gastosClient";
import { parseJsonOrThrow } from "./httpError";
import { HistorialTarea, RankingEntry, Tarea } from "./tareasClient";

export type { ApiError };
export { esApiError };

export type TipoActividad =
  | "gasto_registrado"
  | "tarea_creada"
  | "tarea_completada"
  | "puntos_obtenidos"
  | "miembro_agregado"
  | "miembro_desactivado";

export interface Actividad {
  id: string;
  casa_id: string;
  tipo: TipoActividad;
  miembro_id?: string | null;
  fecha: string;
  descripcion: string;
}

/** Spec `tarjetas-credito`, REQ-004: tarjeta activa cuyo vencimiento está
 * a `UMBRAL_ALERTA_DIAS` días o menos, o ya venció. Mismo shape que
 * `TarjetaAlertaOut` (backend) — snake_case, sin alias (ver
 * `dashboard.py`: solo el campo contenedor `tarjetasConAlerta` se
 * camelCasea, no los objetos que contiene, mismo criterio que
 * `gastosRecientes`/`Gasto`). */
export interface TarjetaAlerta {
  id: string;
  nombre: string;
  banco: string;
  fecha_vencimiento_actual: string;
  dias_para_vencimiento: number;
  vencida: boolean;
}

/** Spec `mantenimiento-casa`, REQ-005: ítem de mantenimiento pendiente
 * cuya fecha estimada está a `UMBRAL_ALERTA_DIAS` días o menos, o ya
 * venció. Mismo shape que `ItemMantenimientoAlertaOut` (backend) —
 * snake_case, sin alias, mismo criterio que `TarjetaAlerta` arriba: solo
 * el campo contenedor `mantenimientoConAlerta` se camelCasea, no los
 * objetos que contiene. Spec `mantenimiento-autos`, REQ-004:
 * `auto_id`/`auto_nombre` (aditivo) — `null`/`undefined` para un ítem de
 * la casa, poblados cuando pertenece a un auto puntual. */
export interface ItemMantenimientoAlerta {
  id: string;
  nombre: string;
  fecha_estimada: string;
  dias_para_vencimiento: number;
  vencido: boolean;
  auto_id?: string | null;
  auto_nombre?: string | null;
}

/** Spec `gastos-sin-reparto`: mismo contrato que `BalanceResponse`
 * (`gastosClient.ts`) — total de la casa por moneda más el aporte
 * informativo de cada miembro, sin ningún campo de deuda. */
export interface BalanceCasa {
  totales: TotalCasa[];
  aportes: AporteMiembro[];
}

/** Spec `gamificacion-puntos`, REQ-005: mismo shape que
 * `calcular_progreso_meta` (backend) — snake_case, sin alias ([API-01]:
 * solo el campo contenedor `metaCasa` se camelCasea, no sus claves
 * internas). */
export interface MetaCasaProgreso {
  puntos_acumulados: number;
  meta: number;
  porcentaje: number;
}

export interface DashboardCasa {
  miembros: Miembro[];
  gastosRecientes: Gasto[];
  balance: BalanceCasa;
  tareasPendientes: Tarea[];
  tareasCompletadasRecientes: HistorialTarea[];
  ranking: RankingEntry[];
  tarjetasConAlerta: TarjetaAlerta[];
  mantenimientoConAlerta: ItemMantenimientoAlerta[];
  metaCasa?: MetaCasaProgreso | null;
}

const API_BASE = "/casas";

export async function obtenerDashboard(casaId: string): Promise<DashboardCasa> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/inicio`);
  return parseJsonOrThrow<DashboardCasa>(resp);
}

export async function obtenerActividad(casaId: string): Promise<Actividad[]> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/actividad`);
  return parseJsonOrThrow<Actividad[]>(resp);
}
