"""T2 (spec `prestamos-entre-miembros`) — Servicio de préstamos: alta,
listado y cambio de estado.

Cubre TC-001 a TC-006 (TC-006 es un control de regresión: crear/
actualizar un préstamo nunca cambia `balance_service.calcular_balance`).
"""
import importlib
import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models.usuario import Usuario
from src.services.balance_service import calcular_balance
from src.services.casa_service import crear_casa
from src.services.exceptions import NotFoundError, ValidationError
from src.services.miembro_service import agregar_miembro
from src.services.prestamo_service import (
    ESTADOS_PRESTAMO_VALIDOS,
    actualizar_estado_prestamo,
    confirmar_prestamo,
    crear_prestamo,
    listar_prestamos,
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
    # (mismo motivo que `gasto_service.test.py`).
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
    monkeypatch.setattr("src.services.balance_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.actividad_service.get_session", lambda: TestSession())
    yield TestSession


def _armar_casa_con_dos_miembros(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    maca_usuario = _crear_usuario_de_prueba(db_session, "maca@example.com")
    maca = agregar_miembro(casa.id, "Maca", "MACA1", maca_usuario.email, admin_id)
    return casa, admin_id, maca.id


def test_tc001_alta_con_datos_validos_persiste_pendiente(db_session):
    casa, admin_id, maca_id = _armar_casa_con_dos_miembros(db_session)

    prestamo = crear_prestamo(
        casa.id,
        admin_id,
        maca_id,
        Decimal("50000.00"),
        "ARS",
        date(2026, 9, 1),
        admin_id,
        descripcion="Alquiler del auto",
    )

    assert prestamo.estado == "pendiente"
    assert prestamo.prestamista_id == admin_id
    assert prestamo.deudor_id == maca_id
    assert prestamo.importe == Decimal("50000.00")
    assert prestamo.moneda == "ARS"
    assert prestamo.descripcion == "Alquiler del auto"

    listado = listar_prestamos(casa.id)
    assert len(listado) == 1
    assert listado[0].id == prestamo.id


def test_tc002_prestamista_igual_a_deudor_es_rechazado(db_session):
    casa, admin_id, _maca_id = _armar_casa_con_dos_miembros(db_session)

    with pytest.raises(ValidationError):
        crear_prestamo(
            casa.id,
            admin_id,
            admin_id,
            Decimal("1000.00"),
            "ARS",
            date(2026, 9, 1),
            admin_id,
        )


def test_tc003_moneda_invalida_es_rechazada(db_session):
    casa, admin_id, maca_id = _armar_casa_con_dos_miembros(db_session)

    with pytest.raises(ValidationError):
        crear_prestamo(
            casa.id,
            admin_id,
            maca_id,
            Decimal("1000.00"),
            "EUR",
            date(2026, 9, 1),
            admin_id,
        )


def test_tc004_cambio_de_estado_en_ambos_sentidos(db_session):
    casa, admin_id, maca_id = _armar_casa_con_dos_miembros(db_session)
    prestamo = crear_prestamo(
        casa.id, admin_id, maca_id, Decimal("1000.00"), "ARS", date(2026, 9, 1), admin_id
    )
    assert prestamo.estado == "pendiente"
    # Spec `prestamos-confirmacion-mutua` (REQ-006): el ciclo pagado/
    # pendiente exige confirmación de ambas partes primero.
    confirmar_prestamo(casa.id, prestamo.id, maca_id, True)

    actualizado = actualizar_estado_prestamo(casa.id, prestamo.id, "pagado", admin_id)
    assert actualizado.estado == "pagado"

    de_vuelta = actualizar_estado_prestamo(casa.id, prestamo.id, "pendiente", admin_id)
    assert de_vuelta.estado == "pendiente"


def test_estado_invalido_es_rechazado(db_session):
    casa, admin_id, maca_id = _armar_casa_con_dos_miembros(db_session)
    prestamo = crear_prestamo(
        casa.id, admin_id, maca_id, Decimal("1000.00"), "ARS", date(2026, 9, 1), admin_id
    )
    confirmar_prestamo(casa.id, prestamo.id, maca_id, True)
    assert "pendiente" in ESTADOS_PRESTAMO_VALIDOS and "pagado" in ESTADOS_PRESTAMO_VALIDOS

    with pytest.raises(ValidationError):
        actualizar_estado_prestamo(casa.id, prestamo.id, "vencido", admin_id)


def test_tc005_listado_ordenado_por_fecha_descendente(db_session):
    casa, admin_id, maca_id = _armar_casa_con_dos_miembros(db_session)
    hoy = date(2026, 9, 10)

    mas_viejo = crear_prestamo(
        casa.id, admin_id, maca_id, Decimal("100.00"), "ARS", hoy - timedelta(days=5), admin_id
    )
    mas_nuevo = crear_prestamo(
        casa.id, admin_id, maca_id, Decimal("200.00"), "ARS", hoy, admin_id
    )
    intermedio = crear_prestamo(
        casa.id, admin_id, maca_id, Decimal("300.00"), "ARS", hoy - timedelta(days=2), admin_id
    )

    listado = listar_prestamos(casa.id)
    assert [p.id for p in listado] == [mas_nuevo.id, intermedio.id, mas_viejo.id]


def test_tc006_control_crear_y_actualizar_prestamo_no_cambia_el_balance(db_session):
    """Control de regresión (REQ-005): `balance_service.calcular_balance`
    debe devolver exactamente lo mismo antes y después de crear un
    préstamo, y de nuevo después de actualizar su estado — un préstamo no
    toca `Gasto`/`GastoParticipante` en absoluto."""
    casa, admin_id, maca_id = _armar_casa_con_dos_miembros(db_session)
    mes_actual = date.today().strftime("%Y-%m")

    balance_antes = calcular_balance(casa.id, mes_actual)

    prestamo = crear_prestamo(
        casa.id,
        admin_id,
        maca_id,
        Decimal("50000.00"),
        "ARS",
        date.today(),
        admin_id,
    )

    balance_despues_de_crear = calcular_balance(casa.id, mes_actual)
    assert balance_despues_de_crear == balance_antes

    confirmar_prestamo(casa.id, prestamo.id, maca_id, True)
    actualizar_estado_prestamo(casa.id, prestamo.id, "pagado", admin_id)

    balance_despues_de_actualizar = calcular_balance(casa.id, mes_actual)
    assert balance_despues_de_actualizar == balance_antes


def test_prestamista_o_deudor_inexistente_en_la_casa_es_rechazado(db_session):
    casa, admin_id, _maca_id = _armar_casa_con_dos_miembros(db_session)
    inexistente = uuid.uuid4()

    with pytest.raises(NotFoundError):
        crear_prestamo(
            casa.id,
            admin_id,
            inexistente,
            Decimal("1000.00"),
            "ARS",
            date(2026, 9, 1),
            admin_id,
        )


def test_actor_no_necesita_ser_prestamista_ni_deudor(db_session):
    """Tradeoff documentado en `00-overview.md`: cualquier miembro activo
    de la casa puede registrar un préstamo entre otros dos miembros."""
    casa, admin_id, maca_id = _armar_casa_con_dos_miembros(db_session)
    bruno_usuario = _crear_usuario_de_prueba(db_session, "bruno@example.com")
    bruno = agregar_miembro(casa.id, "Bruno", "BRU1", bruno_usuario.email, admin_id)

    # Bruno (actor) registra un préstamo entre admin y Maca, sin ser
    # ninguno de los dos.
    prestamo = crear_prestamo(
        casa.id,
        admin_id,
        maca_id,
        Decimal("1000.00"),
        "ARS",
        date(2026, 9, 1),
        bruno.id,
    )
    assert prestamo.prestamista_id == admin_id
    assert prestamo.deudor_id == maca_id
