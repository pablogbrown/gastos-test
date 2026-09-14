"""T2 — Service Layer (integration slice): agregar/desactivar miembro,
guard de membresía activa y aislamiento entre casas.

Cubre TC-003, TC-005, TC-006, TC-008, TC-009 (`casas-miembros`), y
TC-008 de `usuarios-auth` (agregar miembro por email vincula al Usuario
existente; email inexistente es rechazado).
"""
import importlib
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models.usuario import Usuario
from src.services.casa_service import crear_casa
from src.services.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from src.services.miembro_service import (
    agregar_miembro,
    desactivar_miembro,
    requiere_membresia_activa,
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
    migration = importlib.import_module("src.db.migrations.0001_casas_miembros")
    migration.upgrade(engine)
    # 0005 (spec `usuarios-auth`): `agregar_miembro` ahora exige un
    # Usuario real (por email) para vincular al nuevo Miembro.
    migration_usuarios = importlib.import_module("src.db.migrations.0005_usuarios")
    migration_usuarios.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    yield TestSession


def test_admin_agrega_miembro_valido(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")

    miembro = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)

    assert miembro.nombre == "Ana"
    assert miembro.identificacion == "ANA1"
    assert miembro.activo is True
    assert miembro.rol.value == "member"
    # Spec `usuarios-auth`: el Miembro nuevo queda vinculado al Usuario
    # real encontrado por email (TC-008), no a un id inventado.
    assert miembro.usuario_id == ana_usuario.id


def test_agregar_miembro_con_email_de_usuario_inexistente_es_rechazado(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id

    with pytest.raises(NotFoundError):
        agregar_miembro(casa.id, "Ana", "ANA1", "no-registrado@example.com", admin_id)


def test_miembro_no_admin_no_puede_agregar_miembros(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)

    bruno_usuario = _crear_usuario_de_prueba(db_session, "bruno@example.com")
    with pytest.raises(PermissionDeniedError):
        agregar_miembro(casa.id, "Bruno", "BRU1", bruno_usuario.email, ana.id)


def test_agregar_miembro_con_identificacion_duplicada_es_rechazada(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    otra_ana_usuario = _crear_usuario_de_prueba(db_session, "otra-ana@example.com")
    agregar_miembro(casa.id, "Ana", "P1", ana_usuario.email, admin_id)

    with pytest.raises(ValidationError):
        agregar_miembro(casa.id, "Otra Ana", "P1", otra_ana_usuario.email, admin_id)


def test_desactivar_miembro_preserva_su_identidad_e_historial(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)
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
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)

    desactivar_miembro(casa.id, ana.id, admin_id)

    assert requiere_membresia_activa(casa.id, ana.id) is False


def test_dos_casas_mantienen_miembros_independientes(db_session):
    usuario_1, usuario_2 = uuid.uuid4(), uuid.uuid4()
    casa_1 = crear_casa("Casa Brown", usuario_1)
    casa_2 = crear_casa("Casa Verde", usuario_2)
    admin_1 = casa_1.miembros[0].id
    admin_2 = casa_2.miembros[0].id

    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    bruno_usuario = _crear_usuario_de_prueba(db_session, "bruno@example.com")
    miembro_1 = agregar_miembro(casa_1.id, "Ana", "P1", ana_usuario.email, admin_1)
    miembro_2 = agregar_miembro(casa_2.id, "Bruno", "P1", bruno_usuario.email, admin_2)

    assert requiere_membresia_activa(casa_1.id, miembro_1.id) is True
    assert requiere_membresia_activa(casa_2.id, miembro_1.id) is False
    assert requiere_membresia_activa(casa_2.id, miembro_2.id) is True
    assert requiere_membresia_activa(casa_1.id, miembro_2.id) is False


def test_un_usuario_agregado_a_una_segunda_casa_por_email_comparte_su_usuario_id(db_session):
    """TC-007/TC-008 (`usuarios-auth`): un Usuario que ya administra su
    propia Casa puede además ser agregado como Miembro de otra Casa por
    su email — ambas filas Miembro comparten el mismo `usuario_id`."""
    usuario_multi = _crear_usuario_de_prueba(db_session, "multi@example.com")
    casa_propia = crear_casa("Casa de Multi", usuario_multi.id)
    admin_propio = casa_propia.miembros[0].id

    otro_usuario_id = uuid.uuid4()
    casa_ajena = crear_casa("Casa Ajena", otro_usuario_id)
    admin_ajeno = casa_ajena.miembros[0].id

    miembro_en_casa_ajena = agregar_miembro(
        casa_ajena.id, "Multi", "MULTI1", usuario_multi.email, admin_ajeno
    )

    assert miembro_en_casa_ajena.usuario_id == usuario_multi.id
    assert admin_propio != miembro_en_casa_ajena.id
    assert requiere_membresia_activa(casa_propia.id, admin_propio) is True
    assert requiere_membresia_activa(casa_ajena.id, miembro_en_casa_ajena.id) is True
