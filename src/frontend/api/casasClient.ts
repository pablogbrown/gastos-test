// Cliente HTTP delgado sobre la API de T3 (POST/PATCH/GET de /casas).
// No contiene lógica de negocio: solo arma requests y tipa las respuestas.
//
// Spec `usuarios-auth`: reemplaza el header placeholder `X-Usuario-Id`
// por `Authorization: Bearer <jwt>` — el "actor" ya no se pasa como
// parámetro de cada función, se resuelve del lado del backend a partir
// del JWT que agrega `fetchAutenticado` (`authClient.ts`).
import { fetchAutenticado } from "./authClient";
import { ApiError, esApiError, parseJsonOrThrow } from "./httpError";

export type { ApiError };
export { esApiError };

export type Rol = "admin" | "member";

export interface Miembro {
  id: string;
  /** Spec `resolver-rol-usuario-en-casa` (REQ-001): FK al `Usuario` global
   * dueño de este `Miembro` en esta casa — cruzado en `App.tsx` contra
   * `obtenerUsuarioIdActual()` para resolver "mi rol real" y "mi propio
   * Miembro.id". `null` para filas sembradas antes de `usuarios-auth`. */
  usuario_id: string | null;
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
  meta_puntos_mensual?: number | null;
}

const API_BASE = "/casas";

export async function crearCasa(nombre: string): Promise<Casa> {
  const resp = await fetchAutenticado(API_BASE, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nombre }),
  });
  return parseJsonOrThrow<Casa>(resp);
}

/** REQ-004: las Casas donde el Usuario autenticado tiene un Miembro
 * activo — fuente de datos de `SelectorCasas.tsx` (T3). */
export async function listarCasasMias(): Promise<Casa[]> {
  const resp = await fetchAutenticado(`${API_BASE}/mias`);
  return parseJsonOrThrow<Casa[]>(resp);
}

export async function listarMiembros(casaId: string): Promise<Miembro[]> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/miembros`);
  return parseJsonOrThrow<Miembro[]>(resp);
}

export async function agregarMiembro(
  casaId: string,
  nombre: string,
  identificacion: string,
  email: string
): Promise<Miembro> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/miembros`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nombre, identificacion, email }),
  });
  return parseJsonOrThrow<Miembro>(resp);
}

export async function desactivarMiembro(casaId: string, miembroId: string): Promise<Miembro> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/miembros/${miembroId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ activo: false }),
  });
  return parseJsonOrThrow<Miembro>(resp);
}

/** Spec `gamificacion-puntos`, REQ-005: configura (o desactiva, con
 * `meta=null`) la meta de puntos mensual de la casa — requiere
 * Administrador (la API rechaza con 403 si no lo es). */
export async function actualizarMetaPuntos(casaId: string, meta: number | null): Promise<Casa> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/meta`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ meta }),
  });
  return parseJsonOrThrow<Casa>(resp);
}
