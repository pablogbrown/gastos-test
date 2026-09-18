"""Punto de entrada de la API. Ejecutar con: uvicorn src.api.main:app --reload

No forma parte del scope de T3 de `casas-miembros` (que solo produce
`casas_router`), pero es el mínimo necesario para que la API sea
arrancable end-to-end. Las specs `gastos` y `tareas-puntos` agregan aquí
sus propios routers; `dashboard-actividad` agrega el suyo por el mismo
motivo (es la última de las cuatro sub-specs de la feature).
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.auth import auth_router
from src.api.routes.autos import autos_router
from src.api.routes.casas import casas_router
from src.api.routes.dashboard import dashboard_router
from src.api.routes.gastos import gastos_router
from src.api.routes.mantenimiento import mantenimiento_router
from src.api.routes.prestamos import prestamos_router
from src.api.routes.suscripciones import suscripciones_router
from src.api.routes.tareas import tareas_router
from src.api.routes.tarjetas import tarjetas_router
from src.db.base import engine
from src.db.migrate import run_migrations

# CORS: la app Android empaquetada via Capacitor (android-capacitor-app)
# corre en su propio origen (`capacitor://localhost`), distinto del
# origen del backend -- sin esto el WebView bloquea la respuesta. El
# flujo web existente (proxy de Vite, same-origin) nunca manda header
# `Origin`, asi que CORSMiddleware no lo toca (TC-004): esto es
# transparente para toda request sin `Origin`, por construccion de la
# libreria, no por una condicion nueva a mantener.
CORS_ALLOWED_ORIGINS_DEFAULT = (
    "capacitor://localhost,http://localhost,https://localhost"
)


def _parse_cors_allowed_origins(
    env: "os._Environ[str]" = os.environ,
) -> list[str]:
    origenes_raw = env.get("CORS_ALLOWED_ORIGINS", CORS_ALLOWED_ORIGINS_DEFAULT)
    return [o.strip() for o in origenes_raw.split(",") if o.strip()]


app = FastAPI(title="taskia API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_cors_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(casas_router)
app.include_router(gastos_router)
app.include_router(suscripciones_router)
app.include_router(tareas_router)
app.include_router(dashboard_router)
app.include_router(tarjetas_router)
app.include_router(prestamos_router)
app.include_router(mantenimiento_router)
app.include_router(autos_router)


@app.on_event("startup")
def _run_migrations_on_startup() -> None:
    run_migrations(engine)


@app.get("/health")
def health():
    return {"status": "ok"}
