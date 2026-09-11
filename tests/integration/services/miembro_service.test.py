"""T2 — Service Layer (integration slice): agregar/desactivar miembro,
guard de membresía activa y aislamiento entre casas.

Cubre TC-003, TC-005, TC-006, TC-008, TC-009.
"""
import importlib
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.services.casa_service import crear_casa
from src.services.exceptions import PermissionDeniedError, ValidationError
from src.services.miembro_service import (
    agregar_miembro,
    desactivar_miembro,
    requiere_membresia_activa,
)


@pytest.fixture()
def db_session(monkeypatch):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    migration = importlib.import_module("src.db.migrations.0001_casas_miembros")
    migration.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    yield TestSession


def test_admin_agrega_miembro_valido(db_session):
    admin_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", admin_id)

    miembro = agregar_miembro(casa.id, "Ana", "ANA1", admin_id)

    assert miembro.nombre == "Ana"
    assert miembro.identificacion == "ANA1"
    assert miembro.activo is True
    assert miembro.rol.value == "member"


def test_miembro_no_admin_no_puede_agregar_miembros(db_session):
    admin_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", admin_id)
    ana = agregar_miembro(casa.id, "Ana", "ANA1", admin_id)

    with pytest.raises(PermissionDeniedError):
        agregar_miembro(casa.id, "Bruno", "BRU1", ana.id)


def test_agregar_miembro_con_identificacion_duplicada_es_rechazada(db_session):
    admin_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", admin_id)
    agregar_miembro(casa.id, "Ana", "P1", admin_id)

    with pytest.raises(ValidationError):
        agregar_miembro(casa.id, "Otra Ana", "P1", admin_id)


def test_desactivar_miembro_preserva_su_identidad_e_historial(db_session):
    admin_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", admin_id)
    ana = agregar_miembro(casa.id, "Ana", "ANA1", admin_id)
    ana_id_original = ana.id

    desactivado = desactivar_miembro(casa.id, ana.id, admin_id)

    assert desactivado.activo is False
    # La fila (y por lo tanto cualquier gasto/tarea que referencie este
    # id de miembro) sigue existiendo con el mismo id — no hay borrado
    # físico, solo el flag activo cambia.
    assert desactivado.id == ana_id_original
    assert desactivado.nombre == "Ana"
    assert desactivado.identificacion == "ANA1"


def test_usuario_sin_casa_no_esta_habilitado_para_registrar_gasto(db_session):
    casa = crear_casa("Casa Brown", uuid.uuid4())
    usuario_ajeno = uuid.uuid4()

    assert requiere_membresia_activa(casa.id, usuario_ajeno) is False


def test_miembro_desactivado_no_cuenta_como_membresia_activa(db_session):
    admin_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", admin_id)
    ana = agregar_miembro(casa.id, "Ana", "ANA1", admin_id)

    desactivar_miembro(casa.id, ana.id, admin_id)

    assert requiere_membresia_activa(casa.id, ana.id) is False


def test_dos_casas_mantienen_miembros_independientes(db_session):
    admin_1, admin_2 = uuid.uuid4(), uuid.uuid4()
    casa_1 = crear_casa("Casa Brown", admin_1)
    casa_2 = crear_casa("Casa Verde", admin_2)

    miembro_1 = agregar_miembro(casa_1.id, "Ana", "P1", admin_1)
    miembro_2 = agregar_miembro(casa_2.id, "Bruno", "P1", admin_2)

    assert requiere_membresia_activa(casa_1.id, miembro_1.id) is True
    assert requiere_membresia_activa(casa_2.id, miembro_1.id) is False
    assert requiere_membresia_activa(casa_2.id, miembro_2.id) is True
    assert requiere_membresia_activa(casa_1.id, miembro_2.id) is False
