"""T2 — Service Layer (unit slice): crear_casa y permisos.puede.

Cubre TC-001, TC-002 y TC-007 (`casas-miembros`), y TC-007 de
`usuarios-auth` (un Usuario que crea 2 casas tiene 2 Miembros propios,
ambos con su mismo `usuario_id`).
"""
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

import src.db.base as db_base
from src.db.models.miembro import RolEnum
from src.services import permisos
from src.services.casa_service import crear_casa
from src.services.exceptions import ValidationError


@pytest.fixture(autouse=True)
def _sqlite_engine(monkeypatch):
    import importlib

    from sqlalchemy.orm import sessionmaker

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    migration = importlib.import_module("src.db.migrations.0001_casas_miembros")
    migration.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr(db_base, "engine", engine)
    monkeypatch.setattr(db_base, "SessionLocal", TestSession)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    yield


def test_crear_casa_asigna_admin_al_creador():
    usuario_creador = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_creador)

    assert casa.nombre == "Casa Brown"
    assert len(casa.miembros) == 1
    admin = casa.miembros[0]
    # Spec `usuarios-auth`: el Miembro admin tiene su propio `id` (no el
    # `usuario_id` del creador) — el vínculo con la identidad real vive
    # en la FK `usuario_id`. Ver Design Rationale de `crear_casa`.
    assert admin.id != usuario_creador
    assert admin.usuario_id == usuario_creador
    assert admin.rol == RolEnum.ADMIN
    assert admin.activo is True


def test_un_usuario_que_crea_dos_casas_tiene_un_miembro_propio_en_cada_una():
    usuario_id = uuid.uuid4()
    casa_1 = crear_casa("Casa Brown", usuario_id)
    casa_2 = crear_casa("Casa Verde", usuario_id)

    admin_1 = casa_1.miembros[0]
    admin_2 = casa_2.miembros[0]

    assert admin_1.id != admin_2.id
    assert admin_1.usuario_id == usuario_id
    assert admin_2.usuario_id == usuario_id


def test_crear_casa_sin_nombre_es_rechazada():
    with pytest.raises(ValidationError):
        crear_casa("", uuid.uuid4())

    with pytest.raises(ValidationError):
        crear_casa("   ", uuid.uuid4())


def test_admin_puede_consultar_todos_los_gastos_sin_restriccion():
    assert permisos.puede(RolEnum.ADMIN, "consultar_todos_gastos") is True


def test_miembro_no_puede_consultar_todos_los_gastos():
    assert permisos.puede(RolEnum.MEMBER, "consultar_todos_gastos") is False
