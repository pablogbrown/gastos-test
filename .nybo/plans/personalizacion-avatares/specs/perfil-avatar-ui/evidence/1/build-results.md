---
feature: personalizacion-avatares/specs/perfil-avatar-ui
schema: build-results/2
cycle: 1
updated: '2026-09-23T19:55:57.148Z'
exit: in-progress
verdict: pending
judgment:
  entries: 3
---
### Goal

Implementar T1 (avatar+accesorios en Miembros/Ranking) y T2 (pantalla Mi Avatar + navegación) de la spec perfil-avatar-ui, integrando visualmente lo construido por avatares-economia y tienda-accesorios.

### Judgment

- **J003** Miembros.test.tsx/Ranking.test.tsx (y App.test.tsx/MuiRestyle.test.tsx, que renderizan esas pantallas) usaban mocks de fetch por índice/orden de invocación (mockImplementationOnce encadenado) — incompatible con el nuevo fetch por fila (avatar+equipados) que se intercala. Se creó tests/unit/frontend/helpers/mockFetchRouter.ts (dispatch por URL/método) y se reescribieron los mocks afectados; 3 asserts basados en calls[N]/toHaveBeenCalledTimes(N) se cambiaron a buscar la llamada por URL/método — el comportamiento verificado (body del POST/PATCH) no cambió, solo cómo se lo localiza.
- **J004** MiAvatar.tsx no deshabilita el botón Comprar cuando el saldo es insuficiente — el rechazo (402) queda del lado del backend, mismo criterio ya establecido para el rechazo de nivel en razas (403, sin gate del lado del cliente). Solo baja la opacidad de la tarjeta como affordance visual.
- **J005** tienda_service.listar_catalogo_accesorios no excluye accesorios ya comprados del catálogo (ver su propio docstring) — MiAvatar.tsx dedupe por id contra el inventario (idsComprados) para no mostrar 'Comprar' y 'Equipar' para el mismo accesorio a la vez.
