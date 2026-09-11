# Task 2 — Service Layer: Casas, Miembros y Roles

## Scope
- `src/services/casa_service.py`
- `src/services/miembro_service.py`
- `src/services/permisos.py`

## Changes
### Service Logic
- `crear_casa(nombre, usuario_creador)`: valida nombre no vacío (TC-002), crea Casa, crea Miembro inicial con rol `admin` (REQ-001).
- `agregar_miembro(casa_id, nombre, identificacion, actor)`: valida que `actor` sea admin de la casa (TC-006), valida unicidad de identificación (TC-004), crea Miembro con rol `member`.
- `desactivar_miembro(casa_id, miembro_id, actor)`: valida rol admin, marca `activo=false` sin tocar registros de gastos/tareas asociados (TC-005).
- `permisos.puede(rol, accion)`: tabla de permisos por rol (REQ-004) usada como guard en cada servicio y en las rutas de gastos/tareas de las specs dependientes.
- Guard transversal `requiere_membresia_activa(casa_id, usuario_id)` reutilizable por las specs de gastos y tareas para cumplir REQ-005.

## Design Rationale
Los checks de permisos viven en la capa de servicio (no en la UI ni en la ruta) para que cualquier consumidor futuro de la API quede protegido igual — cumple OCP: agregar un permiso nuevo no obliga a tocar cada ruta.

## Dependencies
T1 (modelos Casa/Miembro).

## Done When
- [ ] TC-001, TC-002, TC-003, TC-004, TC-005, TC-006, TC-007, TC-008, TC-009 pasan.
- [ ] `permisos.puede` cubre las acciones listadas en REQ-004 para ambos roles.
- [ ] Build y tipos compilan.

## Interfaces Produced
- `{name: "crear_casa", signature: "(nombre: str, usuario_creador: UUID) -> Casa", kind: "function"}`
- `{name: "agregar_miembro", signature: "(casa_id: UUID, nombre: str, identificacion: str, actor: UUID) -> Miembro", kind: "function"}`
- `{name: "desactivar_miembro", signature: "(casa_id: UUID, miembro_id: UUID, actor: UUID) -> Miembro", kind: "function"}`
- `{name: "requiere_membresia_activa", signature: "(casa_id: UUID, usuario_id: UUID) -> bool", kind: "function"}`

## Standalone Verifiable
Sí, con la base de datos de T1 disponible.
