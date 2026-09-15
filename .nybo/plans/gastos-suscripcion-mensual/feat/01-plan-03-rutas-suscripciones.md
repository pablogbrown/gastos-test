# T3 — Rutas HTTP de suscripciones

## Scope
- `src/api/routes/suscripciones.py` (nuevo).
- `src/api/main.py` — registrar el router nuevo.

## Changes
**API Route**
- Nuevo router `suscripciones_router = APIRouter(prefix="/casas",
  tags=["suscripciones"])`, mismo patrón que `casas.py`/`gastos.py`.
- Schemas (viven en este archivo, mismo criterio que `gastos.py`):
  `SuscripcionCreate {descripcion, importe, categoria_id}`,
  `SuscripcionActivaUpdate {activa: bool}`, `SuscripcionOut {id, casa_id,
  descripcion, importe, categoria_id, pagado_por, activa,
  ultimo_mes_generado, creado_en}`.
- `POST /casas/{casa_id}/suscripciones` → `crear_suscripcion`, 201.
- `GET /casas/{casa_id}/suscripciones` → `listar_suscripciones`.
- `PATCH /casas/{casa_id}/suscripciones/{id}` → si `payload.activa` es
  `True`, 400 ("Reactivar una suscripción no está soportado"), mismo
  criterio que `actualizar_miembro_endpoint`; si es `False`, llama a
  `cancelar_suscripcion`.
- Los tres usan `actor: UUID = Depends(resolver_actor_en_casa)`, y cada
  handler traduce `PermissionDeniedError`/`NotFoundError`/`ValidationError`
  a 403/404/400, mismo patrón que el resto de las rutas.
- `main.py`: importar `suscripciones_router` e incluirlo junto a los
  demás routers de `/casas`.

## Design Rationale
Archivo de ruta propio, no agregado a `gastos.py` — mismo criterio que
separó `casas.py`/`gastos.py`/`tareas.py`/`dashboard.py` entre sí: cada
recurso HTTP en su propio módulo, todos bajo el prefijo compartido
`/casas`.

## Dependencies
T2 — necesita las funciones de `suscripcion_service`.

## Done When
- [ ] `pytest tests/` completo sigue en verde.
- [ ] Los 3 endpoints responden los códigos esperados (verificado ya a
      nivel servicio en T2; acá se confirma que el payload/response HTTP
      tiene la forma correcta).

## Interfaces Produced
- `suscripciones_router` — exportado, registrado en `main.py`.

## Standalone Verifiable
Sí.
