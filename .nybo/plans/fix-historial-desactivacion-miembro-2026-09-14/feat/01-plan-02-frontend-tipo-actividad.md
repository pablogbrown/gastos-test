# T2 — Frontend reconoce `miembro_desactivado`

## Scope
- `src/frontend/api/dashboardClient.ts` — `TipoActividad` union type (línea ~18).
- `src/frontend/pages/HistorialActividad.tsx` — `ETIQUETAS_TIPO`, `ICONOS_TIPO`.
- `tests/unit/frontend/HistorialActividad.test.tsx` — TC-004.

## Changes
**UI**
- `dashboardClient.ts`: agregar `"miembro_desactivado"` a la unión
  `TipoActividad` (mismo lugar donde ya está `"miembro_agregado"`).
- `HistorialActividad.tsx`: agregar una entrada `miembro_desactivado` a
  `ETIQUETAS_TIPO` (ej. `"Miembro desactivado"`) y a `ICONOS_TIPO` —
  reutilizar un ícono ya importado en el archivo que transmita la idea
  (ej. `PersonAddIcon` invertido conceptualmente; si no hay uno
  disponible en el import actual, agregar `PersonRemoveIcon` de
  `@mui/icons-material`, ya en el manifiesto de dependencias vía
  `@mui/icons-material`).

## Design Rationale
Ambos `Record<Actividad["tipo"], ...>` son tipados por TypeScript contra
la unión `TipoActividad` — agregar el valor a la unión sin agregar la
entrada correspondiente en ambos `Record` es un error de compilación
(`tsc --noEmit` lo atrapa), no un bug silencioso: T1 y T2 quedan
acoplados por el compilador, no solo por convención.

## Dependencies
T1 — el tipo debe existir en el backend antes de que el frontend lo
declare (aunque el cambio de TypeScript en sí no requiere que el backend
esté corriendo para compilar).

## Done When
- [ ] TC-004 pasa.
- [ ] `npm run build` (`tsc --noEmit` + `vite build`) sin errores.
- [ ] `npm run test -- --run` completo sigue en verde.

## Interfaces Produced
Ninguna nueva — extiende un tipo y dos `Record` ya exportados/usados
internamente en el mismo módulo.

## Standalone Verifiable
Sí — TC-004 renderiza `HistorialActividad` con una entrada mockeada
`tipo: "miembro_desactivado"` sin necesitar el backend real.
