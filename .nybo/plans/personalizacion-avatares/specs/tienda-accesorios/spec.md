# Tienda de accesorios - Technical Specification

| | |
| --- | --- |
| Progress | [progress.md](progress.md) |

## Intention

### What
Un catálogo de accesorios (ropa/objetos) comprables con los créditos de `avatares-economia`, organizados en slots equipables (cabeza/cuello/cuerpo — como máximo uno activo por slot), con rareza y disponibilidad por tiempo (ítems estacionales/limitados).

### Why
El usuario pidió que los créditos den acceso a "mejoras para el avatar así como nuevos avatares, ropa para los mismos, etc." — esta spec construye la mitad "ropa/accesorios" de ese pedido, sobre la economía ya construida en `avatares-economia`.

## Outcome
Un miembro con créditos entra a la tienda, ve accesorios compatibles con la especie de su avatar actual (algunos bloqueados por precio, algunos de tiempo limitado), compra uno, y lo equipa — reemplazando cualquier otro accesorio que ya tuviera activo en el mismo slot.

## Requirements

### REQ-001: Catálogo de accesorios
Existe un catálogo de accesorios (`AccesorioAvatar`) con nombre, slot (`cabeza`/`cuello`/`cuerpo`), rareza, precio en créditos, especie compatible (`perro`/`gato`/`ambos`), un asset de overlay (ícono/badge, URL/path de texto plano — nunca integrado a la animación Lottie del cuerpo, decisión ya tomada) y una ventana de disponibilidad opcional.

- El catálogo de compra que ve un miembro se filtra por la especie de SU avatar actualmente seleccionado — un accesorio compatible solo con "gato" no aparece para quien tiene un perro seleccionado. Sin avatar seleccionado, se muestra el catálogo completo sin filtrar por especie.

| ID | Given/When/Then | Type |
| --- | --- | --- |
| TC-001 | **Given** el catálogo sembrado **When** se lista **Then** cada accesorio expone slot, rareza, precio, especie compatible, y la URL del asset de overlay. | `[UNIT]` |
| TC-002 | **Given** un miembro con un avatar de especie "perro" seleccionado **When** lista el catálogo de compra **Then** los accesorios compatibles solo con "gato" no aparecen. | `[UNIT]` |

### REQ-002: Compra de accesorios
Comprar un accesorio descuenta su precio del saldo de créditos del miembro (una `CreditoTransaccion` negativa, reusando el ledger de `avatares-economia`) y lo agrega a su inventario (`MiembroAccesorioComprado`) — rechaza la compra si el saldo es insuficiente, y rechaza comprar un accesorio ya presente en el inventario del miembro (evita descuento doble).

| ID | Given/When/Then | Type |
| --- | --- | --- |
| TC-003 | **Given** un miembro con saldo suficiente **When** compra un accesorio **Then** se crea una `CreditoTransaccion` negativa por su precio y el accesorio se agrega a su inventario. | `[INTEGRATION]` |
| TC-004 | **Given** un miembro con saldo insuficiente **When** intenta comprar **Then** la compra se rechaza y no se descuenta nada. | `[INTEGRATION]` |
| TC-005 | **Given** un accesorio ya presente en el inventario del miembro **When** intenta comprarlo de nuevo **Then** se rechaza sin descontar créditos una segunda vez. | `[INTEGRATION]` |

### REQ-003: Equipar/desequipar por slot
Un miembro puede equipar como máximo un accesorio COMPRADO por slot — equipar uno nuevo en un slot ya ocupado reemplaza al anterior, nunca coexisten dos activos en el mismo slot. Equipar requiere que el accesorio esté en el inventario del miembro y sea compatible con la especie de su avatar actualmente seleccionado.

| ID | Given/When/Then | Type |
| --- | --- | --- |
| TC-006 | **Given** un accesorio comprado y compatible con el avatar actual **When** se equipa **Then** queda como el ítem activo de su slot. | `[INTEGRATION]` |
| TC-007 | **Given** un accesorio que el miembro NO compró **When** intenta equiparlo **Then** se rechaza. | `[INTEGRATION]` |
| TC-008 | **Given** dos accesorios del mismo slot, ambos ya comprados **When** se equipa el segundo **Then** reemplaza al primero — nunca quedan ambos activos a la vez. | `[INTEGRATION]` |

### REQ-004: Disponibilidad por tiempo
Un accesorio fuera de su ventana `disponible_desde`/`disponible_hasta` no aparece en el catálogo de compra para quien todavía no lo compró — pero uno ya comprado sigue visible y equipable en el inventario del miembro sin importar la ventana (mismo criterio ya establecido para razas de avatar en `avatares-economia`).

| ID | Given/When/Then | Type |
| --- | --- | --- |
| TC-009 | **Given** un accesorio con `disponible_hasta` en el pasado **When** se lista el catálogo de compra para quien no lo tiene **Then** no aparece. | `[UNIT]` |
| TC-010 | **Given** ese mismo accesorio ya comprado por un miembro **When** ese miembro consulta su inventario **Then** sigue apareciendo y siendo equipable. | `[UNIT]` |

