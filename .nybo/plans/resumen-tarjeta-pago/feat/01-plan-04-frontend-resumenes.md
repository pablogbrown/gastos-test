# T4 — UI de resúmenes importados + Pagar resumen en Tarjetas.tsx

## Scope
- `src/frontend/api/tarjetasClient.ts`:
  - `ResumenImportado` gana `resumen_id: string`.
  - Nueva interfaz `Resumen` (`id, tarjeta_id, fecha_cierre, fecha_
    vencimiento, saldo_ars, saldo_usd, gastos_creados, estado,
    importado_en` — mismos campos que `ResumenTarjetaOut`, sin alias
    camelCase salvo los ya existentes en el resto del archivo).
  - Nuevo `listarResumenes(casaId, tarjetaId): Promise<Resumen[]>` →
    `GET .../resumenes`.
  - Nuevo `pagarResumen(casaId, tarjetaId, resumenId): Promise<Resumen>`
    → `PATCH .../resumenes/{resumenId}/pagar`.
- `src/frontend/pages/Tarjetas.tsx`:
  - Por cada card de tarjeta, cargar y mostrar sus resúmenes (llamar
    `listarResumenes` al montar/tras importar/tras pagar) en una lista
    compacta: fecha de cierre, `Chip` de estado ("Pendiente"/"Pagado"),
    y un botón "Pagar resumen" visible solo si `estado === "pendiente"`.
  - El botón llama `pagarResumen` y refresca la lista de resúmenes de
    esa tarjeta al resolver; un error se muestra con el mismo patrón de
    `Alert`/`formatErrorDetail` ya usado en el resto de la pantalla.
  - Tras una importación exitosa, refrescar también la lista de
    resúmenes de esa tarjeta (no solo la tarjeta en sí).

## Dependencies
T3 (necesita los endpoints `GET .../resumenes` y `PATCH .../pagar`).

## Done When
- TC-007, TC-008 pasan en `tests/unit/frontend/Tarjetas.test.tsx`
  (extender el existente): la lista de resúmenes se muestra por
  tarjeta, el botón "Pagar resumen" solo aparece cuando corresponde y
  dispara la llamada correcta, y un 409 de importación duplicada
  muestra el mensaje de error de la API.

## Verifiability
UNIT — `tests/unit/frontend/Tarjetas.test.tsx`.
