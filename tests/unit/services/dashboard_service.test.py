"""T2 — Service Layer (unit slice): dashboard_service.

Cubre TC-002 (una casa sin gastos ni tareas no lanza error) y que
`armar_dashboard` agrega correctamente cada sección con datos.
"""
import importlib
import uuid
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models.usuario import Usuario
from src.services.casa_service import crear_casa
from src.services.categoria_service import crear_categoria
from src.services.dashboard_service import armar_dashboard
from src.services.exceptions import NotFoundError
from src.services.gasto_service import registrar_gasto
from src.services.miembro_service import agregar_miembro
from src.services.tarea_service import completar_tarea, crear_tarea

_MIGRACIONES = (
    "0001_casas_miembros",
    "0002_gastos",
    "0003_tareas",
    "0004_historial_actividad",
    # 0005 (spec `usuarios-auth`): `agregar_miembro` ahora exige un
    # Usuario real (por email) para vincular al nuevo Miembro.
    "0005_usuarios",
    # 0009 (spec `gastos-suscripcion-mensual`): `listar_gastos` (llamado
    # por `armar_dashboard`) ahora dispara `suscripcion_service.
    # generar_gastos_pendientes` como primera línea, que requiere la
    # tabla `suscripciones`.
    "0009_suscripciones",
    # 0011 (spec `tarjetas-credito`): `armar_dashboard` ahora llama a
    # `obtener_tarjetas_con_alerta`, que requiere la tabla
    # `tarjetas_credito`.
    "0011_tarjetas_credito",
    # 0017 (spec `mantenimiento-casa`): `armar_dashboard` ahora llama a
    # `obtener_items_con_alerta`, que requiere las tablas
    # `items_mantenimiento`/`materiales_mantenimiento`.
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


def _crear_usuario_de_prueba(session_factory, email):
    """Inserta un Usuario real (spec `usuarios-auth`): `agregar_miembro`
    ahora exige que el email vinculado ya exista."""
    session = session_factory()
    try:
        usuario = Usuario(id=uuid.uuid4(), email=email, password_hash="hash-de-prueba")
        session.add(usuario)
        session.commit()
        session.refresh(usuario)
        return usuario
    finally:
        session.close()


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


def test_armar_dashboard_de_casa_vacia_no_lanza_error(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id

    dashboard = armar_dashboard(casa.id)

    assert [m.id for m in dashboard.miembros] == [admin_id]
    assert dashboard.gastos_recientes == []
    assert dashboard.tareas_pendientes == []
    assert dashboard.tareas_completadas_recientes == []
    assert dashboard.ranking == []
    # `calcular_balance` incluye a todo miembro aunque no tenga gastos
    # (spec `gastos-sin-reparto`: `dashboard.balance` es un `BalanceCasa`,
    # no una lista).
    assert len(dashboard.balance.aportes) == 1
    assert dashboard.balance.aportes[0].total == Decimal("0")
    assert dashboard.balance.totales[0].total_gastos == Decimal("0")


def test_armar_dashboard_de_casa_inexistente_lanza_not_found(db_session):
    with pytest.raises(NotFoundError):
        armar_dashboard(uuid.uuid4())


def test_armar_dashboard_agrega_gastos_tareas_y_ranking(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)
    categoria = crear_categoria(casa.id, "Supermercado", admin_id)

    registrar_gasto(
        casa.id,
        "Compra semanal",
        Decimal("10000.00"),
        date(2026, 1, 1),
        categoria.id,
        admin_id,
        admin_id,
    )
    tarea_pendiente = crear_tarea(casa.id, "Sacar la basura", 5, actor=admin_id)
    tarea_completada = crear_tarea(casa.id, "Lavar los platos", 8, actor=admin_id)
    completar_tarea(tarea_completada.id, ana.id, ana.id)

    dashboard = armar_dashboard(casa.id)

    assert len(dashboard.gastos_recientes) == 1
    assert [t.id for t in dashboard.tareas_pendientes] == [tarea_pendiente.id]
    assert len(dashboard.tareas_completadas_recientes) == 1
    assert dashboard.tareas_completadas_recientes[0].tarea_id == tarea_completada.id
    entrada_ana = next(fila for fila in dashboard.ranking if fila["miembroId"] == ana.id)
    assert entrada_ana["puntos"] == 8


def test_armar_dashboard_limita_gastos_y_tareas_completadas_a_diez(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)
    categoria = crear_categoria(casa.id, "Varios", admin_id)

    for i in range(12):
        registrar_gasto(
            casa.id,
            f"Gasto {i}",
            Decimal("1000.00"),
            date(2026, 1, i + 1),
            categoria.id,
            admin_id,
            admin_id,
        )
        tarea = crear_tarea(casa.id, f"Tarea {i}", 1, actor=admin_id)
        completar_tarea(tarea.id, ana.id, ana.id)

    dashboard = armar_dashboard(casa.id)

    assert len(dashboard.gastos_recientes) == 10
    assert len(dashboard.tareas_completadas_recientes) == 10
