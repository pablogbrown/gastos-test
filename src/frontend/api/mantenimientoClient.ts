// Cliente HTTP delgado sobre la API de T3 (mantenimiento). No contiene
// lógica de negocio: solo arma requests y tipa las respuestas — mismo
// patrón delgado que `tarjetasClient.ts`/`prestamosClient.ts`.
import { fetchAutenticado } from "./authClient";
import { ApiError, esApiError, formatErrorDetail } from "./httpError";

export type { ApiError };
export { esApiError };

export type EstadoItemMantenimiento = "pendiente" | "completado";

export interface Material {
  id: string;
  item_mantenimiento_id: string;
  nombre: string;
  cantidad: number;
  conseguido: boolean;
}

export interface ItemMantenimiento {
  id: string;
  casa_id: string;
  nombre: string;
  descripcion: string | null;
  fecha_estimada: string | null;
  recurrente: boolean;
  periodicidad: string | null;
  estado: EstadoItemMantenimiento;
  creado_en: string;
  materiales: Material[];
  // Spec `mantenimiento-autos`, REQ-002/REQ-003: `null`/`undefined` para
  // un ítem de la casa; poblado cuando pertenece a un auto puntual.
  auto_id?: string | null;
  auto_nombre?: string | null;
}

export interface NuevoMaterial {
  nombre: string;
  cantidad: number;
}

export interface NuevoItemMantenimiento {
  nombre: string;
  descripcion?: string;
  fechaEstimada?: string;
  recurrente?: boolean;
  periodicidad?: string;
  materiales?: NuevoMaterial[];
  // Spec `mantenimiento-autos`, REQ-002: opcional — asocia el ítem a un
  // auto puntual en vez de a la casa.
  autoId?: string;
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

export async function crearItem(
  casaId: string,
  item: NuevoItemMantenimiento
): Promise<ItemMantenimiento> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/mantenimiento`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      nombre: item.nombre,
      descripcion: item.descripcion || undefined,
      fecha_estimada: item.fechaEstimada || undefined,
      recurrente: item.recurrente ?? false,
      periodicidad: item.recurrente ? item.periodicidad : undefined,
      materiales: item.materiales && item.materiales.length > 0 ? item.materiales : undefined,
      auto_id: item.autoId || undefined,
    }),
  });
  return parseJsonOrThrow<ItemMantenimiento>(resp);
}

// Spec `mantenimiento-autos`, REQ-003: `autoId` opcional — sin él, el
// backend devuelve solo los ítems de la casa (`auto_id IS NULL`); con
// él, solo los de ese auto.
export async function listarItems(
  casaId: string,
  autoId?: string
): Promise<ItemMantenimiento[]> {
  const url = autoId
    ? `${API_BASE}/${casaId}/mantenimiento?autoId=${encodeURIComponent(autoId)}`
    : `${API_BASE}/${casaId}/mantenimiento`;
  const resp = await fetchAutenticado(url);
  return parseJsonOrThrow<ItemMantenimiento[]>(resp);
}

export async function completarItem(
  casaId: string,
  itemId: string
): Promise<ItemMantenimiento> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/mantenimiento/${itemId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ estado: "completado" }),
  });
  return parseJsonOrThrow<ItemMantenimiento>(resp);
}

export async function agregarMaterial(
  casaId: string,
  itemId: string,
  material: NuevoMaterial
): Promise<Material> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/mantenimiento/${itemId}/materiales`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(material),
  });
  return parseJsonOrThrow<Material>(resp);
}

export async function actualizarMaterial(
  casaId: string,
  itemId: string,
  materialId: string,
  conseguido: boolean
): Promise<Material> {
  const resp = await fetchAutenticado(
    `${API_BASE}/${casaId}/mantenimiento/${itemId}/materiales/${materialId}`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ conseguido }),
    }
  );
  return parseJsonOrThrow<Material>(resp);
}
