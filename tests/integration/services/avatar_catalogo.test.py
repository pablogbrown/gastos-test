"""T2 (spec `avatares-economia`) — catálogo `AvatarPersonaje` + seed.

Cubre TC-003 (el catálogo expone especie/nombre/nivel/rareza/asset) y
TC-004, primera mitad (una raza fuera de ventana no aparece para quien
nunca la eligió). La segunda mitad de TC-004 ("ya seleccionada" se
conserva) se cubre en `avatar_seleccion.test.py` (T3): `listar_catalogo`
ya consulta `MiembroAvatarSeleccionado` incondicionalmente (T3 la
extendió), así que esta fixture migra también `0023` aunque este archivo
no ejercite esa mitad directamente.
"""
import importlib
import uuid
from datetime import date, timedelta

import pytest
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models.avatar_personaje import AvatarPersonaje

# `src/db/models/__init__.py` importa `Miembro` en cuanto se importa
# cualquier cosa bajo `src.db.models.*` (como `AvatarPersonaje` arriba) —
# `Miembro.usuario = relationship("Usuario", ...)` necesita esta clase ya
# registrada para que SQLAlchemy pueda configurar TODOS los mappers
# pendientes en la primera query de este archivo (aunque este test nunca
# cree un Usuario real). Mismo gotcha ya resuelto en cada fixture
# existente que importa `Usuario` para `_crear_usuario_de_prueba` — acá
# no hace falta esa función, solo el import.
from src.db.models.usuario import Usuario  # noqa: F401
from src.services.avatar_service import listar_catalogo


@pytest.fixture()
def db_session(monkeypatch):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    migracion_casas = importlib.import_module("src.db.migrations.0001_casas_miembros")
    migracion_catalogo = importlib.import_module("src.db.migrations.0022_avatar_catalogo")
    # 0023 (spec `avatares-economia`, T3): `listar_catalogo` ya consulta
    # `MiembroAvatarSeleccionado` incondicionalmente (ver docstring de
    # este archivo).
    migracion_seleccion = importlib.import_module("src.db.migrations.0023_avatar_seleccionado")
    migracion_casas.upgrade(engine)
    migracion_catalogo.upgrade(engine)
    migracion_seleccion.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.avatar_service.get_session", lambda: TestSession())
    yield TestSession


def test_el_seed_siembra_al_menos_una_raza_por_nivel(db_session):
    """Done When de T2: el seed inserta al menos una raza por cada uno de
    los 4 niveles."""
    catalogo = listar_catalogo(uuid.uuid4())
    niveles_presentes = {avatar.nivel_requerido for avatar in catalogo}
    assert niveles_presentes == {"Novato", "Activo", "Comprometido", "Campeón de la casa"}
    assert len(catalogo) >= 8


def test_catalogo_expone_especie_nombre_nivel_rareza_y_asset(db_session):
    """TC-003: cada entrada expone especie, nombre, nivel_requerido,
    rareza y la URL del asset Lottie."""
    catalogo = listar_catalogo(uuid.uuid4())
    assert len(catalogo) > 0
    for avatar in catalogo:
        assert avatar.especie in ("perro", "gato")
        assert avatar.raza
        assert avatar.nivel_requerido
        assert avatar.rareza
        assert avatar.lottie_url.startswith("https://")


def test_raza_fuera_de_ventana_no_aparece_para_quien_nunca_la_eligio(db_session):
    """TC-004 (primera mitad): una raza con `disponible_hasta` en el
    pasado no aparece en el catálogo seleccionable."""
    session = db_session()
    try:
        session.execute(
            insert(AvatarPersonaje.__table__),
            [
                {
                    "id": uuid.uuid4(),
                    "especie": "perro",
                    "raza": "Edición limitada vencida",
                    "lottie_url": "https://assets.lottiefiles.com/packages/lf20_vencida.json",
                    "nivel_requerido": "Novato",
                    "rareza": "épico",
                    "disponible_desde": date.today() - timedelta(days=30),
                    "disponible_hasta": date.today() - timedelta(days=1),
                }
            ],
        )
        session.commit()
    finally:
        session.close()

    catalogo = listar_catalogo(uuid.uuid4())
    razas = {avatar.raza for avatar in catalogo}
    assert "Edición limitada vencida" not in razas


def test_raza_dentro_de_ventana_vigente_si_aparece(db_session):
    session = db_session()
    try:
        session.execute(
            insert(AvatarPersonaje.__table__),
            [
                {
                    "id": uuid.uuid4(),
                    "especie": "gato",
                    "raza": "Edición limitada vigente",
                    "lottie_url": "https://assets.lottiefiles.com/packages/lf20_vigente.json",
                    "nivel_requerido": "Novato",
                    "rareza": "épico",
                    "disponible_desde": date.today() - timedelta(days=1),
                    "disponible_hasta": date.today() + timedelta(days=30),
                }
            ],
        )
        session.commit()
    finally:
        session.close()

    catalogo = listar_catalogo(uuid.uuid4())
    razas = {avatar.raza for avatar in catalogo}
    assert "Edición limitada vigente" in razas


def test_migracion_es_idempotente_no_duplica_el_seed(db_session):
    """La migración corre limpia sobre una base ya poblada (Done When de
    T1, aplicado igual acá): correrla una segunda vez no duplica filas."""
    engine = db_session.kw["bind"]
    migracion_catalogo = importlib.import_module("src.db.migrations.0022_avatar_catalogo")
    conteo_antes = len(listar_catalogo(uuid.uuid4()))

    migracion_catalogo.upgrade(engine)

    conteo_despues = len(listar_catalogo(uuid.uuid4()))
    assert conteo_antes == conteo_despues
