"""Punto de entrada de la API. Ejecutar con: uvicorn src.api.main:app --reload

No forma parte del scope de T3 de `casas-miembros` (que solo produce
`casas_router`), pero es el mínimo necesario para que la API sea
arrancable end-to-end. La spec `gastos` agrega aquí su propio
`gastos_router`; la spec hermana `tareas-puntos` agregará el suyo.
"""
from fastapi import FastAPI

from src.api.routes.casas import casas_router
from src.api.routes.gastos import gastos_router
from src.api.routes.tareas import tareas_router

app = FastAPI(title="taskia API")
app.include_router(casas_router)
app.include_router(gastos_router)
app.include_router(tareas_router)


@app.get("/health")
def health():
    return {"status": "ok"}
