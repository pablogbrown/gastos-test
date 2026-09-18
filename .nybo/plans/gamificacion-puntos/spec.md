# Spec: gamificacion-puntos

## Feature
gamificacion-puntos

### What
Suma cuatro mecánicas de gamificación sobre el sistema de puntos ya
existente (`HistorialTarea`), además del ranking simple actual:
niveles, rachas, ranking por mes, logros desbloqueables, y una meta de
puntos mensual compartida por toda la casa.

### Why
El usuario quiere más razones para que la casa use el sistema de
puntos día a día, no solo un ranking histórico que una vez ganado
queda fijo para siempre.

## Solution
Todo se deriva del mismo `HistorialTarea` append-only ya existente —
ninguna mecánica requiere tocar cómo se registran los puntos al
completar una tarea, salvo el hook de logros (que solo LEE el estado
resultante, nunca cambia el puntaje). Dos piezas sí necesitan
persistencia nueva: `LogroObtenido` (qué logro desbloqueó cada
miembro, y cuándo) y `Casa.meta_puntos_mensual` (la meta configurada,
si existe).

- **Niveles**: función pura sobre el total de puntos de un miembro —
  4 escalones fijos (Novato/Activo/Comprometido/Campeón de la casa).
- **Rachas**: días consecutivos (calendario) con al menos una tarea
  completada, por miembro — calculado sobre `HistorialTarea.
  completada_en`, sin tabla nueva.
- **Ranking por mes**: `calcular_ranking` gana un parámetro opcional
  `mes` — sin él, se comporta exactamente igual que hoy (REQ-003,
  regresión: `dashboard_service.armar_dashboard` sigue sin pasarlo).
- **Logros**: catálogo fijo en código (cantidad de tareas completadas,
  puntos totales, racha) evaluado después de completar una tarea;
  cada desbloqueo se persiste una sola vez por miembro.
- **Meta de la casa**: un Administrador configura un objetivo mensual
  de puntos para toda la casa; Inicio muestra el progreso acumulado
  del mes contra esa meta.

## Requirements

- REQ-001: Cada miembro tiene un nivel derivado de su total de puntos
  histórico, en 4 escalones (Novato / Activo / Comprometido / Campeón
  de la casa).
- REQ-002: Cada miembro tiene una racha — cantidad de días
  consecutivos (terminando hoy o ayer) con al menos una tarea
  completada.
- REQ-003: El ranking se puede consultar filtrado por mes, además del
  histórico total ya existente — sin cambiar el comportamiento de
  ningún caller que no pase `mes` explícitamente.
- REQ-004: Un catálogo fijo de logros (por cantidad de tareas
  completadas, puntos totales acumulados, y días de racha) se
  desbloquea automáticamente al completar una tarea, una sola vez por
  miembro y logro.
- REQ-005: Un Administrador puede configurar una meta de puntos
  mensual para la casa; la pantalla de Inicio muestra el progreso
  acumulado de todos los miembros ese mes contra esa meta, cuando está
  configurada.

## Test Cases

- TC-001 (REQ-001): un miembro con 0 puntos es "Novato"; cruzar cada
  umbral (50/150/300) lo sube de nivel.
- TC-002 (REQ-002): completar tareas en días consecutivos acumula
  racha; un día sin ninguna tarea completada la reinicia a 0.
- TC-003 (REQ-002): completar más de una tarea el mismo día cuenta
  como un solo día de racha, no la incrementa dos veces.
- TC-004 (REQ-003): `calcular_ranking(casa_id, mes="2026-09")` solo
  cuenta puntos de tareas completadas ese mes; sin `mes`, el resultado
  es idéntico al comportamiento actual (regresión de
  `dashboard_service`).
- TC-005 (REQ-004): completar la primera tarea desbloquea el logro
  correspondiente; cruzar un umbral de puntos o de racha desbloquea el
  logro asociado exactamente una vez, nunca duplicado.
- TC-006 (REQ-005): un Administrador puede configurar la meta; un
  miembro no-admin no puede. El progreso mostrado (suma de puntos de
  todos los miembros ese mes) coincide con lo esperado.
- TC-007 (frontend, REQ-001/REQ-002/REQ-003/REQ-004): Ranking muestra
  el selector de mes, el nivel y la racha de cada miembro, y sus
  logros desbloqueados.
- TC-008 (frontend, REQ-005): Inicio muestra la meta de la casa con
  barra de progreso solo cuando está configurada; Miembros permite a
  un Administrador editarla.

## Dependencies
Ninguna nueva (reusa `HistorialTarea`/`Miembro`/`Casa` ya existentes).

## Out of Scope
- Recompensas canjeables (premios reales por puntos).
- Logros configurables por el usuario (el catálogo es fijo en código).
- Rachas o metas por equipo/sub-grupo dentro de la casa.
- Notificaciones push al desbloquear un logro o romper una racha.
