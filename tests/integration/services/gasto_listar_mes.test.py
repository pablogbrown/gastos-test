"""T1 (spec `gastos-vista-mensual`) — `gasto_service.listar_gastos`
filtra por mes.

Cubre TC-001 (con `mes` filtra solo los gastos de ese mes), TC-002 (sin
`mes`, comportamiento idéntico al actual — todos los gastos) y TC-006
(control de regresión: `dashboard_service.armar_dashboard`, que llama a
`listar_gastos(casa_id)` sin `mes`, sigue viendo el historial completo
de la casa, no solo el mes actual).
"""
import importlib
import uuid
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.services.casa_service import crear_casa
from src.services.categoria_service import crear_categoria
from src.services.dashboard_service import armar_dashboard
from src.services.exceptions import ValidationError
from src.services.gasto_service import listar_gastos, registrar_gasto

_MIGRACIONES = (
    "0001_casas_miembros",
    "0002_gastos",
    "0003_tareas",
    "0004_historial_actividad",
    "0005_usuarios",
    # `listar_gastos` dispara `suscripcion_service.
    # generar_gastos_pendientes` como primera línea, que requiere la
    # tabla `suscripciones`.
    "0009_suscripciones",
    # `armar_dashboard` llama a `obtener_tarjetas_con_alerta`, que
    # requiere la tabla `tarjetas_credito`.
    "0011_tarjetas_credito",
    # `armar_dashboard` también llama a `obtener_items_con_alerta`, que
    # requiere las tablas `items_mantenimiento`/`materiales_mantenimiento`
    # (spec `mantenimiento-casa`).
    "0017_mantenimiento",
)
_SERVICIOS_CON_SESSION = (
    "casa_service",
    "miembro_service",
    "categoria_service",
    "gasto_service",
    "tarea_service",
    "ranking_service",
    "balance_service",
    "actividad_service",
    "suscripcion_service",
    "tarjeta_service",
    "mantenimiento_service",
)


@pytest.fixture()
def db_session(monkeypatch):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    for nombre in _MIGRACIONES:
        importlib.import_module(f"src.db.migrations.{nombre}").upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    for servicio in _SERVICIOS_CON_SESSION:
        monkeypatch.setattr(f"src.services.{servicio}.get_session", lambda: TestSession())
    yield TestSession


def _crear_gasto(casa_id, categoria_id, admin_id, descripcion, fecha):
    return registrar_gasto(
        casa_id,
        descripcion,
        Decimal("100.00"),
        fecha,
        categoria_id,
        admin_id,
        admin_id,
    )


def test_tc001_con_mes_filtra_solo_los_gastos_de_ese_mes(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    categoria = crear_categoria(casa.id, "Supermercado", admin_id)

    _crear_gasto(casa.id, categoria.id, admin_id, "Gasto de agosto", date(2026, 8, 15))
    _crear_gasto(casa.id, categoria.id, admin_id, "Gasto de septiembre", date(2026, 9, 1))
    _crear_gasto(casa.id, categoria.id, admin_id, "Otro de septiembre", date(2026, 9, 30))

    gastos_septiembre = listar_gastos(casa.id, mes="2026-09")

    descripciones = {gasto.descripcion for gasto in gastos_septiembre}
    assert descripciones == {"Gasto de septiembre", "Otro de septiembre"}


def test_tc002_sin_mes_devuelve_todos_los_gastos_igual_que_hoy(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    categoria = crear_categoria(casa.id, "Supermercado", admin_id)

    _crear_gasto(casa.id, categoria.id, admin_id, "Gasto de agosto", date(2026, 8, 15))
    _crear_gasto(casa.id, categoria.id, admin_id, "Gasto de septiembre", date(2026, 9, 1))

    gastos = listar_gastos(casa.id)

    descripciones = {gasto.descripcion for gasto in gastos}
    assert descripciones == {"Gasto de agosto", "Gasto de septiembre"}


def test_mes_con_formato_invalido_lanza_validation_error(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)

    with pytest.raises(ValidationError):
        listar_gastos(casa.id, mes="fecha-invalida")


def test_tc006_armar_dashboard_sigue_mostrando_historial_completo_sin_filtrar_por_mes(
    db_session,
):
    """Control de regresión (REQ-004): `armar_dashboard` llama a
    `listar_gastos(casa_id)` sin `mes` — debe seguir devolviendo los
    últimos 10 gastos de TODA la casa, sin importar en qué mes estén,
    exactamente igual que antes de esta spec."""
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    categoria = crear_categoria(casa.id, "Varios", admin_id)

    # 6 gastos de agosto + 6 de septiembre -> 12 en total, en dos meses
    # distintos.
    for i in range(6):
        _crear_gasto(casa.id, categoria.id, admin_id, f"Agosto {i}", date(2026, 8, i + 1))
    for i in range(6):
        _crear_gasto(casa.id, categoria.id, admin_id, f"Septiembre {i}", date(2026, 9, i + 1))

    dashboard = armar_dashboard(casa.id)

    assert len(dashboard.gastos_recientes) == 10
    meses_presentes = {gasto.fecha.month for gasto in dashboard.gastos_recientes}
    # Si `armar_dashboard` hubiera empezado a filtrar por el mes actual,
    # solo aparecería un mes -- la presencia de ambos confirma que sigue
    # viendo el historial completo (REQ-004).
    assert meses_presentes == {8, 9}
