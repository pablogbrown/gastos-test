"""T3 (spec `tienda-accesorios`) — equipar/desequipar por slot.

Cubre TC-006 (un accesorio comprado y compatible se activa en su slot),
TC-007 (equipar uno no comprado se rechaza) y TC-008 (equipar un segundo
accesorio del mismo slot reemplaza al primero, nunca coexisten dos
activos en el mismo slot).
"""
import importlib
import uuid

import pytest
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models.accesorio_avatar import AccesorioAvatar
from src.db.models.avatar_personaje import AvatarPersonaje
from src.db.models.miembro_avatar_seleccionado import MiembroAvatarSeleccionado
from src.db.models.usuario import Usuario  # noqa: F401 - ver [DBG-06]
from src.services.avatar_service import otorgar_creditos
from src.services.casa_service import crear_casa
from src.services.exceptions import PermissionDeniedError
from src.services.miembro_service import agregar_miembro
from src.services.tienda_service import comprar_accesorio, desequipar_slot, equipar_accesorio, listar_equipados


@pytest.fixture()
def db_session(monkeypatch):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    for nombre in (
        "0001_casas_miembros",
        "0004_historial_actividad",
        "0005_usuarios",
        "0021_creditos",
        "0022_avatar_catalogo",
        "0023_avatar_seleccionado",
        "0024_accesorio_catalogo",
        "0025_accesorio_comprado",
        "0026_accesorio_equipado",
    ):
        importlib.import_module(f"src.db.migrations.{nombre}").upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    for servicio in (
        "casa_service",
        "miembro_service",
        "avatar_service",
        "tienda_service",
        "actividad_service",
    ):
        monkeypatch.setattr(f"src.services.{servicio}.get_session", lambda: TestSession())
    yield TestSession


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


def _casa_con_miembro(session_factory):
    usuario_admin_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_admin_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(session_factory, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)
    return casa, ana


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


def _crear_y_seleccionar_avatar(session_factory, miembro_id, especie):
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
        session.execute(
            insert(MiembroAvatarSeleccionado.__table__),
            [{"miembro_id": miembro_id, "avatar_personaje_id": avatar_id}],
        )
        session.commit()
    finally:
        session.close()
    return avatar_id


def _comprar(session_factory, casa, miembro, accesorio_id, precio):
    otorgar_creditos(casa.id, miembro.id, precio, motivo="tarea_completada")
    comprar_accesorio(miembro.id, accesorio_id)


def test_equipar_un_accesorio_comprado_y_compatible_lo_activa_en_su_slot(db_session):
    """TC-006: un accesorio comprado y compatible con el avatar actual
    queda como el ítem activo de su slot."""
    casa, ana = _casa_con_miembro(db_session)
    _crear_y_seleccionar_avatar(db_session, ana.id, "perro")
    accesorio_id = _insertar_accesorio(db_session, slot="cabeza", especie_compatible="perro", precio_creditos=10)
    _comprar(db_session, casa, ana, accesorio_id, 10)

    equipado = equipar_accesorio(ana.id, accesorio_id)

    assert equipado.slot == "cabeza"
    assert equipado.accesorio_id == accesorio_id
    equipados = {e.slot: e.accesorio_id for e in listar_equipados(ana.id)}
    assert equipados["cabeza"] == accesorio_id


def test_equipar_un_accesorio_no_comprado_se_rechaza(db_session):
    """TC-007: equipar un accesorio que el miembro no compró se
    rechaza."""
    casa, ana = _casa_con_miembro(db_session)
    accesorio_id = _insertar_accesorio(db_session)

    with pytest.raises(PermissionDeniedError):
        equipar_accesorio(ana.id, accesorio_id)


def test_equipar_un_segundo_accesorio_del_mismo_slot_reemplaza_al_primero(db_session):
    """TC-008: equipar un segundo accesorio del mismo slot reemplaza al
    primero — nunca quedan ambos activos a la vez."""
    casa, ana = _casa_con_miembro(db_session)
    primero = _insertar_accesorio(db_session, nombre="Gorro 1", slot="cabeza", precio_creditos=10)
    segundo = _insertar_accesorio(db_session, nombre="Gorro 2", slot="cabeza", precio_creditos=10)
    _comprar(db_session, casa, ana, primero, 10)
    _comprar(db_session, casa, ana, segundo, 10)

    equipar_accesorio(ana.id, primero)
    equipar_accesorio(ana.id, segundo)

    equipados = listar_equipados(ana.id)
    equipados_en_cabeza = [e for e in equipados if e.slot == "cabeza"]
    assert len(equipados_en_cabeza) == 1
    assert equipados_en_cabeza[0].accesorio_id == segundo


def test_equipar_un_accesorio_incompatible_de_especie_se_rechaza(db_session):
    """El accesorio debe ser compatible con la especie del avatar
    actualmente seleccionado (REQ-003) — comprado no alcanza si la
    especie no matchea."""
    casa, ana = _casa_con_miembro(db_session)
    _crear_y_seleccionar_avatar(db_session, ana.id, "gato")
    accesorio_id = _insertar_accesorio(db_session, especie_compatible="perro", precio_creditos=10)
    _comprar(db_session, casa, ana, accesorio_id, 10)

    with pytest.raises(PermissionDeniedError):
        equipar_accesorio(ana.id, accesorio_id)


def test_desequipar_un_slot_lo_deja_vacio(db_session):
    casa, ana = _casa_con_miembro(db_session)
    accesorio_id = _insertar_accesorio(db_session, slot="cuello", precio_creditos=10)
    _comprar(db_session, casa, ana, accesorio_id, 10)
    equipar_accesorio(ana.id, accesorio_id)

    desequipar_slot(ana.id, "cuello")

    assert listar_equipados(ana.id) == []


def test_desequipar_un_slot_vacio_es_no_op(db_session):
    casa, ana = _casa_con_miembro(db_session)

    desequipar_slot(ana.id, "cuerpo")  # no debe lanzar

    assert listar_equipados(ana.id) == []
