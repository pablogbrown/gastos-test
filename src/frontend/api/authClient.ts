// Cliente HTTP + sesión de autenticación (spec `usuarios-auth`,
// sub-spec `auth-frontend`). Dos responsabilidades:
//  1. Llamar a `POST /auth/login` / `POST /auth/registro` del backend de
//     `auth-backend`.
//  2. Centralizar el manejo de la sesión (guardar/leer/borrar el JWT en
//     `localStorage`) y exponer `fetchAutenticado`, el wrapper de
//     `fetch` que usan `casasClient`/`gastosClient`/`tareasClient`/
//     `dashboardClient` en vez de enviar el header `X-Usuario-Id` — todos
//     agregan `Authorization: Bearer <jwt>` desde acá, un único lugar
//     que cambia si mañana se reemplaza `localStorage` por otro
//     mecanismo (Design Rationale, T2).
import { ApiError, formatErrorDetail } from "./httpError";

export const TOKEN_STORAGE_KEY = "taskia_jwt";

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface RegistroResponse {
  id: string;
  email: string;
}

let listenersCierreSesion: Array<() => void> = [];

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

/** REQ-002/TC-002: registra un Usuario nuevo. No auto-loguea — el
 * llamador (`Registro.tsx`) navega a `Login` con el registro exitoso. */
export async function registrar(
  nombre: string,
  email: string,
  password: string
): Promise<RegistroResponse> {
  const resp = await fetch("/auth/registro", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nombre, email, password }),
  });
  return parseJsonOrThrow<RegistroResponse>(resp);
}

/** REQ-001/TC-003: autentica y devuelve el JWT — `Login.tsx` es quien
 * llama a `guardarSesion` con `access_token`, no esta función. */
export async function login(email: string, password: string): Promise<LoginResponse> {
  const resp = await fetch("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  return parseJsonOrThrow<LoginResponse>(resp);
}

export function guardarSesion(token: string): void {
  localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

export function obtenerToken(): string | null {
  return localStorage.getItem(TOKEN_STORAGE_KEY);
}

/** REQ-005/TC-006: borra la sesión guardada y notifica a quien esté
 * suscripto (`App.tsx`) para que vuelva a mostrar `Login` — el mismo
 * mecanismo dispara tanto un logout explícito como el logout automático
 * de TC-004 (401 de cualquier cliente). */
export function cerrarSesion(): void {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
  listenersCierreSesion.forEach((listener) => listener());
}

export function suscribirseACierreSesion(listener: () => void): () => void {
  listenersCierreSesion.push(listener);
  return () => {
    listenersCierreSesion = listenersCierreSesion.filter((actual) => actual !== listener);
  };
}

/** Decodifica el `sub` (usuario_id) del JWT guardado, sin verificar firma
 * — la verificación real ya la hace el backend en cada request; esto es
 * solo para que pantallas que necesitan la identidad del usuario actual
 * a nivel de UI (p. ej. `Tareas.tsx`, "¿soy yo el responsable?") no
 * dependan de un segundo request. Devuelve `null` ante cualquier token
 * ausente o mal formado. */
export function obtenerUsuarioIdActual(): string | null {
  const token = obtenerToken();
  if (!token) return null;
  try {
    const payload = token.split(".")[1];
    const normalizado = payload.replace(/-/g, "+").replace(/_/g, "/");
    const json = JSON.parse(atob(normalizado)) as { sub?: unknown };
    return typeof json.sub === "string" ? json.sub : null;
  } catch {
    return null;
  }
}

/** Wrapper de `fetch` para los clientes autenticados (TC-003): agrega
 * `Authorization: Bearer <jwt>` cuando hay sesión guardada, y ante un 401
 * (sesión inválida/expirada) dispara `cerrarSesion()` (TC-004) antes de
 * devolver la `Response` — el caller sigue usando su propio
 * `parseJsonOrThrow` para reportar el error como siempre, esto solo
 * agrega el efecto secundario de la sesión. */
export async function fetchAutenticado(
  input: RequestInfo | URL,
  init: RequestInit = {}
): Promise<Response> {
  const token = obtenerToken();
  const headers = new Headers(init.headers);
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  const resp = await fetch(input, { ...init, headers });
  if (resp.status === 401) {
    cerrarSesion();
  }
  return resp;
}
