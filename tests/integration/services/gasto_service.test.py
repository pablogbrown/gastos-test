"""T2 — Service Layer (integration slice): estabilidad de gastos ya
registrados frente a cambios en la membresía de la casa.

Cubre TC-009.
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
from src.services.gasto_service import registrar_gasto
from src.services.miembro_service import agregar_miembro


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
    migration_casas = importlib.import_module("src.db.migrations.0001_casas_miembros")
    migration_gastos = importlib.import_module("src.db.migrations.0002_gastos")
    # 0004 (spec `dashboard-actividad`): `registrar_gasto` dispara un hook
    # a `actividad_service.registrar_actividad`, que requiere la tabla
    # `historial_actividad`.
    migration_actividad = importlib.import_module("src.db.migrations.0004_historial_actividad")
    # 0005 (spec `usuarios-auth`): `agregar_miembro` ahora exige un
    # Usuario real (por email) para vincular al nuevo Miembro.
    migration_usuarios = importlib.import_module("src.db.migrations.0005_usuarios")
    # 0009 (spec `gastos-suscripcion-mensual`): `listar_gastos` ahora
    # dispara `suscripcion_service.generar_gastos_pendientes` como primera
    # línea, que requiere la tabla `suscripciones`.
    migration_suscripciones = importlib.import_module("src.db.migrations.0009_suscripciones")
    migration_casas.upgrade(engine)
    migration_gastos.upgrade(engine)
    migration_actividad.upgrade(engine)
    migration_usuarios.upgrade(engine)
    migration_suscripciones.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.categoria_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.gasto_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.actividad_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.suscripcion_service.get_session", lambda: TestSession())
    yield TestSession


def test_nuevo_miembro_no_altera_gastos_ya_registrados(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    categoria = crear_categoria(casa.id, "Supermercado", admin_id)
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)

    gasto = registrar_gasto(
        casa.id,
        "Compra semanal",
        Decimal("20000.00"),
        date(2026, 1, 1),
        categoria.id,
        admin_id,
        admin_id,
    )
    ids_participantes_originales = {p.miembro_id for p in gasto.participantes}
    montos_originales = {p.miembro_id: p.monto_correspondiente for p in gasto.participantes}

    assert ids_participantes_originales == {admin_id, ana.id}

    # Se agrega un tercer miembro a la casa DESPUÉS del registro del gasto.
    bruno_usuario = _crear_usuario_de_prueba(db_session, "bruno@example.com")
    agregar_miembro(casa.id, "Bruno", "BRU1", bruno_usuario.email, admin_id)

    from src.services.gasto_service import listar_gastos

    (gasto_persistido,) = listar_gastos(casa.id)
    ids_participantes_actuales = {p.miembro_id for p in gasto_persistido.participantes}
    montos_actuales = {p.miembro_id: p.monto_correspondiente for p in gasto_persistido.participantes}

    assert ids_participantes_actuales == ids_participantes_originales
    assert montos_actuales == montos_originales
    assert gasto_persistido.importe == Decimal("20000.00")
