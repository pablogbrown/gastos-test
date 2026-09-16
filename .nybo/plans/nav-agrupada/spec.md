# Menú superior agrupado por categoría

## Intention

### What
El menú de navegación superior (desktop) pasa de 9 pestañas sueltas a 4
elementos de primer nivel: **Inicio** (suelta), **Casa** (Miembros,
Ranking, Actividad), **Gastos** (Gastos, Balance, Tarjetas,
Suscripciones) y **Tareas** (suelta). Los grupos despliegan un menú al
hacer clic. La navegación mobile (barra inferior) no cambia.

### Why
Con 9 pestañas sueltas, el menú superior ya no entra cómodo y mezcla
conceptos de nivel distinto (una pantalla de "casa" al lado de una de
"gastos" al lado de "tareas") — agruparlas por tema hace más fácil
encontrar cada pantalla.

## Solution
`AppNav.tsx` agrega una estructura de agrupación (`Pantalla` → grupo:
`"casa"` | `"gastos"` | `None` para las sueltas). En desktop, en vez de
`Tabs` planas, se renderizan 4 botones de primer nivel: "Inicio" y
"Tareas" navegan directo; "Casa" y "Gastos" despliegan un `Menu` con sus
pantallas. El botón de un grupo se resalta como activo si la pantalla
actual pertenece a ese grupo, sin importar cuál de sus pantallas sea. La
barra inferior mobile (`BottomNavigation`) sigue usando `SECCIONES`
(las 9 pantallas planas) sin ningún cambio — el agrupamiento es
exclusivo del menú superior desktop. Ver
**[Solution Overview](feat/00-overview.md)**.

## Outcome
En desktop, el menú muestra "Inicio · Casa · Gastos · Tareas". Estando
en la pantalla Tarjetas, el botón "Gastos" se ve resaltado como grupo
activo; un clic en "Casa" despliega Miembros/Ranking/Actividad.

## Requirements

| ID | Requirement | Business Rules |
|---|---|---|
| REQ-001 | El menú superior desktop muestra 4 elementos de primer nivel: Inicio, Casa, Gastos, Tareas. | "Inicio" y "Tareas" navegan directo (no despliegan menú, cada uno tiene una sola pantalla). |
| REQ-002 | "Casa" despliega Miembros, Ranking y Actividad; "Gastos" despliega Gastos, Balance, Tarjetas y Suscripciones. | Elegir una opción del menú navega a esa pantalla y cierra el menú. |
| REQ-003 | El grupo que contiene la pantalla actual se muestra resaltado como activo. | Aplica aunque la pantalla activa no sea la primera del grupo (ej. estar en Tarjetas resalta "Gastos"). |
| REQ-004 | La navegación mobile (barra inferior) no cambia — sigue mostrando las 9 pantallas sin agrupar. | El agrupamiento es exclusivo del menú superior desktop. |

## Test Cases

| ID | Given/When/Then | Type |
|---|---|---|
| TC-001 (REQ-001) | **Given** un viewport ancho (desktop) **When** se renderiza el menú **Then** muestra exactamente 4 elementos de primer nivel: Inicio, Casa, Gastos, Tareas | `[UNIT]` |
| TC-002 (REQ-002) | **Given** el menú desktop **When** se hace clic en "Casa" **Then** se despliega un menú con Miembros/Ranking/Actividad; elegir "Ranking" llama a `onChange("ranking")` y cierra el menú | `[UNIT]` |
| TC-003 (REQ-002) | **Given** el menú desktop **When** se hace clic en "Gastos" **Then** se despliega un menú con Gastos/Balance/Tarjetas/Suscripciones | `[UNIT]` |
| TC-004 (REQ-003) | **Given** `pantalla="tarjetas"` **When** se renderiza el menú desktop **Then** el botón "Gastos" se muestra como grupo activo | `[UNIT]` |
| TC-005 (REQ-004, control) | **Given** un viewport angosto (mobile) **When** se renderiza el menú **Then** la barra inferior sigue mostrando las 9 pantallas sin agrupar, sin cambios respecto a hoy | `[UNIT]` |

## Sources

| Type | Reference |
|---|---|
| Session | El usuario pidió agrupar el menú superior por tipo (casa/gastos/tareas), adjuntando una captura del menú plano actual — 2026-09-16. Confirmado vía pregunta de aclaración: Inicio suelto, Actividad dentro de "Casa". |
