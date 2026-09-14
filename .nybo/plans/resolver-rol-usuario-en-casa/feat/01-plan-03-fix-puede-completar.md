# T3 — `Tareas.tsx` compara el `Miembro.id` propio, no el `Usuario.id` global

## Scope
- `src/frontend/App.tsx` — pasar el `Miembro.id` propio a `<Tareas>` en vez del `Usuario.id` global.
- `src/frontend/pages/Tareas.tsx` — `TareasProps`/`puedeCompletar`: renombrar y usar el id correcto.
- `tests/unit/frontend/Tareas.test.tsx` — TC-005, TC-006 (actualizar los tests existentes que usan `usuarioId` para pasar un `Miembro.id`, no un `Usuario.id`, como ya vienen naturalmente construidos con UUIDs de ejemplo — sin cambio de intención, solo de nombre).

## Changes
**UI**
- `Tareas.tsx`: renombrar la prop `usuarioId: string` a `miembroIdActual:
  string` en `TareasProps` (con el comentario existente actualizado
  para reflejar que ahora SÍ es el `Miembro.id` correcto, no una
  identidad global) y actualizar `puedeCompletar(tarea, miembroIdActual,
  rol)` para comparar `tarea.responsableId === miembroIdActual`.
- `App.tsx`: en vez de `usuarioId={usuarioId}` (el `Usuario.id` global),
  pasar `miembroIdActual={miMiembro?.id ?? ""}` — reutilizando el
  `miMiembro` ya resuelto en T2.

## Design Rationale
Corrige el bug ya documentado en `.nybo/memory/domains/frontend.md`
(conflación global-Usuario vs. per-casa-Miembro) resolviendo el
`Miembro.id` correcto en el mismo lugar (`App.tsx`) donde T2 ya lo
calcula, en vez de introducir una segunda resolución paralela. El
renombre de la prop (`usuarioId` → `miembroIdActual`) es deliberado: el
nombre anterior invitaba exactamente a este bug.

## Dependencies
T2 — necesita `miMiembro` ya resuelto en `App.tsx`.

## Done When
- [ ] TC-005, TC-006 pasan.
- [ ] Los tests existentes de `Tareas.tsx` que dependían de `usuarioId`
      siguen pasando con el nombre y la semántica nueva (mismos valores
      de ejemplo, ya eran UUIDs de Miembro coincidiendo con
      `responsableId` en los casos que lo requerían).
- [ ] `npm run build` sin errores de tipos.
- [ ] `npm run test -- --run` completo sigue en verde.

## Interfaces Produced
- `TareasProps.miembroIdActual` — reemplaza a `TareasProps.usuarioId` (breaking rename, consumidor único: `App.tsx`, actualizado en el mismo task).

## Standalone Verifiable
Sí — TC-005/006 verifican `puedeCompletar` end-to-end vía render de
`Tareas` con `miembroIdActual` mockeado.
