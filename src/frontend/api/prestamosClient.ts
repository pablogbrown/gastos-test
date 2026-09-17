// Cliente HTTP delgado sobre la API de T3 (préstamos). No contiene
// lógica de negocio: solo arma requests y tipa las respuestas — mismo
// patrón delgado que `tarjetasClient.ts`.
import { fetchAutenticado } from "./authClient";
import { ApiError, esApiError, parseJsonOrThrowNullable } from "./httpError";

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
  // Spec `prestamos-confirmacion-mutua` (T4): campos aditivos.
  confirmado_prestamista: boolean | null;
  confirmado_deudor: boolean | null;
  estado_confirmacion: string;
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
  return (await parseJsonOrThrowNullable<Prestamo>(resp))!;
}

export async function listarPrestamos(casaId: string): Promise<Prestamo[]> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/prestamos`);
  return (await parseJsonOrThrowNullable<Prestamo[]>(resp))!;
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
  return (await parseJsonOrThrowNullable<Prestamo>(resp))!;
}

/** Confirma o rechaza el propio rol en un préstamo pendiente de
 * confirmación (spec `prestamos-confirmacion-mutua`, T4). Ruta propia,
 * separada de `actualizarEstadoPrestamo` — mismo criterio que T3
 * documenta: modelos de permiso distintos. */
export async function confirmarPrestamo(
  casaId: string,
  prestamoId: string,
  confirma: boolean
): Promise<Prestamo> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/prestamos/${prestamoId}/confirmacion`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ confirma }),
  });
  return (await parseJsonOrThrowNullable<Prestamo>(resp))!;
}
