# T4 — Botón "Importar resumen" en Tarjetas

## Scope
- `src/frontend/api/tarjetasClient.ts`
- `src/frontend/pages/Tarjetas.tsx`
- `tests/unit/frontend/Tarjetas.test.tsx`

## Changes
- `tarjetasClient.ts`: `importarResumen(casaId: string, tarjetaId:
  string, archivo: File): Promise<ResumenImportado>` — `FormData` con el
  archivo, `fetchAutenticado` (sin `Content-Type` manual, el browser lo
  fija con el boundary correcto).
- `Tarjetas.tsx`: cada tarjeta del listado agrega un botón "Importar
  resumen" con un `<input type="file" accept="application/pdf">`
  oculto. Al seleccionar un archivo, se sube de inmediato (sin ningún
  diálogo de confirmación previo, REQ-007) y se muestra el resultado en
  un `Alert`/`Snackbar`: "Resumen importado: N gastos creados (X en
  cuotas, Y vinculados a suscripciones)." Si falla (422/400), muestra el
  mensaje de error tal cual devuelve la API. Tras una importación
  exitosa, se refresca el listado de tarjetas (para ver el nuevo
  cierre/vencimiento).

## Design Rationale
Sin pantalla de revisión previa — coherente con REQ-007 (importación
100% automática, decisión explícita del usuario).

## Dependencies
T3 (`POST .../resumen`).

## Done When
- [ ] TC-010 pasa.
- [ ] `npm run build`/`npm run lint` sin errores.

## Interfaces Produced
Ninguna (consumidor final).

## Interfaces Consumed
- T3: `ResumenImportadoOut`.

## Standalone Verifiable
Sí.
