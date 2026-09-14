# Progress — Resolver el rol real del Usuario en la casa

## Checklist

### Tasks
- [ ] T1 — `MiembroOut` expone `usuario_id`
- [ ] T2 — `App.tsx` resuelve el rol real del Usuario
- [ ] T3 — `Tareas.tsx` compara el `Miembro.id` propio, no el `Usuario.id` global

### Verify
- [ ] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [ ] `[TC-001]` *[INTEGRATION]* — `MiembroOut` incluye `usuario_id`
- [ ] `[TC-002]` *[UNIT]* — Rol `member` oculta altas/bajas en Miembros
- [ ] `[TC-003]` *[UNIT]* — Rol `admin` muestra los controles correspondientes
- [ ] `[TC-004]` *[UNIT]* — Sin match de `usuario_id` el fallback es `"member"`, nunca `"admin"`
- [ ] `[TC-005]` *[UNIT]* — "Marcar completada" visible para el responsable asignado (Miembro.id correcto)
- [ ] `[TC-006]` *[UNIT]* — "Marcar completada" oculto para un member no-responsable

## Completion Summary
Not yet started.

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-14 | plan | — | — | Spec created — 3 tasks, 6 test cases. Escalado desde un finding de bug (rolUsuarioActual hardcodeado) a `/nybo-plan create` por requerir una decisión real de contrato backend, no un one-line fix. |
