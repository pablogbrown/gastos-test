# T2 — CORS en el backend

## Scope
- `src/api/main.py`: agregar `from fastapi.middleware.cors import
  CORSMiddleware` y `app.add_middleware(CORSMiddleware, ...)` — leer
  orígenes permitidos de la env var `CORS_ALLOWED_ORIGINS` (lista
  separada por comas), default
  `"capacitor://localhost,http://localhost,https://localhost"` cuando
  la env var no está seteada. `allow_credentials=True`,
  `allow_methods=["*"]`, `allow_headers=["*"]` (ver Tradeoffs de
  `00-overview.md`).
- Helper pequeño (puede vivir en el propio `main.py` o en un
  `src/api/cors.py` si el resto del archivo ya está apretado) para
  parsear la env var: `origenes = [o.strip() for o in env.get(...,
  default).split(",") if o.strip()]`.

## Dependencies
Ninguna (independiente de T1).

## Done When
- TC-003/TC-004 pasan.
- El resto de la suite backend (363 tests) sigue en verde — `Test
  Client` de FastAPI no envía `Origin` por default en la mayoría de los
  tests existentes, así que `CORSMiddleware` no debería alterar ninguna
  respuesta ya cubierta; confirmar explícitamente con la corrida
  completa, no asumir.

## Verifiability
INTEGRATION — nuevo `tests/integration/api/cors.test.py`: una request
con `Origin: capacitor://localhost` recibe
`Access-Control-Allow-Origin: capacitor://localhost` en la respuesta; una
request con un origen no listado (ej. `http://evil.example`) NO recibe
ese header; una request sin `Origin` (como las de siempre) no se ve
afectada.
