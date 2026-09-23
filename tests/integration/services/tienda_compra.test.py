"""T2 (spec `tienda-accesorios`) — inventario + compra (gasta créditos).

Cubre TC-003 (comprar con saldo suficiente descuenta créditos y agrega al
inventario), TC-004 (saldo insuficiente rechaza sin descontar nada),
TC-005 (comprar un ítem ya en el inventario rechaza sin doble descuento)
y TC-010 (un ítem ya comprado sigue visible/equipable en el inventario
aunque esté fuera de ventana).
"""
import importlib
import uuid
from datetime import date, timedelta

import pytest
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models.accesorio_avatar import AccesorioAvatar
from src.db.models.usuario import Usuario  # noqa: F401 - ver [DBG-06]
from src.services.avatar_service import obtener_balance_creditos, otorgar_creditos
from src.services.casa_service import crear_casa
from src.services.exceptions import ConflictError, ValidationError
from src.services.miembro_service import agregar_miembro
from src.services.tienda_service import comprar_accesorio, listar_inventario


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
        "precio_creditos": 20,
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


def test_comprar_con_saldo_suficiente_descuenta_creditos_y_agrega_al_inventario(db_session):
    """TC-003: comprar un accesorio crea una `CreditoTransaccion` negativa
    por su precio y lo agrega al inventario del miembro."""
    casa, ana = _casa_con_miembro(db_session)
    otorgar_creditos(casa.id, ana.id, 50, motivo="tarea_completada")
    accesorio_id = _insertar_accesorio(db_session, precio_creditos=20)

    comprar_accesorio(ana.id, accesorio_id)

    assert obtener_balance_creditos(ana.id) == 30
    inventario_ids = {accesorio.id for accesorio in listar_inventario(ana.id)}
    assert accesorio_id in inventario_ids


def test_comprar_con_saldo_insuficiente_rechaza_sin_descontar_nada(db_session):
    """TC-004: saldo insuficiente rechaza la compra sin descontar nada."""
    casa, ana = _casa_con_miembro(db_session)
    otorgar_creditos(casa.id, ana.id, 10, motivo="tarea_completada")
    accesorio_id = _insertar_accesorio(db_session, precio_creditos=20)

    with pytest.raises(ValidationError):
        comprar_accesorio(ana.id, accesorio_id)

    assert obtener_balance_creditos(ana.id) == 10
    assert listar_inventario(ana.id) == []


def test_comprar_un_accesorio_ya_en_el_inventario_rechaza_sin_doble_descuento(db_session):
    """TC-005: comprar un accesorio ya presente en el inventario del
    miembro se rechaza sin descontar créditos una segunda vez."""
    casa, ana = _casa_con_miembro(db_session)
    otorgar_creditos(casa.id, ana.id, 100, motivo="tarea_completada")
    accesorio_id = _insertar_accesorio(db_session, precio_creditos=20)

    comprar_accesorio(ana.id, accesorio_id)
    assert obtener_balance_creditos(ana.id) == 80

    with pytest.raises(ConflictError):
        comprar_accesorio(ana.id, accesorio_id)

    assert obtener_balance_creditos(ana.id) == 80


def test_accesorio_ya_comprado_sigue_visible_en_el_inventario_aunque_este_fuera_de_ventana(db_session):
    """TC-010: un accesorio ya comprado sigue apareciendo y siendo
    equipable en el inventario del miembro, sin importar que su ventana
    de disponibilidad ya haya cerrado (REQ-004)."""
    casa, ana = _casa_con_miembro(db_session)
    otorgar_creditos(casa.id, ana.id, 100, motivo="tarea_completada")
    accesorio_id = _insertar_accesorio(
        db_session,
        precio_creditos=20,
        disponible_desde=date.today() - timedelta(days=30),
        disponible_hasta=date.today() + timedelta(days=1),
    )
    comprar_accesorio(ana.id, accesorio_id)

    # La ventana cierra DESPUÉS de la compra (simulado editando la fila
    # directamente, sin pasar por el service — el punto de este test es
    # el comportamiento de `listar_inventario`, no el paso del tiempo).
    session = db_session()
    try:
        accesorio = session.get(AccesorioAvatar, accesorio_id)
        accesorio.disponible_hasta = date.today() - timedelta(days=1)
        session.commit()
    finally:
        session.close()

    inventario_ids = {accesorio.id for accesorio in listar_inventario(ana.id)}
    assert accesorio_id in inventario_ids
