# Avatares y economía de créditos - Technical Specification

| | |
| --- | --- |
| Progress | [progress.md](progress.md) |

## Intention

### What
Un miembro gana **créditos** (moneda de personalización, distinta de los puntos de ranking) al completar tareas, y puede elegir una **raza de avatar animado** (perro o gato, reproducido vía Lottie) entre las que su nivel actual (Novato/Activo/Comprometido/Campeón, ya existente) tiene desbloqueadas.

### Why
El usuario quiere una "buena dosis de personalización" en los perfiles — hoy cada miembro es solo un ícono con su inicial. Esta spec construye la fundación (economía + catálogo + selección) sobre la que la tienda de accesorios (`tienda-accesorios`) y la integración visual (`perfil-avatar-ui`) se apoyan.

## Outcome
Al completar una tarea, un miembro ve su saldo de créditos crecer igual que sus puntos. En una pantalla de selección (construida en `perfil-avatar-ui`), ve las razas de perro/gato ya desbloqueadas por su nivel actual — animadas con Lottie, no estáticas — y puede elegir cuál usar. Una raza de nivel superior aparece bloqueada hasta subir de nivel.

## Requirements

### REQ-001: Créditos ganados en paralelo a los puntos
Cuando un miembro completa una tarea (`tarea_service.completar_tarea`, ya existente), además de registrar sus puntos en `HistorialTarea`, se registra una transacción de crédito (`CreditoTransaccion`) por el mismo importe, a nombre del beneficiario de la tarea — nunca del actor, si un Administrador la completa en nombre de otro.

- El saldo de créditos de un miembro se deriva sumando sus `CreditoTransaccion` — nunca se guarda un contador redundante en `Miembro`, mismo criterio ya establecido para el ranking de puntos (`ranking_service.calcular_ranking` no usa un contador cacheado).
- Una tarea ya completada no otorga créditos adicionales — mismo gate que ya existe para los puntos (`completar_tarea` rechaza recompletar).

| ID | Given/When/Then | Type |
| --- | --- | --- |
| TC-001 | **Given** una tarea sin completar asignada a un beneficiario **When** se completa **Then** se crea una `CreditoTransaccion` positiva a nombre del beneficiario, por el mismo importe que sus `puntos_obtenidos`. | `[INTEGRATION]` |
| TC-002 | **Given** una tarea ya completada **When** se intenta completar de nuevo **Then** no se crea ninguna `CreditoTransaccion` adicional, igual que hoy no se otorgan puntos adicionales. | `[INTEGRATION]` |

### REQ-002: Catálogo de razas de avatar
Existe un catálogo de razas de avatar (`AvatarPersonaje`) con especie (perro/gato), nombre de raza, un asset Lottie referenciado por URL/path de texto plano, nivel mínimo requerido (uno de los 4 niveles de `ranking_service.NIVELES`), rareza, y una ventana de disponibilidad opcional (`disponible_desde`/`disponible_hasta`) para razas de tiempo limitado a futuro.

- El asset Lottie es un campo de texto (URL/path) — reemplazar la animación real de una raza nunca requiere tocar código, solo ese valor.
- Fuera de su ventana de disponibilidad, una raza no aparece en el catálogo seleccionable para quien todavía no la eligió — pero un miembro que ya la tenía seleccionada la conserva sin verse afectado.

| ID | Given/When/Then | Type |
| --- | --- | --- |
| TC-003 | **Given** el catálogo sembrado con al menos una raza por nivel **When** se lista **Then** cada entrada expone especie, nombre, `nivel_requerido`, rareza, y la URL del asset Lottie. | `[UNIT]` |
| TC-004 | **Given** una raza con `disponible_hasta` en el pasado **When** se lista el catálogo seleccionable para un miembro que nunca la eligió **Then** esa raza no aparece — pero si el miembro consultante ya la tenía seleccionada, sí aparece. | `[UNIT]` |

### REQ-003: Desbloqueo de razas por nivel
Un miembro solo puede seleccionar una raza cuyo `nivel_requerido` sea menor o igual a su nivel actual, derivado en el momento (nunca cacheado) del mismo cálculo que ya usa el ranking (`ranking_service._nivel_de` sobre el total histórico de puntos del miembro) — seleccionar una raza de nivel superior se rechaza.

