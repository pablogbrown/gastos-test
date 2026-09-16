# T4 — `Prestamos.tsx` muestra el estado y las acciones de confirmación

## Scope
- `src/frontend/api/prestamosClient.ts`
- `src/frontend/pages/Prestamos.tsx`
- `src/frontend/App.tsx`
- `tests/unit/frontend/Prestamos.test.tsx`

## Changes
- `prestamosClient.ts`: `Prestamo` agrega `confirmado_prestamista:
  boolean | null`, `confirmado_deudor: boolean | null`,
  `estado_confirmacion: string`; nueva función `confirmarPrestamo(casaId,
  prestamoId, confirma: boolean): Promise<Prestamo>` (PATCH a
  `.../confirmacion`).
- `Prestamos.tsx`: agrega prop `miembroIdActual: string` (mismo patrón
  que `Tareas.tsx`). Por cada fila:
  - `estado_confirmacion === "pendiente_confirmacion"`: si
    `miembroIdActual` es la parte a la que le toca confirmar (
    `miembroIdActual === prestamista_id && confirmado_prestamista ===
    null`, o el equivalente para deudor), mostrar dos botones
    "Confirmar"/"Rechazar" en vez del chip de estado (TC-009); para
    cualquier otro miembro, mostrar un `Chip` "Pendiente de
    confirmación" sin acciones (TC-008).
  - `estado_confirmacion === "rechazado"`: `Chip` "Rechazado" (color
    `error`), sin acciones.
  - `estado_confirmacion === "confirmado"`: comportamiento actual sin
    cambios — el chip clickeable pagado/pendiente.
- `App.tsx`: pasar `miembroIdActual={miMiembro?.id ?? ""}` a
  `<Prestamos>` (mismo valor ya calculado para `<Tareas>`).

## Design Rationale
Mismo patrón ya usado por `Tareas.tsx` para "esta acción me toca a mí
específicamente" (`miembroIdActual`) — evita introducir un segundo
mecanismo de identidad en el frontend.

## Dependencies
T3 (`estado_confirmacion`, endpoint de confirmación).

## Done When
- [ ] TC-008 y TC-009 pasan.
- [ ] `npm run build`/`npm run lint` sin errores.

## Interfaces Produced
Ninguna (consumidor final).

## Interfaces Consumed
- T3: `PrestamoOut.estado_confirmacion`, `PATCH .../confirmacion`.

## Standalone Verifiable
Sí.
