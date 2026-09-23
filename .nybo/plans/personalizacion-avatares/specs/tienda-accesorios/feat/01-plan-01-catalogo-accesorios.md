# T1 — Catálogo `AccesorioAvatar` + seed + filtro por especie/ventana

## Scope
- `src/db/models/accesorio_avatar.py` (nuevo)
- `src/db/migrate.py`, `src/db/migrations/0024_accesorio_catalogo.py` (nuevo)
- `src/services/tienda_service.py` (nuevo, arranca con `listar_catalogo_accesorios`)
- `tests/integration/services/tienda_catalogo.test.py` (nuevo)

## Changes

**Data Layer:**
- `AccesorioAvatar`: `id` (GUID PK), `nombre` (string), `slot` (string: `"cabeza"`|`"cuello"`|`"cuerpo"`), `rareza` (string, mismos 4 valores que `AvatarPersonaje`), `precio_creditos` (int), `especie_compatible` (string: `"perro"`|`"gato"`|`"ambos"`), `asset_overlay_url` (string, texto plano), `disponible_desde`/`disponible_hasta` (`Date`, nullable).
- Migración `0024_accesorio_catalogo.py`: crea la tabla y siembra 15-20 accesorios distribuidos en los 3 slots, variando rareza y compatibilidad de especie.

**Service Logic:**
- `tienda_service.listar_catalogo_accesorios(session, miembro_id) -> list[AccesorioAvatar]`: consulta `avatar_service.obtener_avatar_seleccionado(session, miembro_id)` (de `avatares-economia`) — si tiene un avatar seleccionado, filtra a `especie_compatible IN (especie_del_avatar, "ambos")`; sin avatar seleccionado, devuelve el catálogo sin filtrar por especie. En ambos casos, excluye ítems fuera de su ventana de disponibilidad salvo que ya estén en el inventario del miembro (la parte de inventario llega en T2 — dejar el join preparado, completar en T2).

## Implementation Steps
1. RED: escribir `tienda_catalogo.test.py` con TC-001, TC-002, TC-009.
2. GREEN: implementar el modelo, la migración con el seed, y `listar_catalogo_accesorios`.
3. Confirmar que la especie de "ambos" nunca queda filtrada por error (aparece siempre, sin importar el avatar del miembro).

## Design Rationale
Mismo criterio de catálogo con ventana de disponibilidad ya establecido en `avatares-economia`'s `AvatarPersonaje` — reutilizar la forma, no reinventarla, para que ambos catálogos se sientan consistentes.

## Dependencies
Ninguna dentro de esta spec — consume `avatar_service.obtener_avatar_seleccionado` de `avatares-economia` (ya construida).

## Done When
- [ ] TC-001, TC-002, TC-009 pasan.
- [ ] El seed cubre los 3 slots y al menos un ítem "ambos".

## Interfaces Produced
- `listar_catalogo_accesorios(session, miembro_id) -> list[AccesorioAvatar]`.

## Standalone Verifiable
Sí — depende solo de una función ya construida y estable de `avatares-economia`.
