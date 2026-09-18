"""T2 (android-capacitor-app) — TC-003/TC-004: CORS para la app
Capacitor empaquetada.

La app instalada corre en su propio origen (`capacitor://localhost` en
Android, distinto del origen del backend) — sin CORS el WebView bloquea
la respuesta. Cubre:
  - TC-003: un origen permitido (default o via `CORS_ALLOWED_ORIGINS`)
    recibe `Access-Control-Allow-Origin` en la respuesta.
  - TC-004: un origen no permitido no recibe ese header, y una request
    sin header `Origin` (el flujo web same-origin de siempre, vía el
    proxy de Vite) no se ve afectada — cero regresión en la suite
    existente, que nunca manda `Origin`.

Usa `src.api.main.app` directamente (primer test en usar la app
completa en vez de armar un sub-set de routers) — el middleware de CORS
se registra a nivel de app, no de router individual, así que hay que
probarlo contra la app real. `DATABASE_URL` no está seteada en este
proceso de test => `src.db.base.engine` usa el fallback sqlite en
memoria (ver `db/base.py`), igual que el resto de la suite.
"""
from fastapi.testclient import TestClient

from src.api.main import app


def test_tc003_origen_permitido_recibe_el_header_cors():
    with TestClient(app) as client:
        resp = client.get("/health", headers={"Origin": "capacitor://localhost"})

    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == "capacitor://localhost"


def test_tc004_origen_no_permitido_no_recibe_el_header():
    with TestClient(app) as client:
        resp = client.get("/health", headers={"Origin": "http://evil.example"})

    assert resp.status_code == 200
    assert "access-control-allow-origin" not in resp.headers


def test_tc004_sin_header_origin_no_cambia_nada_flujo_web_actual():
    with TestClient(app) as client:
        resp = client.get("/health")

    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
    assert "access-control-allow-origin" not in resp.headers


def test_cors_allowed_origins_env_var_configurable(monkeypatch):
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "http://192.168.1.5:5173")
    import importlib

    from src.api import main as main_module

    importlib.reload(main_module)
    try:
        with TestClient(main_module.app) as client:
            resp_permitido = client.get(
                "/health", headers={"Origin": "http://192.168.1.5:5173"}
            )
            resp_default_ya_no_permitido = client.get(
                "/health", headers={"Origin": "capacitor://localhost"}
            )
        assert (
            resp_permitido.headers.get("access-control-allow-origin")
            == "http://192.168.1.5:5173"
        )
        assert "access-control-allow-origin" not in resp_default_ya_no_permitido.headers
    finally:
        monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)
        importlib.reload(main_module)
