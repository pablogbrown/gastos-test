// Cliente HTTP delgado sobre la API de T3 (tarjetas). No contiene
// lógica de negocio: solo arma requests y tipa las respuestas — mismo
// patrón delgado que `suscripcionesClient.ts`.
import { fetchAutenticado } from "./authClient";
import { ApiError, esApiError, parseJsonOrThrowNullable } from "./httpError";

export type { ApiError };
export { esApiError };

export interface Tarjeta {
  id: string;
  casa_id: string;
  miembro_id: string;
  banco: string;
  nombre: string;
  ultimos_digitos: string;
  fecha_cierre_actual: string;
  fecha_vencimiento_actual: string;
  saldo_actual_ars: string | null;
  saldo_actual_usd: string | null;
  activa: boolean;
  creado_en: string;
}

export interface NuevaTarjeta {
  banco: string;
  nombre: string;
  ultimosDigitos: string;
  fechaCierreActual: string;
  fechaVencimientoActual: string;
}

export interface ActualizacionTarjeta {
  fechaCierreActual?: string;
  fechaVencimientoActual?: string;
  saldoActualArs?: string;
  saldoActualUsd?: string;
}

// spec `importar-resumen-tarjeta`, T4.
export interface ResumenImportado {
  gastos_creados: number;
  cuotas_creadas: number;
  suscripciones_vinculadas: number;
  tarjeta: Tarjeta;
  // spec `resumen-tarjeta-pago`, T4.
  resumen_id: string;
}

// spec `resumen-tarjeta-pago`, T4: un resumen ya importado — mismos
// campos que `ResumenTarjetaOut`, sin alias camelCase (mismo criterio ya
// usado en `Tarjeta` de arriba).
export interface Resumen {
  id: string;
  tarjeta_id: string;
  fecha_cierre: string;
  fecha_vencimiento: string;
  saldo_ars: string | null;
  saldo_usd: string | null;
  gastos_creados: number;
  estado: string;
  importado_en: string;
}

const API_BASE = "/casas";

export async function crearTarjeta(casaId: string, tarjeta: NuevaTarjeta): Promise<Tarjeta> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/tarjetas`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      banco: tarjeta.banco,
      nombre: tarjeta.nombre,
      ultimos_digitos: tarjeta.ultimosDigitos,
      fecha_cierre_actual: tarjeta.fechaCierreActual,
      fecha_vencimiento_actual: tarjeta.fechaVencimientoActual,
    }),
  });
  return (await parseJsonOrThrowNullable<Tarjeta>(resp))!;
}

export async function listarTarjetas(casaId: string): Promise<Tarjeta[]> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/tarjetas`);
  return (await parseJsonOrThrowNullable<Tarjeta[]>(resp))!;
}

export async function actualizarTarjeta(
  casaId: string,
  tarjetaId: string,
  cambios: ActualizacionTarjeta
): Promise<Tarjeta> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/tarjetas/${tarjetaId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      fecha_cierre_actual: cambios.fechaCierreActual,
      fecha_vencimiento_actual: cambios.fechaVencimientoActual,
      saldo_actual_ars: cambios.saldoActualArs,
      saldo_actual_usd: cambios.saldoActualUsd,
    }),
  });
  return (await parseJsonOrThrowNullable<Tarjeta>(resp))!;
}

export async function eliminarTarjeta(casaId: string, tarjetaId: string): Promise<void> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/tarjetas/${tarjetaId}`, {
    method: "DELETE",
  });
  await parseJsonOrThrowNullable<null>(resp);
}

/** Sube el PDF de un resumen (spec `importar-resumen-tarjeta`, REQ-001 a
 * REQ-007): sin ningún paso de confirmación previo (REQ-007), la
 * importación queda hecha en cuanto la promesa resuelve. Sin `Content-
 * Type` manual en el header — `FormData` deja que el browser fije el
 * boundary correcto de `multipart/form-data`, mismo criterio documentado
 * en `01-plan-04-frontend-importar.md`. */
export async function importarResumen(
  casaId: string,
  tarjetaId: string,
  archivo: File
): Promise<ResumenImportado> {
  const formData = new FormData();
  formData.append("archivo", archivo);
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/tarjetas/${tarjetaId}/resumen`, {
    method: "POST",
    body: formData,
  });
  return (await parseJsonOrThrowNullable<ResumenImportado>(resp))!;
}

/** Resúmenes ya importados de una tarjeta (spec `resumen-tarjeta-pago`,
 * REQ-005), más recientes primero. */
export async function listarResumenes(casaId: string, tarjetaId: string): Promise<Resumen[]> {
  const resp = await fetchAutenticado(`${API_BASE}/${casaId}/tarjetas/${tarjetaId}/resumenes`);
  return (await parseJsonOrThrowNullable<Resumen[]>(resp))!;
}

/** Marca un resumen y todos sus gastos vinculados como pagados, en una
 * sola acción (spec `resumen-tarjeta-pago`, REQ-004). */
export async function pagarResumen(
  casaId: string,
  tarjetaId: string,
  resumenId: string
): Promise<Resumen> {
  const resp = await fetchAutenticado(
    `${API_BASE}/${casaId}/tarjetas/${tarjetaId}/resumenes/${resumenId}/pagar`,
    { method: "PATCH" }
  );
  return (await parseJsonOrThrowNullable<Resumen>(resp))!;
}
