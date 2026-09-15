## Summary
- `calcular_balance(casa_id, mes=None)` filtra los gastos considerados por `Gasto.fecha` dentro del mes indicado (`YYYY-MM`), aplicado igual a ambas queries (pago y correspondiente); sin `mes`, usa el mes calendario actual — cambio de comportamiento deliberado (antes sumaba todo el historial).
- `GET /casas/{id}/balance` acepta un query param `mes` opcional (400 si el formato es inválido) y `obtenerBalance(casaId, mes?)` lo propaga.
- `Balance.tsx` agrega un selector nativo `type="month"` preseleccionado en el mes actual; cambiarlo refetchea el balance para ese mes.
- `dashboard_service.armar_dashboard` no cambió — sigue llamando `calcular_balance(casa_id)` sin `mes` y hereda el nuevo default automáticamente.

## Backend Changes
- `src/services/balance_service.py`: nuevo helper `_rango_mes`, filtro de fecha aplicado a ambas queries de agregación.
- `src/api/routes/gastos.py`: `obtener_balance_endpoint` acepta `mes`, mapea `ValidationError` → 400.

## Frontend Changes
- `src/frontend/api/gastosClient.ts`: `obtenerBalance` acepta `mes?` opcional.
- `src/frontend/pages/Balance.tsx`: selector de mes (`TextField type="month"`), refetch on change.

## Automated Testing
- `pytest tests/` — 147 passed (5 nuevos en `tests/integration/services/balance_mensual.test.py` [T1], 2 nuevos en `tests/integration/api/gastos_routes.test.py` [T2]; 2 tests preexistentes de `balance_service.test.py` actualizados para pasar `mes` explícito, ver Judgment J001 en el build log).
- `npm run test -- --run` (vitest) — 70 passed (3 nuevos en `tests/unit/frontend/Balance.test.tsx` [T3]; matcher de URL corregido en `MuiRestyle.test.tsx`, ver Judgment J002).
- `npm run build` — `tsc --noEmit` + `vite build` sin errores.
- `npm run lint` — limpio.
- Live smoke check contra docker-compose local: gasto de este mes + gasto de mes anterior — balance sin `mes` solo refleja el de este mes; cambiando el selector a agosto, la UI refetchea y muestra el gasto de agosto. Confirmado por API y por navegador real (screenshots en `.nybo/plans/balance-mensual/evidence/1/`).

## Suggestions
- Este proyecto no tiene tool de cobertura configurado (`stack.yaml` → `quality_tools.coverage.tool: null`) — gap preexistente, no introducido por esta spec. Ver `evidence/suggestions.yaml` [S001]: `/nybo-brownfield-bootstrap --quality` lo resolvería antes del próximo build que necesite ese gate.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
