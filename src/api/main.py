"""Punto de entrada de la API. Ejecutar con: uvicorn src.api.main:app --reload

No forma parte del scope de T3 de `casas-miembros` (que solo produce
`casas_router`), pero es el mínimo necesario para que la API sea
arrancable end-to-end. Las specs `gastos` y `tareas-puntos` agregan aquí
sus propios routers; `dashboard-actividad` agrega el suyo por el mismo
motivo (es la última de las cuatro sub-specs de la feature).
"""
from fastapi import FastAPI

from src.api.routes.auth import auth_router
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

app = FastAPI(title="taskia API")
app.include_router(auth_router)
app.include_router(casas_router)
app.include_router(gastos_router)
app.include_router(suscripciones_router)
app.include_router(tareas_router)
app.include_router(dashboard_router)
app.include_router(tarjetas_router)
app.include_router(prestamos_router)
app.include_router(mantenimiento_router)


@app.on_event("startup")
def _run_migrations_on_startup() -> None:
    run_migrations(engine)


@app.get("/health")
def health():
    return {"status": "ok"}