| ID | Given/When/Then | Type |
| --- | --- | --- |
| TC-005 | **Given** un miembro en nivel "Novato" **When** intenta seleccionar una raza que requiere nivel "Activo" **Then** la operación es rechazada. | `[INTEGRATION]` |
| TC-006 | **Given** un miembro en nivel "Activo" **When** selecciona una raza que requiere "Novato" o "Activo" **Then** la selección se guarda. | `[INTEGRATION]` |

### REQ-004: Selección y cambio de avatar
Un miembro puede cambiar su avatar seleccionado en cualquier momento entre cualquiera de las razas ya desbloqueadas — la selección se persiste (`MiembroAvatarSeleccionado`) y es lo que `perfil-avatar-ui` lee para mostrar el avatar en Miembros/Ranking.

- Sin selección previa, un miembro no tiene avatar (`null`) — no se autoasigna ninguno por defecto, para no generar datos falsos en miembros creados antes de esta feature.

| ID | Given/When/Then | Type |
| --- | --- | --- |
| TC-007 | **Given** un miembro sin selección previa **When** se consulta su avatar **Then** el resultado es `null`. | `[UNIT]` |
| TC-008 | **Given** un miembro con una raza ya seleccionada **When** elige otra raza ya desbloqueada **Then** la nueva selección reemplaza a la anterior. | `[INTEGRATION]` |

### REQ-005: Reproductor Lottie compartido
Existe un componente `LottieAvatar` (`src/frontend/components/`) que reproduce la animación Lottie de una raza a partir de su URL/path de asset, sin conocer nada de la lógica de negocio de avatares/créditos — puramente presentacional, mismo criterio ya establecido para `PageHeader`/`StatCard`/`EmptyState` (`rediseno-ux-ui/sistema-visual`).

| ID | Given/When/Then | Type |
| --- | --- | --- |
| TC-009 | **Given** `<LottieAvatar src="<url>" />` **When** se renderiza **Then** el reproductor Lottie subyacente recibe esa URL como fuente de animación. | `[UNIT]` |

## Constraints
- REQ-001: el hook de créditos vive dentro de `tarea_service.completar_tarea`, después del `commit` que registra `HistorialTarea` — mismo orden ya establecido para `registrar_actividad` (`[SERV-02]`), nunca antes.
- REQ-002/REQ-003: ningún nivel ni umbral se hardcodea de nuevo — reusar `ranking_service.NIVELES`/`_nivel_de` tal cual, nunca duplicar la lista de niveles en `avatar_service.py`.
- REQ-005: `LottieAvatar` no puede importar ningún cliente de `src/frontend/api/*` — mismo criterio de componente puramente presentacional ya establecido (`sistema-visual`, Constraints).
- Ningún archivo de `gamificacion-puntos` (puntos/ranking/logros/meta) se modifica — esta spec solo LEE el nivel ya calculado, nunca cambia cómo se calcula.

## Solution
Se agrega una nueva tabla de transacciones de crédito (ledger, nunca un contador cacheado) enganchada a `completar_tarea`, un catálogo de razas de avatar con desbloqueo por nivel, y un componente Lottie compartido — sin tocar el sistema de puntos/niveles existente.

### Data model

```mermaid
erDiagram
  MIEMBRO ||--o{ CREDITO_TRANSACCION : gana
  MIEMBRO ||--o| MIEMBRO_AVATAR_SELECCIONADO : elige
  AVATAR_PERSONAJE ||--o{ MIEMBRO_AVATAR_SELECCIONADO : es

  CREDITO_TRANSACCION {
    uuid id PK
    uuid casa_id FK
    uuid miembro_id FK
    int cantidad
    string motivo
    datetime creada_en
  }
  AVATAR_PERSONAJE {
    uuid id PK
    string especie
    string raza
    string lottie_url
    string nivel_requerido
    string rareza
    date disponible_desde
    date disponible_hasta
  }
  MIEMBRO_AVATAR_SELECCIONADO {
    uuid miembro_id PK_FK
    uuid avatar_personaje_id FK
    datetime actualizado_en
  }
```

### Contracts

- `POST /casas/{casa_id}/tareas/{tarea_id}/completar` — sin cambio de firma; internamente ahora también crea una `CreditoTransaccion`.
- `GET /miembros/{miembro_id}/creditos` → `{ "saldo": int }`.
- `GET /miembros/{miembro_id}/avatares-disponibles` → lista de `AvatarPersonaje` que ese miembro puede seleccionar hoy (desbloqueadas por nivel, dentro de ventana de disponibilidad o ya elegida).
- `GET /miembros/{miembro_id}/avatar` → `AvatarPersonaje` seleccionado o `null`.
- `PUT /miembros/{miembro_id}/avatar` `{ "avatar_personaje_id": uuid }` → rechaza 403 si la raza no está desbloqueada para ese miembro.

