// Cliente HTTP delgado sobre la API de T3 (POST/PATCH/GET de /casas).
// No contiene lógica de negocio: solo arma requests y tipa las respuestas.

export type Rol = "admin" | "member";

export interface Miembro {
  id: string;
  casa_id: string;
  nombre: string;
  identificacion: string;
  rol: Rol;
  activo: boolean;
}

export interface Casa {
  id: string;
  nombre: string;
  creado_en: string;
  miembros: Miembro[];
}

export interface ApiError {
  status: number;
  detail: string;
}

const API_BASE = "/casas";

async function parseJsonOrThrow<T>(resp: Response): Promise<T> {
  if (!resp.ok) {
    let detail = resp.statusText;
    try {
      const body = await resp.json();
      detail = body.detail ?? detail;
    } catch {
      // cuerpo no-JSON o vacío: se mantiene resp.statusText
    }
    const error: ApiError = { status: resp.status, detail };
    throw error;
  }
  return (await resp.json()) as T;
}

export async function crearCasa(nombre: string, usuarioId: string): Promise<Casa> {
  const resp = await fetch(API_BASE, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Usuario-Id": usuarioId },
    body: JSON.stringify({ nombre }),
  });
  return parseJsonOrThrow<Casa>(resp);
}

export async function listarMiembros(casaId: string, usuarioId: string): Promise<Miembro[]> {
  const resp = await fetch(`${API_BASE}/${casaId}/miembros`, {
    headers: { "X-Usuario-Id": usuarioId },
  });
  return parseJsonOrThrow<Miembro[]>(resp);
}

export async function agregarMiembro(
  casaId: string,
  nombre: string,
  identificacion: string,
  usuarioId: string
): Promise<Miembro> {
  const resp = await fetch(`${API_BASE}/${casaId}/miembros`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Usuario-Id": usuarioId },
    body: JSON.stringify({ nombre, identificacion }),
  });
  return parseJsonOrThrow<Miembro>(resp);
}

export async function desactivarMiembro(
  casaId: string,
  miembroId: string,
  usuarioId: string
): Promise<Miembro> {
  const resp = await fetch(`${API_BASE}/${casaId}/miembros/${miembroId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", "X-Usuario-Id": usuarioId },
    body: JSON.stringify({ activo: false }),
  });
  return parseJsonOrThrow<Miembro>(resp);
}

export function esApiError(err: unknown): err is ApiError {
  return typeof err === "object" && err !== null && "status" in err && "detail" in err;
}
