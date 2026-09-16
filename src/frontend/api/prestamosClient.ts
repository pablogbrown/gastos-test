// Cliente HTTP delgado sobre la API de T3 (préstamos). No contiene
// lógica de negocio: solo arma requests y tipa las respuestas — mismo
// patrón delgado que `tarjetasClient.ts`.
import { fetchAutenticado } from "./authClient";
import { ApiError, esApiError, formatErrorDetail } from "./httpError";

export type { ApiError };
export { esApiError };

export interface Prestamo {
  id: string;
  casa_id: string;
  prestamista_id: string;
  deudor_id: string;
  importe: string;
  moneda: string;
  descripcion: string | null;
  fecha: string;
  estado: string;
  creado_en: string;
}

export interface NuevoPrestamo {
  prestamistaId: string;
  deudorId: string;
  importe: string;
  moneda?: string;
  fecha: string;
  descripcion?: string;
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

export async function crearPrestamo(casaId: string, prestamo: NuevoPrestamo): Promise<Prestamo> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/prestamos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      prestamista_id: prestamo.prestamistaId,
      deudor_id: prestamo.deudorId,
      importe: prestamo.importe,
      moneda: prestamo.moneda,
      fecha: prestamo.fecha,
      descripcion: prestamo.descripcion || undefined,
    }),
  });
  return (await parseJsonOrThrow<Prestamo>(resp))!;
}

export async function listarPrestamos(casaId: string): Promise<Prestamo[]> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/prestamos`);
  return (await parseJsonOrThrow<Prestamo[]>(resp))!;
}

export async function actualizarEstadoPrestamo(
  casaId: string,
  prestamoId: string,
  estado: string
): Promise<Prestamo> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/prestamos/${prestamoId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ estado }),
  });
  return (await parseJsonOrThrow<Prestamo>(resp))!;
}
