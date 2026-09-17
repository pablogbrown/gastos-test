// Tipos y helpers de error HTTP compartidos por los ~10 clientes de API
// del frontend (casasClient/gastosClient/tareasClient/dashboardClient/
// authClient/mantenimientoClient/suscripcionesClient/autosClient/
// tarjetasClient/prestamosClient). Módulo propio (no dentro de
// `casasClient.ts`) para que `authClient.ts` pueda importar
// `formatErrorDetail` sin crear un ciclo: `casasClient` necesita
// `fetchAutenticado` de `authClient`, así que si estos helpers vivieran
// en `casasClient.ts`, `authClient` no podría importarlos de vuelta.
//
// `parseJsonOrThrow`/`parseJsonOrThrowNullable` (más abajo) también
// vivían duplicados, uno por cliente, hasta que se extrajeron acá.

export interface ApiError {
  status: number;
  detail: string;
}

// Mensaje genérico para cualquier 422 de validación de Pydantic — nunca
// se le muestra al usuario el texto crudo de esos errores (en inglés,
// con jerga de implementación como "uuid"/"decimal"/"field required").
const MENSAJE_VALIDACION_GENERICO = "Revisá que todos los campos estén completos y sean válidos.";

/** Normaliza `detail` de una respuesta de error a un string legible.
 *
 * FastAPI devuelve `detail` como string para los errores de negocio
 * (`HTTPException(detail=str(exc))`, ver rutas de la API) — esos
 * mensajes ya están en español y pensados para el usuario, se muestran
 * tal cual. Un 422 de validación de Pydantic, en cambio, lo devuelve
 * como un array de objetos `{loc, msg, type}` con mensajes técnicos en
 * inglés (ej. "value is not a valid uuid") — nunca deben llegar al
 * usuario así: además del riesgo de crash ya conocido (`<Alert>
 * {error.detail}</Alert>` con un objeto/array revienta con "Objects are
 * not valid as a React child", sin error boundary), exponen detalles de
 * implementación. Se reemplazan siempre por un mensaje genérico. */
export function formatErrorDetail(raw: unknown): string | undefined {
  if (typeof raw === "string") return raw;
  if (Array.isArray(raw) && raw.length > 0) return MENSAJE_VALIDACION_GENERICO;
  return undefined;
}

export function esApiError(err: unknown): err is ApiError {
  return typeof err === "object" && err !== null && "status" in err && "detail" in err;
}

/** Parsea el body JSON de una respuesta exitosa, o arma y lanza un
 * `ApiError` legible a partir de una respuesta no-ok — mismo criterio de
 * error en los ~10 clientes de API de este proyecto (extraído acá para
 * no duplicarlo en cada uno). Usar esta variante cuando el endpoint
 * nunca responde 204 (todo GET/POST/PATCH con body). */
export async function parseJsonOrThrow<T>(resp: Response): Promise<T> {
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

/** Igual que `parseJsonOrThrow`, pero para un endpoint que puede
 * responder 204 (ej. un DELETE) — devuelve `null` en ese caso en vez de
 * intentar parsear un body vacío como JSON. */
export async function parseJsonOrThrowNullable<T>(resp: Response): Promise<T | null> {
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
