# T1 — Estructura de grupos + menú desktop desplegable

## Scope
- `src/frontend/AppNav.tsx`
- `tests/unit/frontend/AppShell.test.tsx` (extiende + actualiza TC-002 existente)

## Changes
- `AppNav.tsx`: agregar `GRUPOS_DESKTOP` (ver `00-overview.md` para la
  forma exacta del tipo) con esta agrupación fija:
  - Suelta: `inicio`.
  - Grupo "Casa": `miembros`, `ranking`, `actividad`.
  - Grupo "Gastos": `gastos`, `balance`, `tarjetas`, `suscripciones`.
  - Suelta: `tareas`.
  - `SECCIONES` (usada por `BottomNavigation`, mobile) NO se toca —
    sigue siendo el array plano de 9 pantallas, sin cambios (REQ-004,
    TC-005).
- Rama desktop de `AppNav` (dentro de `if (esDesktop)`): reemplazar
  `<Tabs>` por una fila de botones construida a partir de
  `GRUPOS_DESKTOP`:
  - Entrada `"suelta"` → un botón (`Tab`/`Button`, lo que mantenga mejor
    el estilo visual actual) que llama `onChange(pantalla)` directo.
  - Entrada `"grupo"` → un botón con `aria-haspopup="menu"` que abre un
    `<Menu anchorEl={...} open={...}>` con un `<MenuItem>` por cada
    pantalla del grupo (ícono + label de `SECCIONES`, reutilizados por
    `value` — no duplicar íconos/labels a mano); elegir un `MenuItem`
    llama `onChange(pantallaElegida)` y cierra el menú (TC-002/TC-003).
    El botón del grupo se marca activo (`variant`/color distinto, mismo
    criterio visual que ya usa `Tabs` para el tab seleccionado) cuando
    `pantalla` está incluida en las pantallas del grupo (TC-004).
- Rama mobile de `AppNav` (`BottomNavigation`): sin ningún cambio.

## Design Rationale
Ver `00-overview.md` — por qué mobile no se agrupa y por qué el clic en
un grupo nunca navega directo.

**Actualizar (no eliminar) el TC-002 existente de `AppShell.test.tsx`**
(spec `ui-modernization`): hoy asume un `tablist` con 9 `tab` directos
en desktop — pasa a verificar los 4 elementos de primer nivel
(Inicio/Casa/Gastos/Tareas) y que abrir "Casa"/"Gastos" expone sus
pantallas como opciones de menú. El TC-001 (mobile) de esa spec queda
intacto, sin tocar una sola línea.

## Dependencies
Ninguna — primera y única tarea.

## Done When
- [ ] TC-001 a TC-005 pasan.
- [ ] El TC-002 original de `ui-modernization` (`AppShell.test.tsx`) queda actualizado y en verde, reflejando el nuevo contrato desktop.
- [ ] `npm run build`/`npm run lint` sin errores.

## Interfaces Produced
- `GRUPOS_DESKTOP` (exportado, por si otra pantalla necesita conocer el agrupamiento en el futuro).

## Standalone Verifiable
Sí.
