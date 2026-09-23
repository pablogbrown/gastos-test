"""T1 (spec `tienda-accesorios`) — catálogo `AccesorioAvatar` + seed +
filtro por especie/ventana.

Cubre TC-001 (el catálogo expone slot/rareza/precio/especie/asset por
ítem), TC-002 (un accesorio incompatible de especie no aparece para el
avatar actual del miembro) y TC-009 (un accesorio fuera de ventana no
aparece en el catálogo de compra).
"""
import importlib
import uuid
from datetime import date, timedelta

import pytest
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models.accesorio_avatar import AccesorioAvatar
from src.db.models.avatar_personaje import AvatarPersonaje
from src.db.models.miembro_avatar_seleccionado import MiembroAvatarSeleccionado

# `src/db/models/__init__.py` importa `Miembro` en cuanto se importa
# cualquier cosa bajo `src.db.models.*` — `Miembro.usuario = relationship(
# "Usuario", ...)` necesita esta clase ya registrada para que SQLAlchemy
# pueda configurar todos los mappers pendientes ([DBG-06],
# `.nybo/memory/domains/db.md`), aunque este archivo nunca cree un
# Usuario real.
from src.db.models.usuario import Usuario  # noqa: F401
from src.services.avatar_service import seleccionar_avatar
from src.services.tienda_service import listar_catalogo_accesorios


@pytest.fixture()
def db_session(monkeypatch):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    for nombre in (
        "0001_casas_miembros",
        "0003_tareas",
        "0004_historial_actividad",
        "0020_gamificacion",
        "0022_avatar_catalogo",
        "0023_avatar_seleccionado",
        "0024_accesorio_catalogo",
    ):
        importlib.import_module(f"src.db.migrations.{nombre}").upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.avatar_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.tienda_service.get_session", lambda: TestSession())
    yield TestSession


def _crear_avatar_de_especie(session_factory, especie):
    """Inserta una raza `AvatarPersonaje` mínima de la especie dada y
    devuelve su id — el seed real de `0022` ya trae razas por especie,
    pero una fila propia evita acoplar este test al contenido exacto del
    seed."""
    avatar_id = uuid.uuid4()
    session = session_factory()
    try:
        session.execute(
            insert(AvatarPersonaje.__table__),
            [
                {
                    "id": avatar_id,
                    "especie": especie,
                    "raza": f"Raza de prueba {especie}",
                    "lottie_url": "https://assets.lottiefiles.com/packages/lf20_prueba.json",
                    "nivel_requerido": "Novato",
                    "rareza": "común",
                }
            ],
        )
        session.commit()
    finally:
        session.close()
    return avatar_id


def _seleccionar(session_factory, miembro_id, avatar_personaje_id):
    session = session_factory()
    try:
        session.execute(
            insert(MiembroAvatarSeleccionado.__table__),
            [{"miembro_id": miembro_id, "avatar_personaje_id": avatar_personaje_id}],
        )
        session.commit()
    finally:
        session.close()


def _insertar_accesorio(session_factory, **overrides):
    accesorio_id = uuid.uuid4()
    fila = {
        "id": accesorio_id,
        "nombre": "Accesorio de prueba",
        "slot": "cabeza",
        "rareza": "común",
        "precio_creditos": 10,
        "especie_compatible": "ambos",
        "asset_overlay_url": "https://assets.lottiefiles.com/packages/lf20_overlay_prueba.json",
        "disponible_desde": None,
        "disponible_hasta": None,
    }
    fila.update(overrides)
    session = session_factory()
    try:
        session.execute(insert(AccesorioAvatar.__table__), [fila])
        session.commit()
    finally:
        session.close()
    return accesorio_id


def test_el_seed_siembra_los_3_slots_y_al_menos_un_item_ambos(db_session):
    """Done When de T1: el seed cubre `cabeza`/`cuello`/`cuerpo` y al
    menos un ítem de especie `ambos`."""
    catalogo = listar_catalogo_accesorios(uuid.uuid4())
    slots_presentes = {accesorio.slot for accesorio in catalogo}
    assert slots_presentes == {"cabeza", "cuello", "cuerpo"}
    assert any(accesorio.especie_compatible == "ambos" for accesorio in catalogo)


def test_catalogo_expone_slot_rareza_precio_especie_y_asset(db_session):
    """TC-001: cada accesorio expone slot, rareza, precio, especie
    compatible y la URL del asset de overlay."""
    catalogo = listar_catalogo_accesorios(uuid.uuid4())
    assert len(catalogo) > 0
    for accesorio in catalogo:
        assert accesorio.slot in ("cabeza", "cuello", "cuerpo")
        assert accesorio.rareza
        assert isinstance(accesorio.precio_creditos, int)
        assert accesorio.especie_compatible in ("perro", "gato", "ambos")
        assert accesorio.asset_overlay_url.startswith("https://")


def test_accesorio_de_especie_incompatible_no_aparece_para_el_avatar_actual(db_session):
    """TC-002: un miembro con un avatar de especie "perro" seleccionado no
    ve los accesorios compatibles solo con "gato" (y viceversa); un ítem
    "ambos" siempre aparece, sin importar la especie del avatar."""
    miembro_id = uuid.uuid4()
    avatar_perro_id = _crear_avatar_de_especie(db_session, "perro")
    _seleccionar(db_session, miembro_id, avatar_perro_id)

    solo_gato = _insertar_accesorio(db_session, nombre="Collar de gato", especie_compatible="gato")
    solo_perro = _insertar_accesorio(db_session, nombre="Correa de perro", especie_compatible="perro")
    ambos = _insertar_accesorio(db_session, nombre="Bufanda universal", especie_compatible="ambos")

    catalogo = listar_catalogo_accesorios(miembro_id)
    ids_catalogo = {accesorio.id for accesorio in catalogo}

    assert solo_gato not in ids_catalogo
    assert solo_perro in ids_catalogo
    assert ambos in ids_catalogo


def test_sin_avatar_seleccionado_el_catalogo_no_se_filtra_por_especie(db_session):
    """Sin avatar seleccionado, se muestra el catálogo completo sin
    filtrar por especie (spec.md, REQ-001)."""
    miembro_sin_avatar = uuid.uuid4()
    solo_gato = _insertar_accesorio(db_session, nombre="Collar de gato", especie_compatible="gato")
    solo_perro = _insertar_accesorio(db_session, nombre="Correa de perro", especie_compatible="perro")

    catalogo = listar_catalogo_accesorios(miembro_sin_avatar)
    ids_catalogo = {accesorio.id for accesorio in catalogo}

    assert solo_gato in ids_catalogo
    assert solo_perro in ids_catalogo


def test_accesorio_fuera_de_ventana_no_aparece_en_el_catalogo_de_compra(db_session):
    """TC-009: un accesorio con `disponible_hasta` en el pasado no
    aparece en el catálogo de compra para quien no lo tiene."""
    miembro_id = uuid.uuid4()
    vencido = _insertar_accesorio(
        db_session,
        nombre="Gorro de temporada vencido",
        disponible_desde=date.today() - timedelta(days=30),
        disponible_hasta=date.today() - timedelta(days=1),
    )
    vigente = _insertar_accesorio(
        db_session,
        nombre="Gorro de temporada vigente",
        disponible_desde=date.today() - timedelta(days=1),
        disponible_hasta=date.today() + timedelta(days=30),
    )

    catalogo = listar_catalogo_accesorios(miembro_id)
    ids_catalogo = {accesorio.id for accesorio in catalogo}

    assert vencido not in ids_catalogo
    assert vigente in ids_catalogo