## Constraints
- REQ-002: toda compra usa el mismo ledger `CreditoTransaccion` de `avatares-economia` (`motivo="compra_accesorio"`) — esta spec no crea un segundo mecanismo de descuento.
- REQ-003: la especie compatible se valida contra `avatar_service.obtener_avatar_seleccionado` (de `avatares-economia`) — nunca se duplica esa lógica.
- Ningún archivo de `avatares-economia` se modifica salvo lo estrictamente necesario para exponer sus funciones ya producidas (`obtener_balance_creditos`, `obtener_avatar_seleccionado`) — esta spec las consume, no las reimplementa.

## Solution
Se agrega el catálogo de accesorios, el inventario de compras, y el estado de equipado por slot, todo apoyado en el ledger de créditos y el avatar seleccionado que `avatares-economia` ya construyó.

### Data model

```mermaid
erDiagram
  MIEMBRO ||--o{ MIEMBRO_ACCESORIO_COMPRADO : posee
  MIEMBRO ||--o{ MIEMBRO_ACCESORIO_EQUIPADO : equipa
  ACCESORIO_AVATAR ||--o{ MIEMBRO_ACCESORIO_COMPRADO : es
  ACCESORIO_AVATAR ||--o{ MIEMBRO_ACCESORIO_EQUIPADO : es

  ACCESORIO_AVATAR {
    uuid id PK
    string nombre
    string slot
    string rareza
    int precio_creditos
    string especie_compatible
    string asset_overlay_url
    date disponible_desde
    date disponible_hasta
  }
  MIEMBRO_ACCESORIO_COMPRADO {
    uuid miembro_id PK_FK
    uuid accesorio_id PK_FK
    datetime comprado_en
  }
  MIEMBRO_ACCESORIO_EQUIPADO {
    uuid miembro_id PK_FK
    string slot PK
    uuid accesorio_id FK
  }
```

### Contracts

- `GET /accesorios?miembro_id=...` → catálogo filtrado por especie del avatar actual del miembro.
- `GET /miembros/{miembro_id}/accesorios` → inventario comprado (ignorando ventana de disponibilidad).
- `POST /miembros/{miembro_id}/accesorios/{accesorio_id}/comprar` → 402/`ValidationError` si saldo insuficiente, 409 si ya comprado.
- `PUT /miembros/{miembro_id}/accesorios/equipar` `{accesorio_id}` → resuelve el `slot` del accesorio y reemplaza lo que hubiera activo ahí; 403 si no está en el inventario o es incompatible de especie.
- `DELETE /miembros/{miembro_id}/accesorios/{slot}/equipado` → desequipa el slot (queda vacío).

### Task Execution

| Task | File | Description | Dependencies |
| --- | --- | --- | --- |
| T1 | [01-plan-01-catalogo-accesorios.md](feat/01-plan-01-catalogo-accesorios.md) | Catálogo `AccesorioAvatar` + seed + filtro por especie/ventana | — |
| T2 | [01-plan-02-compra-accesorios.md](feat/01-plan-02-compra-accesorios.md) | Inventario + compra (gasta créditos) | T1 |
| T3 | [01-plan-03-equipar-accesorios.md](feat/01-plan-03-equipar-accesorios.md) | Equipar/desequipar por slot + endpoints | T2 |

### Verification

| Task | Test cases | Additional gate criteria |
| --- | --- | --- |
| T1 | TC-001, TC-002, TC-009 | `[AUTO]` `pytest tests/integration/services/tienda_catalogo.test.py`. |
| T2 | TC-003, TC-004, TC-005, TC-010 | `[AUTO]` `pytest tests/integration/services/tienda_compra.test.py`. |
| T3 | TC-006, TC-007, TC-008 | `[AUTO]` `pytest tests/integration/services/tienda_equipar.test.py`; las 5 rutas responden con los códigos esperados. |

#### Outcome Smoke Test
1. Con un miembro con créditos y un avatar "perro" seleccionado, listar el catálogo de accesorios — confirmar que los de "gato" no aparecen.
2. Comprar un accesorio compatible; confirmar que el saldo baja exactamente su precio.
3. Equiparlo; confirmar que queda como el ítem activo de su slot.
4. Comprar y equipar un segundo accesorio del mismo slot; confirmar que reemplaza al primero.
5. Gate final: los 3 test suites en verde, endpoints respondiendo los códigos esperados.

## Sources

| Type | Reference | Detail |
| --- | --- | --- |
| Spec | avatares-economia | .nybo/plans/personalizacion-avatares/specs/avatares-economia/spec.md — provee el ledger de créditos y el avatar seleccionado que esta spec consume. |
| Spec | personalizacion-avatares | .nybo/plans/personalizacion-avatares/plan.md — feature-level, split rationale. |

## History

| # | Date | Event | Verdict | Summary |
| --- | --- | --- | --- | --- |
| 1 | 2026-09-23 | plan | — | Spec created — 3 tasks, 10 test cases. |
