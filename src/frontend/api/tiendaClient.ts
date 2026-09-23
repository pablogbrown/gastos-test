// Cliente HTTP delgado sobre la API de la tienda de accesorios (spec
// `tienda-accesorios`). No contiene lógica de negocio: solo arma
// requests y tipa las respuestas. Mismo patrón que `avatarClient.ts`.
//
// Rutas anidadas bajo `/casas/{casaId}/miembros/{miembroId}/...` — igual
// que `avatarClient.ts` (ver Judgment de `tienda.py`, backend).
import { fetchAutenticado } from "./authClient";
import { ApiError, esApiError, parseJsonOrThrow, parseJsonOrThrowNullable } from "./httpError";

export type { ApiError };
export { esApiError };

export interface AccesorioAvatar {
  id: string;
  nombre: string;
  slot: string;
  rareza: string;
  precio_creditos: number;
  especie_compatible: string;
  asset_overlay_url: string;
  disponible_desde?: string | null;
  disponible_hasta?: string | null;
}

function apiBase(casaId: string, miembroId: string): string {
  return `/casas/${casaId}/miembros/${miembroId}`;
}

export async function listarCatalogoAccesorios(
  casaId: string,
  miembroId: string
): Promise<AccesorioAvatar[]> {
  const resp = await fetchAutenticado(`${apiBase(casaId, miembroId)}/accesorios/catalogo`);
  return parseJsonOrThrow<AccesorioAvatar[]>(resp);
}

export async function listarInventario(casaId: string, miembroId: string): Promise<AccesorioAvatar[]> {
  const resp = await fetchAutenticado(`${apiBase(casaId, miembroId)}/accesorios`);
  return parseJsonOrThrow<AccesorioAvatar[]>(resp);
}

// Spec `perfil-avatar-ui`, REQ-001 ([S003] de `tienda-accesorios`
// resuelto en este build: la ruta backend no existía todavía — ver
// Judgment de `tienda.py`). Usado por Miembros/Ranking para pintar el
// overlay de los accesorios equipados de cada miembro.
export async function listarAccesoriosEquipados(
  casaId: string,
  miembroId: string
): Promise<AccesorioAvatar[]> {
  const resp = await fetchAutenticado(`${apiBase(casaId, miembroId)}/accesorios/equipados`);
  return parseJsonOrThrow<AccesorioAvatar[]>(resp);
}

export async function comprarAccesorio(
  casaId: string,
  miembroId: string,
  accesorioId: string
): Promise<AccesorioAvatar> {
  const resp = await fetchAutenticado(
    `${apiBase(casaId, miembroId)}/accesorios/${accesorioId}/comprar`,
    { method: "POST" }
  );
  return parseJsonOrThrow<AccesorioAvatar>(resp);
}

export async function equiparAccesorio(
  casaId: string,
  miembroId: string,
  accesorioId: string
): Promise<AccesorioAvatar> {
  const resp = await fetchAutenticado(`${apiBase(casaId, miembroId)}/accesorios/equipar`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ accesorio_id: accesorioId }),
  });
  return parseJsonOrThrow<AccesorioAvatar>(resp);
}

export async function desequiparSlot(casaId: string, miembroId: string, slot: string): Promise<void> {
  const resp = await fetchAutenticado(`${apiBase(casaId, miembroId)}/accesorios/${slot}/equipado`, {
    method: "DELETE",
  });
  await parseJsonOrThrowNullable<null>(resp);
}
