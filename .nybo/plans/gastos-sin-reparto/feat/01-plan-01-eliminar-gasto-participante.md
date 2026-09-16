# T1 — Elimina `GastoParticipante`; `gasto_service` deja de repartir

## Scope
- `src/db/models/gasto.py`
- `src/db/migrations/0014_eliminar_gasto_participantes.py` (nuevo)
- `src/db/migrate.py`
- `src/services/gasto_service.py`
- Todo archivo de test que construya/lea `GastoParticipante` o
  `gasto.participantes` — grep `GastoParticipante\|\.participantes\b\|participantes=` en `tests/` y `src/` para encontrar cada uno (esperables: `tests/integration/services/gasto_service.test.py`, `gasto_cuotas.test.py`, `gasto_moneda.test.py`, `gasto_estado.test.py`, `gasto_listar_mes.test.py`, `resumen_importer.test.py`, `tests/integration/api/gastos_routes.test.py` y sus variantes `_moneda_routes`/`_estado_routes`/`_mes_routes`, `tests/integration/db/postgres_migrations.test.py`, y cualquier test de dashboard que arme un `Gasto` con participantes de fixture).

## Changes
**Data Layer**
- `Gasto`: eliminar la relationship `participantes` y su docstring
  asociada.
- `GastoParticipante`: eliminar la clase completa.
- Migración `0014_eliminar_gasto_participantes.py`: `DROP TABLE IF
  EXISTS gasto_participantes` (idempotente, mismo criterio que las
  migraciones aditivas de este proyecto pero a la inversa).
- Registrar `0014` en `_MIGRACIONES` (verificar al implementar que sigue
  siendo el próximo número libre).

**Servicio**
- `registrar_gasto`: eliminar el parámetro `participantes`, la llamada a
  `_resolver_participantes`, la validación "no hay miembros activos
  disponibles para dividir el gasto", y el loop que crea
  `GastoParticipante` (tanto en el camino sin cuotas como en
  `_crear_gastos_en_cuotas`). **Mantener** la división del importe total
  entre las N cuotas (`_dividir_importe(importe_decimal, cuotas)`) — no
  tiene relación con participantes, sigue existiendo tal cual.
- `_crear_gastos_en_cuotas`/`registrar_gasto_cuotas_restantes`: eliminar
  el parámetro `miembros_participantes` y el sub-reparto por
  participante de cada cuota (`_dividir_importe(parte_cuota,
  len(miembros_participantes))` y su loop de `GastoParticipante`) — cada
  cuota queda con su importe completo, sin ninguna subdivisión adicional.
- Eliminar `_resolver_participantes` (ya sin ningún caller).
- `_ = gasto.participantes` (forzar carga antes de cerrar sesión,
  presente en varios puntos): eliminar esas líneas, ya no aplica.

**Tests**
- Actualizar cada test encontrado por el grep de arriba: quitar
  cualquier `participantes=[...]` de una llamada a `registrar_gasto`,
  quitar cualquier aserción sobre `gasto.participantes`/
  `GastoParticipante`, y ajustar fixtures de casas/miembros que existían
  solo para poder tener "participantes" donde ya no hace falta.

## Design Rationale
`_dividir_importe` se mantiene como utilidad general (partir X en N
partes iguales con ajuste de redondeo) — solo pierde su uso para
repartir entre participantes; sigue siendo necesaria para dividir el
importe total de una compra entre sus cuotas mensuales.

## Dependencies
Ninguna — primera tarea.

## Done When
- [ ] TC-001, TC-002 y TC-008 pasan.
- [ ] Suite completa en verde (todo test que antes construía/leía `GastoParticipante` queda actualizado, no eliminado sin reemplazo si cubría otra cosa además del reparto).
- [ ] Migración corre limpia e idempotente contra Postgres real.

## Interfaces Produced
Ninguna nueva — elimina interfaces existentes (`GastoParticipante`, `registrar_gasto(participantes=...)`).

## Standalone Verifiable
Sí.
