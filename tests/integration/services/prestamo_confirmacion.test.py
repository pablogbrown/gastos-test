"""T2 (spec `prestamos-confirmacion-mutua`) — Confirmación mutua de un
préstamo: auto-confirmación al crear, `confirmar_prestamo`, y el guard
en `actualizar_estado_prestamo`.

Cubre TC-001 a TC-007 (`10-verify.md`).
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
from src.services.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from src.services.miembro_service import agregar_miembro
from src.services.prestamo_service import (
    actualizar_estado_prestamo,
    confirmar_prestamo,
    crear_prestamo,
)


def _crear_usuario_de_prueba(session_factory, email):
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
    # `agregar_miembro` dispara un hook a `actividad_service.
    # registrar_actividad`, que requiere la tabla `historial_actividad`
    # (mismo motivo que `prestamo_service.test.py`).
    migration_actividad = importlib.import_module("src.db.migrations.0004_historial_actividad")
    migration_usuarios = importlib.import_module("src.db.migrations.0005_usuarios")
    migration_prestamos = importlib.import_module("src.db.migrations.0014_prestamos")
    migration_casas.upgrade(engine)
    migration_gastos.upgrade(engine)
    migration_actividad.upgrade(engine)
    migration_usuarios.upgrade(engine)
    migration_prestamos.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.prestamo_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.actividad_service.get_session", lambda: TestSession())
    yield TestSession


def _armar_casa_con_tres_miembros(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    maca_usuario = _crear_usuario_de_prueba(db_session, "maca@example.com")
    maca = agregar_miembro(casa.id, "Maca", "MACA1", maca_usuario.email, admin_id)
    bruno_usuario = _crear_usuario_de_prueba(db_session, "bruno@example.com")
    bruno = agregar_miembro(casa.id, "Bruno", "BRU1", bruno_usuario.email, admin_id)
    return casa, admin_id, maca.id, bruno.id


def _crear(casa_id, prestamista_id, deudor_id, actor):
    return crear_prestamo(
        casa_id,
        prestamista_id,
        deudor_id,
        Decimal("1000.00"),
        "ARS",
        date(2026, 9, 1),
        actor,
    )


def test_tc001_prestamista_registra_su_rol_queda_confirmado(db_session):
    casa, admin_id, maca_id, _bruno_id = _armar_casa_con_tres_miembros(db_session)

    prestamo = _crear(casa.id, admin_id, maca_id, admin_id)

    assert prestamo.confirmado_prestamista is True
    assert prestamo.confirmado_deudor is None
    assert prestamo.estado_confirmacion == "pendiente_confirmacion"


def test_tc002_deudor_registra_su_rol_queda_confirmado(db_session):
    casa, admin_id, maca_id, _bruno_id = _armar_casa_con_tres_miembros(db_session)

    prestamo = _crear(casa.id, admin_id, maca_id, maca_id)

    assert prestamo.confirmado_deudor is True
    assert prestamo.confirmado_prestamista is None
    assert prestamo.estado_confirmacion == "pendiente_confirmacion"


def test_tc003_tercero_registra_ambos_quedan_pendientes(db_session):
    casa, admin_id, maca_id, bruno_id = _armar_casa_con_tres_miembros(db_session)

    prestamo = _crear(casa.id, admin_id, maca_id, bruno_id)

    assert prestamo.confirmado_prestamista is None
    assert prestamo.confirmado_deudor is None
    assert prestamo.estado_confirmacion == "pendiente_confirmacion"


def test_tc004_tercero_no_puede_confirmar_ni_rechazar(db_session):
    casa, admin_id, maca_id, bruno_id = _armar_casa_con_tres_miembros(db_session)
    prestamo = _crear(casa.id, admin_id, maca_id, admin_id)

    with pytest.raises(PermissionDeniedError):
        confirmar_prestamo(casa.id, prestamo.id, bruno_id, True)


def test_tc005_ambas_partes_confirman_queda_confirmado(db_session):
    casa, admin_id, maca_id, _bruno_id = _armar_casa_con_tres_miembros(db_session)
    prestamo = _crear(casa.id, admin_id, maca_id, admin_id)
    assert prestamo.estado_confirmacion == "pendiente_confirmacion"

    confirmado = confirmar_prestamo(casa.id, prestamo.id, maca_id, True)

    assert confirmado.confirmado_prestamista is True
    assert confirmado.confirmado_deudor is True
    assert confirmado.estado_confirmacion == "confirmado"


def test_tc006_una_parte_rechaza_queda_rechazado_permanente(db_session):
    casa, admin_id, maca_id, _bruno_id = _armar_casa_con_tres_miembros(db_session)
    prestamo = _crear(casa.id, admin_id, maca_id, admin_id)

    rechazado = confirmar_prestamo(casa.id, prestamo.id, maca_id, False)

    assert rechazado.confirmado_deudor is False
    assert rechazado.estado_confirmacion == "rechazado"

    # Permanente: ni el propio deudor ni el prestamista pueden volver a
    # confirmar/rechazar un préstamo ya rechazado.
    with pytest.raises(ValidationError):
        confirmar_prestamo(casa.id, prestamo.id, maca_id, True)
    with pytest.raises(ValidationError):
        confirmar_prestamo(casa.id, prestamo.id, admin_id, True)


def test_tc005b_confirmar_dos_veces_ya_resuelto_es_rechazado(db_session):
    """Complemento de TC-005: una vez `estado_confirmacion == "confirmado"`,
    ni siquiera la misma parte puede volver a llamar `confirmar_prestamo`."""
    casa, admin_id, maca_id, _bruno_id = _armar_casa_con_tres_miembros(db_session)
    prestamo = _crear(casa.id, admin_id, maca_id, admin_id)
    confirmar_prestamo(casa.id, prestamo.id, maca_id, True)

    with pytest.raises(ValidationError):
        confirmar_prestamo(casa.id, prestamo.id, maca_id, True)


def test_tc007_no_se_puede_cambiar_estado_antes_de_confirmar(db_session):
    casa, admin_id, maca_id, _bruno_id = _armar_casa_con_tres_miembros(db_session)
    prestamo = _crear(casa.id, admin_id, maca_id, admin_id)
    assert prestamo.estado_confirmacion == "pendiente_confirmacion"

    with pytest.raises(ValidationError):
        actualizar_estado_prestamo(casa.id, prestamo.id, "pagado", admin_id)


def test_no_se_puede_cambiar_estado_de_un_prestamo_rechazado(db_session):
    casa, admin_id, maca_id, _bruno_id = _armar_casa_con_tres_miembros(db_session)
    prestamo = _crear(casa.id, admin_id, maca_id, admin_id)
    confirmar_prestamo(casa.id, prestamo.id, maca_id, False)

    with pytest.raises(ValidationError):
        actualizar_estado_prestamo(casa.id, prestamo.id, "pagado", admin_id)


def test_se_puede_cambiar_estado_una_vez_confirmado_por_ambas_partes(db_session):
    casa, admin_id, maca_id, _bruno_id = _armar_casa_con_tres_miembros(db_session)
    prestamo = _crear(casa.id, admin_id, maca_id, admin_id)
    confirmar_prestamo(casa.id, prestamo.id, maca_id, True)

    actualizado = actualizar_estado_prestamo(casa.id, prestamo.id, "pagado", admin_id)
    assert actualizado.estado == "pagado"


def test_confirmar_prestamo_inexistente_lanza_not_found(db_session):
    casa, admin_id, _maca_id, _bruno_id = _armar_casa_con_tres_miembros(db_session)

    with pytest.raises(NotFoundError):
        confirmar_prestamo(casa.id, uuid.uuid4(), admin_id, True)
