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

/** Normaliza `detail` de una respuesta de error a un string legible.
 *
 * FastAPI devuelve `detail` como string para los errores de negocio
 * (`HTTPException(detail=str(exc))`, ver rutas de la API), pero un 422
 * de validación de Pydantic lo devuelve como un array de objetos
 * `{loc, msg, type}` — sin este chequeo, ese array se propaga tal cual
 * y cualquier pantalla que hace `<Alert>{error.detail}</Alert>` crashea
 * con "Objects are not valid as a React child" (sin error boundary). */
export function formatErrorDetail(raw: unknown): string | undefined {
  if (typeof raw === "string") return raw;
  if (Array.isArray(raw)) {
    const mensajes = raw
      .map((item) =>
        item && typeof item === "object" && "msg" in item ? String((item as { msg: unknown }).msg) : null
      )
      .filter((mensaje): mensaje is string => mensaje !== null);
    if (mensajes.length > 0) return mensajes.join("; ");
  }
  return undefined;
}

export function esApiError(err: unknown): err is ApiError {
  return typeof err === "object" && err !== null && "status" in err && "detail" in err;
}
