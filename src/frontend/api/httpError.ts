// Tipos y helpers de error HTTP compartidos por todos los clientes de API
// (casasClient/gastosClient/tareasClient/dashboardClient/authClient).
//
// Extraído de `casasClient.ts` (spec `usuarios-auth`) a su propio módulo
// para que `authClient.ts` pueda reusar `formatErrorDetail` sin crear un
// import circular: antes, `authClient` habría tenido que importar desde
// `casasClient`, que a su vez necesita importar `fetchAutenticado` desde
// `authClient`. `casasClient.ts` re-exporta estos símbolos para no romper
// los imports existentes (`gastosClient.ts`, `tareasClient.ts`,
// `dashboardClient.ts` siguen importando `formatErrorDetail` desde
// `./casasClient`).

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
