// Cliente HTTP delgado sobre la API de T3 (suscripciones). No contiene
// lógica de negocio: solo arma requests y tipa las respuestas — mismo
// patrón delgado que `gastosClient.ts`.
import { fetchAutenticado } from "./authClient";
import { ApiError, esApiError, formatErrorDetail } from "./httpError";

export type { ApiError };
export { esApiError };

export interface Suscripcion {
  id: string;
  casa_id: string;
  descripcion: string;
  importe: string;
  categoria_id: string;
  pagado_por: string;
  activa: boolean;
  ultimo_mes_generado: string | null;
  creado_en: string;
  // Spec `gastos-multi-moneda`: siempre presente ("ARS" o "USD").
  moneda: string;
}

export interface NuevaSuscripcion {
  descripcion: string;
  importe: string;
  categoriaId: string;
  // Spec `gastos-multi-moneda`: ausente -> "ARS" (default) en el
  // backend — nunca se fuerza "ARS" explícito en el body.
  moneda?: "ARS" | "USD";
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

export async function crearSuscripcion(
  casaId: string,
  suscripcion: NuevaSuscripcion
): Promise<Suscripcion> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/suscripciones`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      descripcion: suscripcion.descripcion,
      importe: suscripcion.importe,
      categoria_id: suscripcion.categoriaId,
      moneda: suscripcion.moneda,
    }),
  });
  return parseJsonOrThrow<Suscripcion>(resp);
}

export async function listarSuscripciones(casaId: string): Promise<Suscripcion[]> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/suscripciones`);
  return parseJsonOrThrow<Suscripcion[]>(resp);
}

export async function cancelarSuscripcion(
  casaId: string,
  suscripcionId: string
): Promise<Suscripcion> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/suscripciones/${suscripcionId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ activa: false }),
  });
  return parseJsonOrThrow<Suscripcion>(resp);
}
