"""T1 — Data Layer: Usuario y FK Miembro.usuario_id.

Cubre el "Done When" de T1: la migración 0005 corre limpia sobre una base
con las 4 migraciones anteriores ya aplicadas, y `usuarios.email` rechaza
duplicados a nivel de constraint.
"""
import importlib
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models.casa import Casa
from src.db.models.miembro import Miembro, RolEnum
from src.db.models.usuario import Usuario

_MIGRACIONES = (
    "0001_casas_miembros",
    "0002_gastos",
    "0003_tareas",
    "0004_historial_actividad",
    "0005_usuarios",
)


def _engine_migrado():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    for nombre in _MIGRACIONES:
        importlib.import_module(f"src.db.migrations.{nombre}").upgrade(engine)
    return engine


@pytest.fixture()
def session():
    engine = _engine_migrado()
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        yield db
    finally:
        db.close()


def test_migracion_0005_corre_limpia_sobre_base_con_las_4_anteriores_aplicadas():
    # No debe lanzar sobre una base que ya tiene 0001-0004 aplicadas.
    _engine_migrado()


def test_crear_usuario_valido(session):
    usuario = Usuario(
        id=uuid.uuid4(),
        email="pablo@example.com",
        password_hash="hash-no-es-texto-plano",
        nombre="Pablo",
    )
    session.add(usuario)
    session.commit()

    persisted = session.query(Usuario).one()
    assert persisted.email == "pablo@example.com"
    assert persisted.password_hash == "hash-no-es-texto-plano"


def test_email_duplicado_falla_constraint(session):
    session.add(
        Usuario(id=uuid.uuid4(), email="dup@example.com", password_hash="h1")
    )
    session.commit()

    session.add(
        Usuario(id=uuid.uuid4(), email="dup@example.com", password_hash="h2")
    )
    with pytest.raises(IntegrityError):
        session.commit()


def test_miembro_usuario_id_es_nullable_y_puede_vincularse_a_un_usuario(session):
    casa = Casa(id=uuid.uuid4(), nombre="Casa Brown")
    session.add(casa)
    session.commit()

    # Nullable: preserva filas sembradas antes de esta spec.
    miembro_sin_usuario = Miembro(
        id=uuid.uuid4(),
        casa_id=casa.id,
        nombre="Legacy",
        identificacion="LEG1",
        rol=RolEnum.MEMBER,
    )
    session.add(miembro_sin_usuario)
    session.commit()
    assert miembro_sin_usuario.usuario_id is None

    usuario = Usuario(id=uuid.uuid4(), email="ana@example.com", password_hash="h")
    session.add(usuario)
    session.commit()

    miembro_con_usuario = Miembro(
        id=uuid.uuid4(),
        casa_id=casa.id,
        usuario_id=usuario.id,
        nombre="Ana",
        identificacion="ANA1",
        rol=RolEnum.MEMBER,
    )
    session.add(miembro_con_usuario)
    session.commit()

    assert miembro_con_usuario.usuario_id == usuario.id


def test_un_usuario_puede_tener_miembros_en_varias_casas(session):
    casa_1 = Casa(id=uuid.uuid4(), nombre="Casa Brown")
    casa_2 = Casa(id=uuid.uuid4(), nombre="Casa Verde")
    usuario = Usuario(id=uuid.uuid4(), email="multi@example.com", password_hash="h")
    session.add_all([casa_1, casa_2, usuario])
    session.commit()

    session.add_all(
        [
            Miembro(
                id=uuid.uuid4(),
                casa_id=casa_1.id,
                usuario_id=usuario.id,
                nombre="Multi",
                identificacion="M1",
                rol=RolEnum.ADMIN,
            ),
            Miembro(
                id=uuid.uuid4(),
                casa_id=casa_2.id,
                usuario_id=usuario.id,
                nombre="Multi",
                identificacion="M1",
                rol=RolEnum.ADMIN,
            ),
        ]
    )
    # No debe lanzar: dos Miembro distintos, mismo usuario_id.
    session.commit()

    miembros_del_usuario = (
        session.query(Miembro).filter(Miembro.usuario_id == usuario.id).all()
    )
    assert len(miembros_del_usuario) == 2
