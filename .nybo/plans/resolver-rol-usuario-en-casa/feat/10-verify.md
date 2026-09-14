# Verify — Resolver el rol real del Usuario en la casa

## T1 — `MiembroOut` expone `usuario_id`

### Test Scenarios
- Happy path: `GET /casas/{id}/miembros` incluye `usuario_id` en cada objeto (TC-001).

### Gate Criteria
- `[AUTO]` TC-001 en verde.
- `[AUTO]` Suite completa de `pytest tests/` sigue en verde — ningún consumidor existente asume una forma cerrada del objeto.

## T2 — `App.tsx` resuelve el rol real

### Test Scenarios
- Happy path: mi propio `Miembro` tiene `rol: "member"` → `Miembros` oculta altas/bajas (TC-002).
- Happy path: mi propio `Miembro` tiene `rol: "admin"` → controles visibles (TC-003).
- Edge: `miembros` aún no incluye mi propia fila (carga en curso) → fallback seguro a `"member"` (TC-004).

### Gate Criteria
- `[AUTO]` TC-002, TC-003, TC-004 en verde.
- `[AUTO]` `npm run build` sin errores de tipos.

## T3 — `puedeCompletar` usa el `Miembro.id` correcto

### Test Scenarios
- Happy path: tarea asignada a mi propio `Miembro.id` → "Marcar completada" visible (TC-005).
- Edge: tarea asignada al `Miembro.id` de otro, rol `member` → botón oculto (TC-006).

### Gate Criteria
- `[AUTO]` TC-005, TC-006 en verde.
- `[AUTO]` Los 3 tests preexistentes de `puedeCompletar` (sin responsable, responsable propio, responsable ajeno) siguen en verde con el nombre de prop nuevo.

## End-to-End Verification
1. `pytest tests/` y `npm run test -- --run` en verde.
2. `npm run build` sin errores.
3. Smoke manual contra el docker-compose local: loguear como member (`Pablo`) → NO ver "Agregar miembro"/"Desactivar" en Miembros; loguear como admin → sí verlos. Asignar una tarea a un member y loguear como ese member → "Marcar completada" visible solo en esa tarea, no en las de otros.
4. Repetir el escenario del incidente original (member intentando desactivar admin) → el botón "Desactivar" ya ni siquiera se muestra para un member, cerrando la vía de UI hacia ese intento (el backend ya lo rechazaba; ahora la UI tampoco lo ofrece).

## Failure Triage

| If TC-XXX fails | Check first | Root cause pattern |
|---|---|---|
| TC-001 | ¿`MiembroOut` realmente declara el campo, o solo el modelo ORM lo tiene? | Campo agregado al modelo pero no al schema Pydantic de respuesta |
| TC-002/003/004 | ¿La comparación usa `===` sobre strings, o mezcla `string`/`UUID`? | `usuario_id` del backend es UUID serializado a string; comparar contra un objeto no-string nunca matchea |
| TC-005/006 | ¿`App.tsx` pasa `miMiembro?.id`, no `miMiembro?.usuario_id`? | Confundir cuál de los dos ids corresponde a "mi Miembro en esta casa" vs. "mi Usuario global" — exactamente el bug original |
