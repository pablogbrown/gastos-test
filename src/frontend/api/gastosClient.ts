// Cliente HTTP delgado sobre la API de T3 (categorías, gastos, balance).
// No contiene lógica de negocio: solo arma requests y tipa las respuestas.
//
// Spec `usuarios-auth`: usa `fetchAutenticado` (Authorization: Bearer
// <jwt>) en vez de `X-Usuario-Id` — ver `casasClient.ts` para el mismo
// patrón.
import { fetchAutenticado } from "./authClient";
import { ApiError, esApiError, formatErrorDetail } from "./httpError";

export type { ApiError };
export { esApiError };

export interface Categoria {
  id: string;
  casa_id: string;
  nombre: string;
}

export interface ParticipanteGasto {
  miembro_id: string;
  monto_correspondiente: string;
}

export interface Gasto {
  id: string;
  casa_id: string;
  descripcion: string;
  importe: string;
  fecha: string;
  pagado_por: string;
  categoria_id: string;
  participantes: ParticipanteGasto[];
  cuota_grupo_id?: string | null;
  cuota_numero?: number | null;
  cuota_total?: number | null;
  // Spec `gastos-multi-moneda`: siempre presente ("ARS" o "USD").
  moneda: string;
  // Spec `gastos-estado-pago`: siempre presente ("pagado" o "a_pagar").
  estado: string;
}

export interface BalancePorMiembro {
  miembro_id: string;
  nombre: string;
  pago: string;
  correspondia: string;
  balance: string;
  // Spec `gastos-multi-moneda`, REQ-002: la moneda de esta fila.
  moneda: string;
}

export interface Transferencia {
  deudor_id: string;
  acreedor_id: string;
  monto: string;
  // Spec `gastos-multi-moneda`, REQ-003: la moneda del grupo dentro del
  // que se sugirió esta transferencia.
  moneda: string;
}

export interface BalanceResponse {
  balances: BalancePorMiembro[];
  transferencias: Transferencia[];
}

export interface NuevoGasto {
  descripcion: string;
  importe: string;
  fecha: string;
  categoriaId: string;
  pagadoPor?: string;
  participantes?: string[];
  cuotas?: number;
  // Spec `gastos-multi-moneda`: ausente -> "ARS" (default) en el
  // backend — nunca se fuerza "ARS" explícito en el body.
  moneda?: "ARS" | "USD";
  // Spec `gastos-estado-pago`: ausente -> "pagado" (default) en el
  // backend — nunca se fuerza "pagado" explícito en el body, mismo
  // criterio que `moneda`.
  estado?: "pagado" | "a_pagar";
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

export async function listarCategorias(casaId: string): Promise<Categoria[]> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/categorias`);
  return parseJsonOrThrow<Categoria[]>(resp);
}

export async function crearCategoria(casaId: string, nombre: string): Promise<Categoria> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/categorias`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nombre }),
  });
  return parseJsonOrThrow<Categoria>(resp);
}

export async function registrarGasto(casaId: string, gasto: NuevoGasto): Promise<Gasto> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/gastos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      descripcion: gasto.descripcion,
      importe: gasto.importe,
      fecha: gasto.fecha,
      categoria_id: gasto.categoriaId,
      pagado_por: gasto.pagadoPor,
      participantes: gasto.participantes,
      cuotas: gasto.cuotas,
      moneda: gasto.moneda,
      estado: gasto.estado,
    }),
  });
  return parseJsonOrThrow<Gasto>(resp);
}

export async function listarGastos(casaId: string, mes?: string): Promise<Gasto[]> {
  const query = mes ? `?mes=${mes}` : "";
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/gastos${query}`);
  return parseJsonOrThrow<Gasto[]>(resp);
}

export async function actualizarEstadoGasto(
  casaId: string,
  gastoId: string,
  estado: "pagado" | "a_pagar"
): Promise<Gasto> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/gastos/${gastoId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ estado }),
  });
  return parseJsonOrThrow<Gasto>(resp);
}

export async function obtenerBalance(casaId: string, mes?: string): Promise<BalanceResponse> {
  const query = mes ? `?mes=${mes}` : "";
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/balance${query}`);
  return parseJsonOrThrow<BalanceResponse>(resp);
}
