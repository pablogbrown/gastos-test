// Cliente HTTP delgado sobre la API de T3 (categorías, gastos, balance).
// No contiene lógica de negocio: solo arma requests y tipa las respuestas.
import { ApiError, esApiError, formatErrorDetail } from "./casasClient";

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
}

export interface BalancePorMiembro {
  miembro_id: string;
  nombre: string;
  pago: string;
  correspondia: string;
  balance: string;
}

export interface Transferencia {
  deudor_id: string;
  acreedor_id: string;
  monto: string;
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

export async function listarCategorias(casaId: string, usuarioId: string): Promise<Categoria[]> {
  const resp = await fetch(`${API_BASE}/${casaId}/categorias`, {
    headers: { "X-Usuario-Id": usuarioId },
  });
  return parseJsonOrThrow<Categoria[]>(resp);
}

export async function crearCategoria(
  casaId: string,
  nombre: string,
  usuarioId: string
): Promise<Categoria> {
  const resp = await fetch(`${API_BASE}/${casaId}/categorias`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Usuario-Id": usuarioId },
    body: JSON.stringify({ nombre }),
  });
  return parseJsonOrThrow<Categoria>(resp);
}

export async function registrarGasto(
  casaId: string,
  gasto: NuevoGasto,
  usuarioId: string
): Promise<Gasto> {
  const resp = await fetch(`${API_BASE}/${casaId}/gastos`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Usuario-Id": usuarioId },
    body: JSON.stringify({
      descripcion: gasto.descripcion,
      importe: gasto.importe,
      fecha: gasto.fecha,
      categoria_id: gasto.categoriaId,
      pagado_por: gasto.pagadoPor,
      participantes: gasto.participantes,
    }),
  });
  return parseJsonOrThrow<Gasto>(resp);
}

export async function listarGastos(casaId: string, usuarioId: string): Promise<Gasto[]> {
  const resp = await fetch(`${API_BASE}/${casaId}/gastos`, {
    headers: { "X-Usuario-Id": usuarioId },
  });
  return parseJsonOrThrow<Gasto[]>(resp);
}

export async function obtenerBalance(casaId: string, usuarioId: string): Promise<BalanceResponse> {
  const resp = await fetch(`${API_BASE}/${casaId}/balance`, {
    headers: { "X-Usuario-Id": usuarioId },
  });
  return parseJsonOrThrow<BalanceResponse>(resp);
}
