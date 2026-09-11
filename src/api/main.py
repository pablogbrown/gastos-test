"""Punto de entrada de la API. Ejecutar con: uvicorn src.api.main:app --reload

No forma parte del scope de T3 (que solo produce `casas_router`), pero es
el mínimo necesario para que la API sea arrancable end-to-end. Las specs
hermanas (`gastos`, `tareas-puntos`) agregarán su propio router aquí.
"""
from fastapi import FastAPI

from src.api.routes.casas import casas_router

app = FastAPI(title="taskia API")
app.include_router(casas_router)


@app.get("/health")
def health():
    return {"status": "ok"}
