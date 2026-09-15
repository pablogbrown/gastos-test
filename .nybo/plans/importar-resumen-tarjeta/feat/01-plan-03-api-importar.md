# T3 — Endpoint de subida de PDF

## Scope
- `src/api/routes/tarjetas.py`
- `tests/integration/api/importar_resumen_routes.test.py` (nuevo).

## Changes
- `ResumenImportadoOut` (schema): `gastos_creados: int, cuotas_creadas:
  int, suscripciones_vinculadas: int, tarjeta: TarjetaOut`.
- `POST /casas/{casa_id}/tarjetas/{tarjeta_id}/resumen` — recibe
  `archivo: UploadFile` (`multipart/form-data`), lee los bytes, llama a
  `resumen_importer_service.importar_resumen(casa_id, tarjeta_id, bytes,
  actor)`.
  - `PdfFormatoNoReconocidoError` → 422 con `detail` descriptivo (TC-009).
  - `NotFoundError` (tarjeta inexistente) → 404.
  - `ValidationError` → 400.

## Design Rationale
Mismo patrón de traducción de excepciones que el resto de las rutas
(`ValidationError`→400, `NotFoundError`→404); 422 reservado para "el
archivo no tiene el formato esperado" — distingue "dato con forma
inválida" (400) de "documento no reconocible" (422), mismo criterio que
ya separa `ValidationError` de un 422 genérico de Pydantic en el resto
del proyecto.

## Dependencies
T2 (`importar_resumen`).

## Done When
- [ ] Un `POST` con el PDF de ejemplo responde 200 con los contadores esperados.
- [ ] TC-009 responde 422.

## Interfaces Produced
- `ResumenImportadoOut`.

## Interfaces Consumed
- T2: `importar_resumen`.

## Standalone Verifiable
Sí.
