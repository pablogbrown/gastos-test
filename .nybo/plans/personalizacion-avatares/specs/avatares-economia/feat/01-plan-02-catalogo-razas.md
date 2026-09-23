# T2 — Catálogo `AvatarPersonaje` + seed

## Scope
- `src/db/models/avatar_personaje.py` (nuevo)
- `src/db/migrate.py`, `src/db/migrations/0022_avatar_catalogo.py` (nuevo)
- `src/services/avatar_service.py` (edit: agrega `listar_catalogo`)
- `tests/integration/services/avatar_catalogo.test.py` (nuevo)

## Changes

**Data Layer:**
- `AvatarPersonaje`: `id` (GUID PK), `especie` (string: `"perro"`|`"gato"`), `raza` (string), `lottie_url` (string — URL o path del asset, reemplazable sin tocar código), `nivel_requerido` (string, uno de `ranking_service.NIVELES`'s nombres — `"Novato"`/`"Activo"`/`"Comprometido"`/`"Campeón de la casa"`), `rareza` (string: `"común"`|`"raro"`|`"épico"`|`"legendario"`), `disponible_desde`/`disponible_hasta` (`Date`, nullable — `NULL` = sin límite).
- Migración `0022_avatar_catalogo.py`: crea la tabla y siembra el catálogo inicial — curar 8-10 filas desde LottieFiles' "Animals Lottie Animations Pack" (licencia Simple License, uso comercial sin atribución), distribuidas en los 4 niveles (2-3 razas por nivel) y variando rareza. Registrar en un comentario de la migración la fuente y licencia de cada `lottie_url` usada.

**Service Logic:**
- `avatar_service.listar_catalogo(session, miembro_id) -> list[AvatarPersonaje]`: devuelve toda raza con `disponible_desde`/`disponible_hasta` cubriendo hoy (o sin límite), MÁS cualquier raza fuera de ventana que `miembro_id` ya tenga seleccionada (join contra `MiembroAvatarSeleccionado`, ver T3 — en esta task, si la tabla de selección todavía no existe, dejar el join preparado pero condicional/no-op hasta que T3 la cree; confirmar en T3 que esta función queda completa).

## Implementation Steps
1. RED: escribir `avatar_catalogo.test.py` con TC-003 (catálogo expone los campos esperados) y TC-004 (raza fuera de ventana no aparece).
2. GREEN: implementar el modelo, la migración con el seed curado, y `listar_catalogo`.
3. Documentar en un comentario de la migración: fuente exacta del pack Lottie usado y su licencia, para que reemplazar un asset después no pierda esa trazabilidad.

## Design Rationale
El campo `lottie_url` como texto plano (no un enum ni un asset embebido) es lo que permite reemplazar cualquier animación por una hecha a medida después sin tocar código ni migrar de nuevo — decisión explícita del usuario, ver spec.md Sources.

## Dependencies
Ninguna — corre en paralelo a T1.

## Done When
- [ ] TC-003, TC-004 pasan.
- [ ] El seed inserta al menos una raza por cada uno de los 4 niveles.
- [ ] Cada fila sembrada tiene un `lottie_url` real (verificable, de una fuente con licencia comercial libre).

## Interfaces Produced
- `listar_catalogo(session, miembro_id) -> list[AvatarPersonaje]`.

## Standalone Verifiable
Sí — el catálogo y su filtro de disponibilidad se verifican sin depender de selección (T3) ni créditos (T1).
