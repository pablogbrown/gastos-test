# T2 — Componentes compartidos

## Scope
- `src/frontend/components/PageHeader.tsx` (nuevo)
- `src/frontend/components/StatCard.tsx` (nuevo)
- `src/frontend/components/EmptyState.tsx` (nuevo)
- `tests/unit/frontend/PageHeader.test.tsx`, `StatCard.test.tsx`, `EmptyState.test.tsx` (nuevos)

## Changes

**`PageHeader`** — `{ title: string; subtitle?: string; action?: { label: string; onClick: () => void; icon?: ReactNode } }`. Renderiza el título como heading (`Typography variant="h5"` o similar), subtítulo opcional, y un `Button`/`IconButton` de acción primaria alineado a la derecha si `action` está presente.

**`StatCard`** — `{ icon?: ReactNode; label: string; value: string; color?: "default"|"success"|"warning"|"error" }`. Tarjeta compacta (usa el `Card` ya restyled por T1) con el valor en tipografía destacada (mayor peso/tamaño que la etiqueta) y color opcional según el semántico del tema.

**`EmptyState`** — `{ icon?: ReactNode; message: string; action?: { label: string; onClick: () => void } }`. Ícono centrado, mensaje, y botón de acción opcional (p.ej. "Agregar el primero").

Los 3 son puramente presentacionales — **ningún import de `src/frontend/api/*`** (constraint de la spec).

## Implementation Steps
1. Crear el directorio `src/frontend/components/` si no existe.
2. Implementar `PageHeader.tsx` con su interfaz de props documentada.
3. Implementar `StatCard.tsx`.
4. Implementar `EmptyState.tsx`.
5. Un test por componente, consultando por rol/label accesible (convención de dominio ya establecida).

## Design Rationale
Single Responsibility — cada componente resuelve exactamente un patrón visual repetido (encabezado, estadística, estado vacío) que hoy cada pantalla reimplementa a mano de forma inconsistente. Mantenerlos sin dependencias de API es lo que permite que T4 (Inicio) y las 3 specs siguientes los reutilicen sin acoplamiento.

## Dependencies
T1 (consume el tema restyled para que sus `Card`/`Typography` hereden la nueva identidad visual).

## Done When
- [ ] Los 3 componentes existen con props tipadas.
- [ ] TC-003, TC-004, TC-005 pasan.
- [ ] Ninguno importa `src/frontend/api/*`.

## Interfaces Produced
- `PageHeader` — `(props: PageHeaderProps) => JSX.Element`.
- `StatCard` — `(props: StatCardProps) => JSX.Element`.
- `EmptyState` — `(props: EmptyStateProps) => JSX.Element`.

## Standalone Verifiable
Sí — cada componente se testea de forma aislada con props sintéticas.
