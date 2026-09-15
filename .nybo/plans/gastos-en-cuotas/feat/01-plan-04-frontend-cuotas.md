# T4 — `Gastos.tsx` ofrece cargar en cuotas

## Scope
- `src/frontend/api/gastosClient.ts` — `NuevoGasto`/`registrarGasto`.
- `src/frontend/pages/Gastos.tsx` — formulario "Nuevo gasto".
- `tests/unit/frontend/Gastos.test.tsx` — TC-007.

## Changes
**UI**
- `NuevoGasto`: agregar `cuotas?: number`.
- `registrarGasto`: incluir `cuotas: gasto.cuotas` en el body enviado
  (`JSON.stringify` omite la clave si es `undefined`, mismo patrón ya
  usado por `pagadoPor`/`participantes`).
- `Gastos.tsx`: nuevo `TextField type="number"` "Cuotas (opcional)"
  junto a los campos existentes del formulario. Estado `cuotas: string`
  (mismo patrón que `puntos` en `Tareas.tsx`); al enviar,
  `cuotas: cuotas === "" ? undefined : Number(cuotas)` — mismo criterio
  ya aplicado en el fix `fix-validacion-puntos-tarea` para no convertir
  "vacío" en `1`/`0` accidentalmente.
- Ayuda visual: si `cuotas` tiene un valor ≥ 2, mostrar un texto de
  ayuda breve (ej. "Se van a crear 3 gastos, uno por mes").

## Design Rationale
Mismo patrón de conversión "vacío → undefined, nunca 0/1 por
default" ya establecido en `fix-validacion-puntos-tarea` — reutilizar
la convención en vez de reinventar otra forma de manejar un campo
numérico opcional.

## Dependencies
T3 — necesita que el backend acepte `cuotas` en el body.

## Done When
- [ ] TC-007 pasa.
- [ ] `npm run build` sin errores de tipos.
- [ ] `npm run test -- --run` completo sigue en verde.

## Interfaces Produced
Ninguna nueva.

## Standalone Verifiable
Sí — TC-007 verifica el body enviado por el formulario con un mock de
`fetch`, sin depender del backend real.
