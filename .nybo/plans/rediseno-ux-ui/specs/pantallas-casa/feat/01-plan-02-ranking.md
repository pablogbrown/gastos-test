# T2 — Ranking con progreso visual

## Scope
- `src/frontend/pages/Ranking.tsx`

## Changes
- Encabezado vía `PageHeader` (incluye el selector de mes ya existente de `gamificacion-puntos`).
- Nivel: barra o indicador de progreso (`LinearProgress` o equivalente) mostrando la posición del miembro entre su nivel actual y el próximo umbral, en vez de solo el nombre del nivel en texto.
- Racha: ícono (p.ej. de fuego/llama) + número de días consecutivos, en vez de "Racha: N días" en texto plano.
- Logros: cada logro desbloqueado como chip/badge individual (reutilizando `NOMBRES_LOGRO`, convención `FRONP-03` ya establecida) en vez de una lista de texto separada por comas.
- Meta de la casa (si está configurada): barra de progreso agregada de todos los miembros del mes.

## Implementation Steps
1. Baseline: confirmar `Ranking.test.tsx` en verde.
2. Reemplazar encabezado por `PageHeader`, preservando el selector de mes.
3. Agregar indicador de progreso de nivel.
4. Agregar ícono+número de racha.
5. Reconstruir logros como chips individuales.
6. Re-correr el suite sin modificar queries.

## Design Rationale
Esta pantalla es la que más pierde por falta de jerarquía visual hoy — la gamificación de `gamificacion-puntos` (niveles/rachas/logros) fue pensada para motivar, pero como texto plano no logra ese efecto. Es el ejemplo más directo del feedback "viejo, poco atractivo" del usuario.

## Dependencies
Ninguna dentro de esta spec.

## Done When
- [ ] TC-003, TC-004, TC-007 pasan.
- [ ] `Ranking.test.tsx` en verde, queries sin modificar.

## Interfaces Produced
Ninguna.

## Standalone Verifiable
Sí.
