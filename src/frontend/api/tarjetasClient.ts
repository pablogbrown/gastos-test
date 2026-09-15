// Cliente HTTP delgado sobre la API de T3 (tarjetas). No contiene
// lógica de negocio: solo arma requests y tipa las respuestas — mismo
// patrón delgado que `suscripcionesClient.ts`.
import { fetchAutenticado } from "./authClient";
import { ApiError, esApiError, formatErrorDetail } from "./httpError";

export type { ApiError };
export { esApiError };

export interface Tarjeta {
  id: string;
  casa_id: string;
  miembro_id: string;
  banco: string;
  nombre: string;
  ultimos_digitos: string;
  fecha_cierre_actual: string;
  fecha_vencimiento_actual: string;
  saldo_actual_ars: string | null;
  saldo_actual_usd: string | null;
  activa: boolean;
  creado_en: string;
}

export interface NuevaTarjeta {
  banco: string;
  nombre: string;
  ultimosDigitos: string;
  fechaCierreActual: string;
  fechaVencimientoActual: string;
}

export interface ActualizacionTarjeta {
  fechaCierreActual?: string;
  fechaVencimientoActual?: string;
  saldoActualArs?: string;
  saldoActualUsd?: string;
}

const API_BASE = "/casas";

async function parseJsonOrThrow<T>(resp: Response): Promise<T | null> {
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
  if (resp.status === 204) return null;
  return (await resp.json()) as T;
}

export async function crearTarjeta(casaId: string, tarjeta: NuevaTarjeta): Promise<Tarjeta> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/tarjetas`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      banco: tarjeta.banco,
      nombre: tarjeta.nombre,
      ultimos_digitos: tarjeta.ultimosDigitos,
      fecha_cierre_actual: tarjeta.fechaCierreActual,
      fecha_vencimiento_actual: tarjeta.fechaVencimientoActual,
    }),
  });
  return (await parseJsonOrThrow<Tarjeta>(resp))!;
}

export async function listarTarjetas(casaId: string): Promise<Tarjeta[]> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/tarjetas`);
  return (await parseJsonOrThrow<Tarjeta[]>(resp))!;
}

export async function actualizarTarjeta(
  casaId: string,
  tarjetaId: string,
  cambios: ActualizacionTarjeta
): Promise<Tarjeta> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/tarjetas/${tarjetaId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      fecha_cierre_actual: cambios.fechaCierreActual,
      fecha_vencimiento_actual: cambios.fechaVencimientoActual,
      saldo_actual_ars: cambios.saldoActualArs,
      saldo_actual_usd: cambios.saldoActualUsd,
    }),
  });
  return (await parseJsonOrThrow<Tarjeta>(resp))!;
}

export async function eliminarTarjeta(casaId: string, tarjetaId: string): Promise<void> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/tarjetas/${tarjetaId}`, {
    method: "DELETE",
  });
  await parseJsonOrThrow<null>(resp);
}
