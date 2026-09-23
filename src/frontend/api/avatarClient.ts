// Cliente HTTP delgado sobre la API de T3 (avatares/créditos). No
// contiene lógica de negocio: solo arma requests y tipa las respuestas.
// Mismo patrón que `tareasClient.ts`/`casasClient.ts`.
//
// Rutas anidadas bajo `/casas/{casaId}/miembros/{miembroId}/...` — igual
// que toda otra ruta autenticada de este proyecto (`resolver_actor_en_casa`
// exige `casa_id` en la URL; ver Judgment de `avatares.py`, backend).
import { fetchAutenticado } from "./authClient";
import { ApiError, esApiError, parseJsonOrThrow } from "./httpError";

export type { ApiError };
export { esApiError };

export interface AvatarPersonaje {
  id: string;
  especie: string;
  raza: string;
  lottie_url: string;
  nivel_requerido: string;
  rareza: string;
  disponible_desde?: string | null;
  disponible_hasta?: string | null;
}

export interface Creditos {
  saldo: number;
}

function apiBase(casaId: string, miembroId: string): string {
  return `/casas/${casaId}/miembros/${miembroId}`;
}

export async function obtenerCreditos(casaId: string, miembroId: string): Promise<Creditos> {
  const resp = await fetchAutenticado(`${apiBase(casaId, miembroId)}/creditos`);
  return parseJsonOrThrow<Creditos>(resp);
}

export async function listarAvataresDisponibles(
  casaId: string,
  miembroId: string
): Promise<AvatarPersonaje[]> {
  const resp = await fetchAutenticado(`${apiBase(casaId, miembroId)}/avatares-disponibles`);
  return parseJsonOrThrow<AvatarPersonaje[]>(resp);
}

// Spec `perfil-avatar-ui`, REQ-002/TC-004 (ver Judgment de `avatares.py`,
// backend): catálogo completo (locked+unlocked), nunca expuesto por
// `avatares-economia` — "Mi Avatar" lo necesita para mostrar las razas
// bloqueadas con su nivel requerido, no solo las ya desbloqueadas de
// `listarAvataresDisponibles`.
export async function listarAvataresCatalogo(
  casaId: string,
  miembroId: string
): Promise<AvatarPersonaje[]> {
  const resp = await fetchAutenticado(`${apiBase(casaId, miembroId)}/avatares-catalogo`);
  return parseJsonOrThrow<AvatarPersonaje[]>(resp);
}

export async function obtenerAvatarSeleccionado(
  casaId: string,
  miembroId: string
): Promise<AvatarPersonaje | null> {
  const resp = await fetchAutenticado(`${apiBase(casaId, miembroId)}/avatar`);
  return parseJsonOrThrow<AvatarPersonaje | null>(resp);
}

export async function seleccionarAvatar(
  casaId: string,
  miembroId: string,
  avatarPersonajeId: string
): Promise<AvatarPersonaje> {
  const resp = await fetchAutenticado(`${apiBase(casaId, miembroId)}/avatar`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ avatar_personaje_id: avatarPersonajeId }),
  });
  return parseJsonOrThrow<AvatarPersonaje>(resp);
}
