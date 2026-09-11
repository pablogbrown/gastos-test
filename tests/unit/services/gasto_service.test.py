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


def test_gasto_sin_participantes_explicitos_se_divide_entre_todos_los_activos(db_session):
    casa, admin_id, categoria = _casa_con_categoria(db_session)
    agregar_miembro(
        casa.id, "Ana", "ANA1", _crear_usuario_de_prueba(db_session, "ana@example.com").email, admin_id
    )
    agregar_miembro(
        casa.id, "Bruno", "BRU1", _crear_usuario_de_prueba(db_session, "bruno@example.com").email, admin_id
    )
    agregar_miembro(
        casa.id, "Carla", "CAR1", _crear_usuario_de_prueba(db_session, "carla@example.com").email, admin_id
    )
    # 4 miembros activos en total (admin + 3).

    gasto = registrar_gasto(
        casa.id,
        "Gasto compartido",
        Decimal("40000.00"),
        date(2026, 1, 1),
        categoria.id,
        admin_id,
        admin_id,
    )

    assert len(gasto.participantes) == 4


def test_gasto_con_participantes_explicitos_solo_los_afecta_a_ellos(db_session):
    casa, admin_id, categoria = _casa_con_categoria(db_session)
    ana = agregar_miembro(
        casa.id, "Ana", "ANA1", _crear_usuario_de_prueba(db_session, "ana@example.com").email, admin_id
    )
    agregar_miembro(
        casa.id, "Bruno", "BRU1", _crear_usuario_de_prueba(db_session, "bruno@example.com").email, admin_id
    )
    agregar_miembro(
        casa.id, "Carla", "CAR1", _crear_usuario_de_prueba(db_session, "carla@example.com").email, admin_id
    )

    gasto = registrar_gasto(
        casa.id,
        "Cena",
        Decimal("30000.00"),
        date(2026, 1, 1),
        categoria.id,
        admin_id,
        admin_id,
        participantes=[admin_id, ana.id],
    )

    ids_participantes = {p.miembro_id for p in gasto.participantes}
    assert ids_participantes == {admin_id, ana.id}


def test_division_de_40000_entre_4_participantes_da_10000_cada_uno(db_session):
    casa, admin_id, categoria = _casa_con_categoria(db_session)
    ana = agregar_miembro(
        casa.id, "Ana", "ANA1", _crear_usuario_de_prueba(db_session, "ana@example.com").email, admin_id
    )
    bruno = agregar_miembro(
        casa.id, "Bruno", "BRU1", _crear_usuario_de_prueba(db_session, "bruno@example.com").email, admin_id
    )
    carla = agregar_miembro(
        casa.id, "Carla", "CAR1", _crear_usuario_de_prueba(db_session, "carla@example.com").email, admin_id
    )

    gasto = registrar_gasto(
        casa.id,
        "Gasto compartido",
        Decimal("40000.00"),
        date(2026, 1, 1),
        categoria.id,
        admin_id,
        admin_id,
        participantes=[admin_id, ana.id, bruno.id, carla.id],
    )

    for participante in gasto.participantes:
        assert participante.monto_correspondiente == Decimal("10000.00")
    assert sum(p.monto_correspondiente for p in gasto.participantes) == gasto.importe


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
