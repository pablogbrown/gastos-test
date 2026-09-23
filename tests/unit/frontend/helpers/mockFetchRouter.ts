import { vi } from "vitest";

// Spec `perfil-avatar-ui`: desde esta spec, Miembros/Ranking disparan
// fetches propios de avatar/accesorios equipados por CADA fila,
// intercalados con el flujo principal de la pantalla (listar miembros,
// alta, meta, ranking, logros). Un mock secuencial por índice de llamada
// (`fetchMock.mockImplementationOnce` encadenado, o `fetchMock.mock.
// calls[N]`) deja de ser confiable en cuanto CUALQUIER pantalla con
// filas de miembro (con avatar) tiene más de una fila — las llamadas de
// avatar de cada fila se intercalan en una posición no determinística
// para el test. Estos helpers despachan por PATRÓN DE URL/MÉTODO en vez
// de por orden de invocación.

export type Respuesta = {
  ok: boolean;
  status?: number;
  statusText?: string;
  json: () => Promise<unknown>;
};

export type Handler = (
  url: string,
  init?: RequestInit
) => Respuesta | undefined;

export function respuestaJson(json: unknown, overrides: Partial<Respuesta> = {}): Respuesta {
  return { ok: true, json: async () => json, ...overrides };
}

export function respuestaError(status: number, detail: string, statusText = "Error"): Respuesta {
  return { ok: false, status, statusText, json: async () => ({ detail }) };
}

/** Arma un mock de `fetch` global que prueba cada `handler` en orden —
 * el primero que devuelve algo (no `undefined`) gana — y cae a
 * `porDefecto` si ninguno matchea. */
export function crearFetchRouter(
  handlers: Handler[],
  porDefecto: Respuesta = respuestaJson(null)
) {
  return vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    for (const handler of handlers) {
      const resultado = handler(url, init);
      if (resultado !== undefined) return resultado;
    }
    return porDefecto;
  });
}

function metodoDe(init?: RequestInit): string {
  return (init?.method ?? "GET").toUpperCase();
}

/** `GET .../avatar` (fin exacto de ruta — nunca matchea
 * `/avatares-disponibles` ni `/avatares-catalogo`, que terminan
 * distinto) → siempre `null` (sin avatar seleccionado), salvo que
 * `porMiembro` tenga una entrada para ese `miembroId`. */
export function handlerAvatar(porMiembro: Record<string, unknown> = {}): Handler {
  return (url, init) => {
    if (metodoDe(init) !== "GET" || !/\/avatar$/.test(url)) return undefined;
    const miembroId = url.match(/\/miembros\/([^/]+)\/avatar$/)?.[1];
    const avatar = miembroId && miembroId in porMiembro ? porMiembro[miembroId] : null;
    return respuestaJson(avatar);
  };
}

/** `GET .../accesorios/equipados` → `[]` salvo que `porMiembro` tenga
 * una entrada para ese `miembroId`. */
export function handlerAccesoriosEquipados(porMiembro: Record<string, unknown[]> = {}): Handler {
  return (url, init) => {
    if (metodoDe(init) !== "GET" || !url.endsWith("/accesorios/equipados")) return undefined;
    const miembroId = url.match(/\/miembros\/([^/]+)\/accesorios\/equipados$/)?.[1];
    const equipados = miembroId && miembroId in porMiembro ? porMiembro[miembroId] : [];
    return respuestaJson(equipados);
  };
}

/** `GET .../miembros` (listado, nunca el alta `POST` a la misma URL) —
 * responde una SECUENCIA fija para llamadas sucesivas (mismo criterio
 * que `mockImplementationOnce` encadenado, pero contado solo sobre
 * llamadas de ESTE tipo, nunca sobre el total de fetches de la
 * pantalla). La última entrada se repite para cualquier llamada
 * adicional. */
export function handlerListaMiembros(secuencia: unknown[][]): Handler {
  let llamada = 0;
  return (url, init) => {
    if (metodoDe(init) !== "GET" || !/\/miembros$/.test(url)) return undefined;
    const indice = Math.min(llamada, secuencia.length - 1);
    llamada += 1;
    return respuestaJson(secuencia[indice]);
  };
}
