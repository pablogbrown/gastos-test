# T1 — Registrar actividad en alta y baja de miembro

## Scope
- `src/db/models/historial_actividad.py` — agregar `MIEMBRO_DESACTIVADO = "miembro_desactivado"` al enum.
- `src/services/miembro_service.py` — `agregar_miembro`/`desactivar_miembro`: llamar `registrar_actividad` tras el `commit` exitoso.
- `tests/integration/api/miembro_historial_actividad.test.py` (nuevo) — TC-001, TC-002, TC-003.

## Changes
**Data Layer**
- `TipoActividadEnum`: agregar `MIEMBRO_DESACTIVADO = "miembro_desactivado"`.

**Service Logic**
- `agregar_miembro`: después de `session.refresh(miembro)` y antes del
  `return`, llamar
  `registrar_actividad(casa_id, TipoActividadEnum.MIEMBRO_AGREGADO, miembro.id, f"{miembro.nombre} fue agregado a la casa.")`.
- `desactivar_miembro`: después de `session.refresh(miembro)` y antes del
  `return`, llamar
  `registrar_actividad(casa_id, TipoActividadEnum.MIEMBRO_DESACTIVADO, miembro.id, f"{miembro.nombre} fue desactivado.")`.
- Import `registrar_actividad` y `TipoActividadEnum` en
  `miembro_service.py` (mismo import que ya usan `gasto_service.py`/
  `tarea_service.py`).

## Design Rationale
Mismo patrón exacto que `gasto_service.registrar_gasto`/
`tarea_service.crear_tarea` — un hook llamado una vez, después de que la
transacción de negocio ya confirmó, nunca antes (evita registrar un
evento que en definitiva no ocurrió si algo falla después). No se
introduce abstracción nueva: se reutiliza el hook existente tal cual.

## Dependencies
Ninguna — independiente del fix de membresía duplicada (spec separada);
toca el mismo archivo (`miembro_service.py`) pero una región de código
distinta (el final de cada función, no la validación de entrada).

## Done When
- [x] TC-001, TC-002, TC-003 pasan.
- [x] `pytest tests/` completo sigue en verde.

## Interfaces Produced
- `TipoActividadEnum.MIEMBRO_DESACTIVADO` — `{name: "MIEMBRO_DESACTIVADO", signature: "str enum member", kind: "export"}`

## Standalone Verifiable
Sí — TC-001/002/003 verifican este cambio completo vía la API, sin
depender del frontend.
