---
feature: personalizacion-avatares/specs/tienda-accesorios
schema: build-results/2
cycle: 1
updated: '2026-09-23T20:22:00Z'
exit: ready
verdict: verified
judgment:
  entries: 6
observations:
  entries: 2
tests:
  backend:
    passed: 437
    failed: 0
    skipped: 1
  frontend:
    passed: 183
    failed: 0
build: passed
lint: passed
coverage: unavailable - not configured
---
### Goal

Implementar la spec `tienda-accesorios` (3 tasks): catálogo `AccesorioAvatar`
+ seed + filtro por especie/ventana (T1), inventario + compra que gasta
créditos (T2), equipar/desequipar por slot + endpoints (T3). Depende de
`avatares-economia` (créditos + avatar seleccionado, PR #53, aún no
mergeado a `feat/personalizacion-avatares`) — construida sobre
`feat/personalizacion-avatares--avatares-economia` directamente, en un
worktree aislado, no sobre la rama padre todavía desactualizada. Bloquea
a `perfil-avatar-ui`.

### Judgment

- **J001** (spec-deviation, settled — L2): las 5 rutas se anidan bajo
  `/casas/{casa_id}/miembros/{miembro_id}/accesorios/...`, no el contrato
  literal de spec.md (`/accesorios?miembro_id=...` y
  `/miembros/{miembro_id}/...`, sin `casa_id`) — mismo criterio y misma
  razón ya establecidos por `avatares.py` (`avatares-economia`):
  `resolver_actor_en_casa` exige `casa_id` de la URL, y el proxy de Vite
  solo reenvía `/casas`/`/auth`. El catálogo de compra pasa a
  `GET .../accesorios/catalogo` (antes `GET /accesorios?miembro_id=...`)
  para no colisionar con `GET .../accesorios` (inventario, antes
  `GET /miembros/{miembro_id}/accesorios`).
- **J002** (spec-deviation, settled — L2): POST comprar, PUT equipar y
  DELETE desequipar son self-service (`actor == miembro_id`, 403 si no) —
  spec.md no lo menciona explícitamente para esta spec, pero ninguno de
  REQ-002/REQ-003 nombra un override de Administrador, y es el mismo
  criterio ya aplicado al PUT de selección de avatar en `avatares.py`
  (gastar/equipar el avatar de otro miembro no tiene ningún caso de uso
  declarado).
- **J003** (spec-deviation, settled — L2): `comprar_accesorio` mapea
  `ValidationError` (saldo insuficiente) a 402, no al 400 que usa el
  resto de `ValidationError` en todo el proyecto — spec.md's Contracts lo
  pide explícitamente ("402/ValidationError si saldo insuficiente").
  Documentado como excepción puntual, no una redefinición del mapeo
  general (ver `[APIP-02]`, Curación). "Ya comprado" usa `ConflictError`
  -> 409, ya establecido en el proyecto (mismo tipo que usa
  `tarjetas.py`/`tareas.py`).
- **J004** (spec-deviation, settled — L2): `listar_catalogo_accesorios`
  (T1) NO implementa el join con `MiembroAccesorioComprado` que el propio
  task file de T1/T2 sugiere ("dejar el join preparado, completar en
  T2") — spec.md's TC-010 prueba ese caso contra `listar_inventario`
  ("consulta su inventario"), no contra el catálogo de compra; REQ-004
  dice explícitamente que un ítem fuera de ventana "no aparece en el
  catálogo de compra" sin excepción, y "sigue visible/equipable en el
  INVENTARIO". Con esa lectura, un ítem ya comprado no necesita
  reaparecer en el catálogo de compra (no se puede recomprar, REQ-002 ya
  lo rechaza igual) — implementar sin el join mantiene T1 standalone-
  verifiable (su propia promesa) y evita acoplarlo al modelo de T2 antes
  de tiempo. Las 10 test cases pasan con esta lectura.
- **J005** (spec-deviation, settled — L2): se agregó
  `tests/integration/api/tienda_routes.test.py` (9 tests), no listado en
  `run-plan.json`'s `files_touched` de T3 (que solo nombra el test file
  de servicio) — el Done When de T3 y la fila de Verification de spec.md
  exigen explícitamente "las 5 rutas responden con los códigos
  esperados", que un test de servicio puro no puede cubrir.
- **J006**: las funciones de `tienda_service` abren y cierran su propia
  sesión (`fn(miembro_id, ...)`), igual que `avatar_service.py` — mismo
  criterio ya establecido ([SERVP-01] no aplica, ninguna se llama desde
  dentro de la transacción de otro servicio).

### Observations

- [DOMAIN candidate, db — promoted, see Curation] `MiembroAccesorioComprado`
  `(miembro_id, accesorio_id)` y `MiembroAccesorioEquipado`
  `(miembro_id, slot)` usan clave primaria compuesta para su propio
  invariante de unicidad, en vez del check de service-layer que
  `[SERV-01]` establece como default — ambas tablas son puros joins sin
  `id` propio, la clave compuesta ES su identidad, no una regla de
  negocio superpuesta. Ver `[DBP-03]`.
- [DOMAIN candidate, api — promoted, see Curation] Una ruta puede mapear
  UNA condición puntual de `ValidationError` a un código distinto de 400
  cuando spec.md's Contracts lo documenta explícitamente (acá: 402 por
  saldo insuficiente) — sin redefinir el mapeo general del resto del
  proyecto. Ver `[APIP-02]`.

### Verification