### Open Decisions

#### D-01: Librería de reproducción Lottie en React
- **Opción A — `lottie-react`**: wrapper liviano sobre `lottie-web`, un solo componente `<Lottie animationData=.../>`, mantenida activamente, sin UI de controles propia.
- **Opción B — `@lottiefiles/react-lottie-player`**: player oficial de LottieFiles, más pesado (incluye controles de reproducción que esta feature no necesita).
- **Opción C — `react-lottie`**: paquete más viejo, mantenimiento discontinuo.

**Status:** resuelto automáticamente (nivel de confianza semi-autonomous, sin `--discuss`).
- [x] A — `lottie-react`
- [ ] B — `@lottiefiles/react-lottie-player`
- [ ] C — `react-lottie`

**Rationale:** esta feature solo necesita reproducir una animación en loop, sin controles de usuario — la superficie mínima de A reduce riesgo de bugs de integración y peso de bundle frente a B, y evita el mantenimiento discontinuo de C.

### Task Execution

| Task | File | Description | Dependencies |
| --- | --- | --- | --- |
| T1 | [01-plan-01-creditos.md](feat/01-plan-01-creditos.md) | Ledger de créditos + hook en `completar_tarea` | — |
| T2 | [01-plan-02-catalogo-razas.md](feat/01-plan-02-catalogo-razas.md) | Catálogo `AvatarPersonaje` + seed | — |
| T3 | [01-plan-03-seleccion-avatar.md](feat/01-plan-03-seleccion-avatar.md) | Desbloqueo por nivel + selección + endpoints | T1, T2 |
| T4 | [01-plan-04-lottie-avatar.md](feat/01-plan-04-lottie-avatar.md) | Componente `LottieAvatar` + `avatarClient.ts` | T3 |

### Verification

| Task | Test cases | Additional gate criteria |
| --- | --- | --- |
| T1 | TC-001, TC-002 | `[AUTO]` `.venv/bin/python3 -m pytest tests/integration/services/creditos.test.py`. |
| T2 | TC-003, TC-004 | `[AUTO]` migración corre limpia sobre una base vacía; seed inserta al menos una raza por nivel. |
| T3 | TC-005, TC-006, TC-007, TC-008 | `[AUTO]` `.venv/bin/python3 -m pytest tests/integration/services/avatar_seleccion.test.py`. |
| T4 | TC-009 | `[AUTO]` `npm run build` compila con `lottie-react` agregado a `package.json`; `npm run test` verde. |

#### Outcome Smoke Test
1. Completar una tarea como un miembro; confirmar que su saldo de créditos (`GET /miembros/{id}/creditos`) sube en el mismo importe que sus puntos.
2. Con un miembro Novato, confirmar que solo las razas de nivel Novato aparecen en `avatares-disponibles`.
3. Subir de nivel a ese miembro (completando más tareas) y confirmar que nuevas razas aparecen desbloqueadas.
4. Seleccionar una raza desbloqueada y confirmar que `GET /miembros/{id}/avatar` la devuelve.
5. Gate final: los 4 test suites en verde, `npm run build`/`pytest` sin errores.

## Sources

| Type | Reference | Detail |
| --- | --- | --- |
| Session | Captured from this conversation on 2026-09-23 | El usuario pidió personalización de perfiles con avatares animados de animales; decisiones de técnica/economía/progresión/alcance/assets confirmadas vía preguntas dirigidas antes de planificar. |
| Spec | gamificacion-puntos | .nybo/plans/gamificacion-puntos/spec.md — define `NIVELES`/`_nivel_de` que esta spec reutiliza sin duplicar. |
| Spec | rediseno-ux-ui/sistema-visual | .nybo/plans/rediseno-ux-ui/specs/sistema-visual/spec.md — precedente de componente presentacional puro (`PageHeader`/`StatCard`/`EmptyState`) que `LottieAvatar` sigue. |

## History

| # | Date | Event | Verdict | Summary |
| --- | --- | --- | --- | --- |
| 1 | 2026-09-23 | plan | — | Spec created — 4 tasks, 9 test cases. |
