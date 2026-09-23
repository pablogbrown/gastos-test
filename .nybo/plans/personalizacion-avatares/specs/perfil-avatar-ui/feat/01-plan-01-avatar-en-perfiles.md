# T1 — Avatar+accesorios en Miembros/Ranking

## Scope
- `src/frontend/pages/Miembros.tsx`
- `src/frontend/pages/Ranking.tsx`

## Changes
- Ambas pantallas: en el lugar donde hoy renderizan `Avatar` con la inicial del miembro, consultar `avatarClient.obtenerAvatarSeleccionado(miembroId)` (de `avatares-economia`) — si devuelve una raza, renderizar `LottieAvatar` con su `lottie_url`, superponiendo (overlay simple, badges/íconos posicionados encima, nunca integrados a la animación) los accesorios equipados actuales del miembro (`tiendaClient.listarInventario`/equivalente de equipados). Si devuelve `null`, mantener el `Avatar` con inicial exactamente como está hoy.

## Implementation Steps
1. Baseline: confirmar `Miembros.test.tsx`/`Ranking.test.tsx` en verde.
2. Reemplazar el `Avatar` por la lógica condicional `LottieAvatar` vs. respaldo, en Miembros.
3. Repetir en Ranking.
4. Agregar los overlays de accesorios equipados (posicionamiento simple, ej. `position: absolute` sobre el `LottieAvatar`).
5. Re-correr ambos suites — agregar los casos nuevos (TC-001/002/003) sin modificar las queries preexistentes que no dependen del avatar.

## Design Rationale
El respaldo a `Avatar`+inicial para un miembro sin selección (dato preexistente) evita que esta feature rompa cualquier casa que ya tenía miembros antes de que esta feature existiera — mismo principio de "cero regresión" ya aplicado en cada spec de este proyecto.

## Dependencies
Ninguna dentro de esta spec — consume `avatarClient`/`LottieAvatar` de `avatares-economia` y el inventario/equipados de `tienda-accesorios`, ambas ya construidas.

## Done When
- [ ] TC-001, TC-002, TC-003 pasan.
- [ ] `Miembros.test.tsx` y `Ranking.test.tsx` en verde.

## Interfaces Produced
Ninguna.

## Standalone Verifiable
Sí — depende solo de interfaces ya construidas y estables de las 2 specs anteriores.