**Build**: `npm run build` (`tsc --noEmit && vite build`) — green, sin
tocar ningún archivo de frontend (esta spec es 100% backend). **Backend**:
`python3 -m pytest tests/` — 437 passed, 1 skipped (pre-existente, no
relacionado — mismo skip que la baseline de `avatares-economia`).
**Frontend**: `npm run test -- --run` — 183 passed (baseline sin cambios,
confirmado corriendo la suite completa tras un `npm install` que faltaba
en este worktree recién creado — gap de entorno del propio worktree, no
una regresión: `lottie-react` está declarado en `package.json` desde
`avatares-economia` pero `git worktree add` no corre `npm install`).
**Lint**: `npm run lint` (`eslint src/frontend`) — clean. **Coverage**:
`unavailable — not configured` (stack.yaml's `quality_tools.coverage.tool:
null`, gap preexistente, mismo estado que `avatares-economia`; remedio
`/nybo-brownfield-bootstrap --quality`).

**Test cases — las 10 resueltas, ninguna diferida** (`[E2E]`/`[MANUAL]`:
ninguna en esta spec): TC-001/002/009 `tienda_catalogo.test.py` (T1);
TC-003/004/005/010 `tienda_compra.test.py` (T2); TC-006/007/008
`tienda_equipar.test.py` (T3, más 6 tests de servicio adicionales
—especie incompatible, desequipar— y 9 tests de ruta en
`tienda_routes.test.py` verificando los 5 endpoints y sus códigos
200/402/403/404/409/204).

**Migraciones**: `run_migrations` corrido dos veces seguidas contra un
engine SQLite fresco (0001-0026 completas) confirma: las 3 tablas nuevas
existen, el seed de 18 accesorios se siembra una sola vez (idempotente,
igual que el criterio ya establecido en `0022_avatar_catalogo.py`).

**Live evidence (Outcome Smoke Test, spec.md's 5 pasos, driven live
end-to-end)**: real Postgres no alcanzable desde este sandbox (mismo
motivo ya documentado en el build de `avatares-economia`: colisión de
puertos con el `docker-compose` del worktree principal, que corre el
código de OTRA rama). Se corrió un `uvicorn src.api.main:app` real desde
este worktree (SQLite fallback, migraciones reales 0001-0026, cero
fixtures) en un puerto libre. Confirmado en vivo: (1) registrado un
Usuario/Casa/Miembro reales, Ana completó 4 tareas de 20 puntos (créditos
vía el hook ya existente de `avatares-economia`) hasta 80 créditos, y
seleccionó un avatar "perro" (Beagle) real vía
`PUT .../avatar`; (2) `GET .../accesorios/catalogo` para Ana devuelve 13
ítems, especies `{perro, ambos}` únicamente — CERO ítems "solo-gato"
visibles; (3) comprar un accesorio de `cabeza` (20 créditos) bajó el
saldo de 80 a exactamente 60 (`GET .../creditos` confirmado antes/después);
(4) `PUT .../equipar` lo dejó activo en `cabeza`; (5) comprar y equipar
un segundo accesorio de `cabeza` reemplazó al primero (`GET .../accesorios`
confirma que AMBOS siguen en el inventario, solo uno queda activo —
re-equipar el primero lo vuelve a activar, confirmando que no hay
ninguna fila perdida); adicionalmente, los 3 códigos de error del
contrato confirmados en vivo: 402 (accesorio legendario sin saldo
suficiente), 409 (recomprar el mismo accesorio), 403 (el Administrador
intenta comprar en nombre de Ana). `DELETE .../cabeza/equipado` devolvió
204 y dejó el slot vacío.

**Security**: las 3 rutas de escritura (comprar/equipar/desequipar) son
self-service-only (actor debe ser el propio miembro); `accesorio_id`
server-validado contra el inventario real y la especie del avatar
seleccionado en cada compra/equipar; sin secretos nuevos. **Design/wiki
alignment**: el descuento reusa el mismo ledger `CreditoTransaccion` de
`avatares-economia` (ninguna tabla de contabilidad nueva, Constraint de
spec.md); `avatar_service.obtener_balance_creditos`/
`obtener_avatar_seleccionado` consumidas tal cual, cero líneas
reimplementadas (`git diff` contra la rama base confirma que ningún
archivo de `avatares-economia` fue tocado salvo lo ya construido y
estable que esta spec importa).

### Curation

Promovidas 2 Observations a memoria de dominio permanente
(severity-gated — convenciones reales, project-wide): `db.md` `[DBP-03]`
(clave primaria compuesta como identidad de una tabla-join pura, sin
`id` propio — distinto del check de service-layer que `[SERV-01]`
establece para invariantes de negocio sobre una entidad que ya tiene su
propio `id`); `api.md` `[APIP-02]` (una ruta puede mapear una condición
puntual de `ValidationError` a un código distinto del 400 default,
cuando spec.md lo documenta explícitamente, sin redefinir el mapeo
general). Verifiqué primero si el patrón de "multi-row `insert()` con
dicts de distintas keys" (usado en el seed de 0024, normalizado con
`disponible_desde`/`disponible_hasta` explícitos en cada fila) era un
gotcha real de SQLAlchemy antes de documentarlo — no lo es (confirmado
con un script aislado: SQLAlchemy acepta keys distintas por fila sin
error), así que NO se agregó ninguna entrada falsa a `db.md`'s Gotchas;
la normalización se dejó en el código de todas formas por claridad, sin
comentario de gotcha. Dejadas solo en `suggestions.yaml` (no
domain-memory-worthy, spec-specific): S001 (assets placeholder — datos,
no convención), S002 (aviso de rutas reales para `perfil-avatar-ui` —
advisory puntual), S003 (`GET .../accesorios/equipados` faltante —
seguimiento de producto, no una convención de código).
