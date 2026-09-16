// Cliente HTTP delgado sobre la API de T3 (autos). No contiene lógica de
// negocio: solo arma requests y tipa las respuestas — mismo patrón
// delgado que `tarjetasClient.ts`/`mantenimientoClient.ts`.
import { fetchAutenticado } from "./authClient";
import { ApiError, esApiError, formatErrorDetail } from "./httpError";

export type { ApiError };
export { esApiError };

export interface Auto {
  id: string;
  casa_id: string;
  marca: string;
  modelo: string;
  patente: string | null;
  anio: number | null;
  creado_en: string;
}

export interface NuevoAuto {
  marca: string;
  modelo: string;
  patente?: string;
  anio?: number;
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

export async function crearAuto(casaId: string, auto: NuevoAuto): Promise<Auto> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/autos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      marca: auto.marca,
      modelo: auto.modelo,
      patente: auto.patente || undefined,
      anio: auto.anio,
    }),
  });
  return parseJsonOrThrow<Auto>(resp);
}

export async function listarAutos(casaId: string): Promise<Auto[]> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/autos`);
  return parseJsonOrThrow<Auto[]>(resp);
}
