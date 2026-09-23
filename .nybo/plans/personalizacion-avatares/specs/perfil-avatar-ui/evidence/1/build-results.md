---
feature: personalizacion-avatares/specs/perfil-avatar-ui
schema: build-results/2
cycle: 1
updated: '2026-09-23T19:50:00.144Z'
exit: in-progress
verdict: pending
judgment:
  entries: 3
---
### Goal

Implementar T1 (avatar+accesorios en Miembros/Ranking) y T2 (pantalla Mi Avatar + navegación) de la spec perfil-avatar-ui, integrando visualmente lo construido por avatares-economia y tienda-accesorios.

### Judgment

- **J001** T1 necesitaba un endpoint para leer los accesorios equipados de un miembro con su detalle completo (asset_overlay_url) para pintar el overlay en Miembros/Ranking (TC-001). `tienda_service.listar_equipados` existía pero devuelve la fila de join, no el `AccesorioAvatar` — agregado `tienda_service.listar_accesorios_equipados` + `GET .../accesorios/equipados` en `tienda.py` (resuelve el [S003] pendiente de tienda-accesorios). Decision-class: spec-deviation, settleable a nivel semi-autonomous — tomada y documentada, no diferida.
- **J002** Ninguna spec anterior expone el catálogo COMPLETO de razas de avatar (locked+unlocked) — avatares-economia solo expone /avatares-disponibles, ya filtrado por nivel. REQ-002/TC-004 de esta spec (mostrar razas bloqueadas con su nivel requerido) lo necesita para T2 — agregado GET .../avatares-catalogo en avatares.py, exponiendo avatar_service.listar_catalogo (ya existía, sin ruta). Mismo criterio/decision-class que J001.
- **J003** Miembros.test.tsx/Ranking.test.tsx (y App.test.tsx/MuiRestyle.test.tsx, que renderizan esas pantallas) usaban mocks de fetch por índice/orden de invocación (mockImplementationOnce encadenado) — incompatible con el nuevo fetch por fila (avatar+equipados) que se intercala. Se creó tests/unit/frontend/helpers/mockFetchRouter.ts (dispatch por URL/método) y se reescribieron los mocks afectados; 3 asserts basados en calls[N]/toHaveBeenCalledTimes(N) se cambiaron a buscar la llamada por URL/método — el comportamiento verificado (body del POST/PATCH) no cambió, solo cómo se lo localiza.
