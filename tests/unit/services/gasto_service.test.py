"""T2 — Service Layer (unit slice): registrar_gasto y crear_categoria.

Cubre TC-001, TC-002, TC-003, TC-004, TC-005 y TC-006.
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
from src.services.exceptions import NotFoundError, PermissionDeniedError, ValidationError
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
    migration_casas.upgrade(engine)
    migration_gastos.upgrade(engine)
    migration_actividad.upgrade(engine)
    migration_usuarios.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.categoria_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.gasto_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.actividad_service.get_session", lambda: TestSession())
    yield TestSession


def _casa_con_categoria(db_session, nombre_categoria="Supermercado"):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    categoria = crear_categoria(casa.id, nombre_categoria, admin_id)
    return casa, admin_id, categoria


def test_registrar_gasto_con_datos_validos_se_guarda_asociado_a_quien_pago(db_session):
    casa, admin_id, categoria = _casa_con_categoria(db_session)

    gasto = registrar_gasto(
        casa.id,
        "Compra semanal",
        Decimal("100.00"),
        date(2026, 1, 1),
        categoria.id,
        admin_id,
        admin_id,
    )

    assert gasto.descripcion == "Compra semanal"
    assert gasto.pagado_por == admin_id
    assert gasto.importe == Decimal("100.00")


def test_registrar_gasto_sin_categoria_es_rechazado(db_session):
    casa, admin_id, _categoria = _casa_con_categoria(db_session)

    with pytest.raises(ValidationError):
        registrar_gasto(
            casa.id,
            "Compra semanal",
            Decimal("100.00"),
            date(2026, 1, 1),
            None,
            admin_id,
            admin_id,
        )


def test_no_admin_no_puede_crear_categoria(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)

    with pytest.raises(PermissionDeniedError):
        crear_categoria(casa.id, "Otra", ana.id)


def test_registrar_gasto_no_acepta_participantes_ni_genera_reparto(db_session):
    """TC-001 (spec `gastos-sin-reparto`): `registrar_gasto` ya no tiene
    ningún parámetro `participantes` — pasarlo explícitamente falla con
    un `TypeError`, y el gasto en sí no expone ningún atributo de
    reparto."""
    casa, admin_id, categoria = _casa_con_categoria(db_session)
    agregar_miembro(
        casa.id, "Ana", "ANA1", _crear_usuario_de_prueba(db_session, "ana@example.com").email, admin_id
    )

    with pytest.raises(TypeError):
        registrar_gasto(
            casa.id,
            "Gasto compartido",
            Decimal("40000.00"),
            date(2026, 1, 1),
            categoria.id,
            admin_id,
            admin_id,
            participantes=[admin_id],
        )

    gasto = registrar_gasto(
        casa.id,
        "Gasto compartido",
        Decimal("40000.00"),
        date(2026, 1, 1),
        categoria.id,
        admin_id,
        admin_id,
    )
    assert not hasattr(gasto, "participantes")


def test_registrar_gasto_actor_sin_membresia_activa_es_rechazado(db_session):
    casa, admin_id, categoria = _casa_con_categoria(db_session)
    usuario_ajeno = uuid.uuid4()

    with pytest.raises(PermissionDeniedError):
        registrar_gasto(
            casa.id,
            "Gasto",
            Decimal("100.00"),
            date(2026, 1, 1),
            categoria.id,
            admin_id,
            usuario_ajeno,
        )


def test_registrar_gasto_con_categoria_inexistente_es_rechazado(db_session):
    casa, admin_id, _categoria = _casa_con_categoria(db_session)

    with pytest.raises(ValidationError):
        registrar_gasto(
            casa.id,
            "Gasto",
            Decimal("100.00"),
            date(2026, 1, 1),
            uuid.uuid4(),
            admin_id,
            admin_id,
        )
