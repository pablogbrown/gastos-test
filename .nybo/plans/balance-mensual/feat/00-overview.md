# Solution Overview — Balance filtrable por mes

## File Index
- [../spec.md](../spec.md)
- [10-verify.md](10-verify.md)
- [99-progress.md](99-progress.md)

### Task Index

| Task | File | Description | Dependencies |
|---|---|---|---|
| T1 | [01-plan-01-calcular-balance-por-mes.md](01-plan-01-calcular-balance-por-mes.md) | `calcular_balance` filtra por mes, default mes actual | — |
| T2 | [01-plan-02-ruta-y-cliente.md](01-plan-02-ruta-y-cliente.md) | Ruta + cliente HTTP exponen el query param `mes` | T1 |
| T3 | [01-plan-03-selector-de-mes.md](01-plan-03-selector-de-mes.md) | `Balance.tsx` agrega el selector de mes | T2 |

## Problema y solución
`calcular_balance` agrega `Gasto`/`GastoParticipante` sin ningún filtro
de fecha. Se agrega un parámetro opcional `mes: Optional[str]` (formato
`YYYY-MM`); sin valor, se resuelve al mes calendario actual
(`date.today()`) antes de armar las queries. El resto del cálculo
(por miembro, pago vs. correspondiente, transferencias sugeridas) no
cambia — solo cambia qué subconjunto de gastos entra a la suma.

## Arquitectura
Sin componentes nuevos — un parámetro nuevo en una función ya existente,
propagado por la ruta HTTP ya existente y el cliente HTTP ya existente.
`dashboard_service.armar_dashboard` sigue llamando a `calcular_balance(casa_id)`
sin pasar `mes` — hereda el nuevo default (mes actual) automáticamente,
sin necesitar su propio cambio de firma.

## Tradeoffs
- **Default = mes actual (rompe el comportamiento de hoy) vs. default =
  todo el tiempo (aditivo, sin breaking change)**: se eligió mes actual
  porque es lo que realmente resuelve el problema que motiva esta spec
  (cuotas/suscripciones futuras no deben inflar la deuda de hoy) — un
  default "todo el tiempo" con un filtro opcional no lo lograría, porque
  nada obligaría a las pantallas existentes a pasar el filtro. Se
  documenta como cambio de comportamiento deliberado, no un descuido.

## API/Data Contracts
- `GET /casas/{casa_id}/balance` — nuevo query param opcional `mes`
  (string, `YYYY-MM`). Sin cambio en la forma de la respuesta
  (`BalanceResponse`).
- `obtenerBalance(casaId, mes?)` (`gastosClient.ts`) — nuevo parámetro
  opcional, agrega `?mes=YYYY-MM` a la URL cuando está presente.
