---
feature: gastos-vista-mensual
schema: build-results/2
cycle: 1
updated: '2026-09-16T15:33:43.867Z'
exit: ready
verdict: verified
judgment:
  entries: 2
observations:
  entries: 1
tests:
  backend:
    passed: 268
    failed: 0
  frontend:
    passed: 105
    failed: 0
---
### Goal

Implementar el spec gastos-vista-mensual: gasto_service.listar_gastos acepta un parametro mes opcional (YYYY-MM) via un nuevo helper _rango_mes local (duplicado deliberado de balance_service._rango_mes); GET /casas/{casa_id}/gastos?mes= lo expone via query param; Gastos.tsx agrega un selector de mes (TextField type=month, mismo patron que Balance.tsx) que filtra el listado. TC-001 a TC-006, con TC-006 como control de regresion de armar_dashboard (que sigue llamando listar_gastos sin mes).

### Observations

- [SERVP-02 update] Esta spec es la 3ra confirmacion del patron de duplicar un helper de aritmetica de fecha (`_rango_mes`) por servicio en vez de compartirlo -- `gasto_service._rango_mes` es casi identico a `balance_service._rango_mes`, con una diferencia deliberada: `mes` es obligatorio (sin default a 'mes actual'), porque `listar_gastos(casa_id)` sin `mes` debe seguir significando 'todos', no 'este mes' (a diferencia de `calcular_balance`). Convencion actualizada en `.nybo/memory/domains/services.md` [SERVP-02].

### Verification

### Build
- `npm run build`: OK. `npm run lint`: OK.

### Tests
- Backend (docker, Postgres real): 268 passed (261 baseline post-merge + 7 nuevos), 0 failed.
- Frontend (`npm run test -- --run`): 105 passed en 18 archivos (102 + 3 nuevos), 0 failed.
- Sin coverage tool configurado (`stack.yaml`); cada TC-xxx automatable = test real (gate duro disponible).

### Test cases & progress
- `[TC-001]` PASS — `gasto_listar_mes.test.py::test_tc001_con_mes_filtra_solo_los_gastos_de_ese_mes`
- `[TC-002]` PASS — `gasto_listar_mes.test.py::test_tc002_sin_mes_devuelve_todos_los_gastos_igual_que_hoy`
- `[TC-003]` PASS — `gastos_mes_routes.test.py::test_tc003_gastos_con_mes_explicito_filtra_la_respuesta`
- `[TC-004]` PASS — `Gastos.test.tsx` (pide el mes al cargar + al cambiar el selector)
- `[TC-005]` PASS — `Gastos.test.tsx` (mes actual preseleccionado)
- `[TC-006]` PASS — `gasto_listar_mes.test.py::test_tc006_...` (control: `armar_dashboard` sin filtrar por mes, 12 gastos en 2 meses)

T1-T3 `[x]`. Extra: 400 en mes inválido (servicio+API), control TC-002 a nivel HTTP.

### Manual test cases
Ninguna `[MANUAL]` en spec.md.

### Live evidence
- Smoke HTTP real contra Postgres (puerto alterno; 8000/5173 ocupados por otro stack `gastos-test` no relacionado): `mes=2026-09` → solo septiembre; `mes=2026-08` → solo agosto; sin `mes` → ambos; `mes=invalido` → 400.
- Sin smoke visual del selector en navegador (mismo conflicto de puertos) — cubierto end-to-end por TC-004/TC-005 en `Gastos.test.tsx`.

### Security
Sin cambios: mismo guard `resolver_actor_en_casa`.

### Design principles
Mismo patrón que `balance_service`/`GET .../balance?mes=`. Ningún archivo >500 líneas.

### Wiki alignment
`services.md` [SERVP-02] actualizada — 3ra confirmación (ver Curation).

### Curation

- Convention updated: `services.md` [SERVP-02] — 3ra confirmación (`balance_service._rango_mes`, `gasto_service._sumar_meses`, ahora `gasto_service._rango_mes`); confidence `high`, `verified: 2026-09-16`.
- J001/J002 dentro de la autoridad del builder (merge de `main` pedido explícitamente; ajuste mecánico de matchers de test) — sin entradas en `decisions.yaml`.
- Sin architecture facts / foundation gaps nuevos — extensión aditiva sobre el patrón ya existente de `balance_service`.
