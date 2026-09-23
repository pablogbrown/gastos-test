# T4 — Componente `LottieAvatar` + `avatarClient.ts`

## Scope
- `package.json` (edit: agregar `lottie-react`, ver spec.md D-01)
- `src/frontend/components/LottieAvatar.tsx` (nuevo)
- `src/frontend/api/avatarClient.ts` (nuevo)
- `tests/unit/frontend/LottieAvatar.test.tsx` (nuevo)

## Changes
- `npm install lottie-react` (dependencia nueva, decisión ya tomada en spec.md D-01).
- `LottieAvatar` — `{ src: string; loop?: boolean; className?: string }`: envuelve `<Lottie animationData={...} loop={loop ?? true} />` de `lottie-react`, resolviendo `src` (URL o path) a los datos de animación (fetch si es URL remota, import si es un asset local del bundle — decidir en implementación según el shape real de las URLs sembradas en T2). Puramente presentacional — sin imports de `src/frontend/api/*`.
- `avatarClient.ts` — funciones delgadas (mismo patrón que el resto de `src/frontend/api/*`) para los 4 endpoints de T3: `listarAvataresDisponibles`, `obtenerAvatarSeleccionado`, `seleccionarAvatar`, `obtenerCreditos`.

## Implementation Steps
1. Instalar `lottie-react` y confirmar que `npm run build` sigue verde.
2. RED: escribir `LottieAvatar.test.tsx` con TC-009.
3. GREEN: implementar `LottieAvatar` y `avatarClient.ts`.
4. Confirmar que `LottieAvatar` no importa nada de `src/frontend/api/*` (constraint de la spec).

## Design Rationale
Mismo patrón ya establecido para clientes de API delgados (`gastosClient.ts`, etc.) y componentes presentacionales puros (`PageHeader`/`StatCard`/`EmptyState`) — ninguna decisión nueva de arquitectura, solo aplicar los patrones existentes al nuevo dominio.

## Dependencies
T3 (los endpoints que `avatarClient.ts` consume deben existir).

## Done When
- [ ] TC-009 pasa.
- [ ] `npm run build` compila con `lottie-react` instalado.
- [ ] `LottieAvatar` no importa `src/frontend/api/*`.

## Interfaces Produced
- `LottieAvatar(props: LottieAvatarProps) => JSX.Element`.

## Standalone Verifiable
Sí para `LottieAvatar` (test con una URL sintética); `avatarClient.ts` requiere T3 real para probarse contra el backend, pero su propio test unitario puede mockear `fetch`.
