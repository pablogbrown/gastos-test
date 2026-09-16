"""T2 (spec `mantenimiento-autos`) — Servicio de Auto: alta y listado.

Cubre TC-001.
"""
import importlib
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.services.auto_service import crear_auto, listar_autos
from src.services.casa_service import crear_casa
from src.services.exceptions import PermissionDeniedError, ValidationError


@pytest.fixture()
def db_session(monkeypatch):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    migration_casas = importlib.import_module("src.db.migrations.0001_casas_miembros")
    migration_mantenimiento = importlib.import_module("src.db.migrations.0017_mantenimiento")
    migration_autos = importlib.import_module("src.db.migrations.0018_mantenimiento_autos")
    migration_casas.upgrade(engine)
    migration_mantenimiento.upgrade(engine)
    migration_autos.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.auto_service.get_session", lambda: TestSession())
    yield TestSession


def _armar_casa():
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    return casa, admin_id


def test_tc001_alta_de_auto_con_datos_validos_persiste_y_aparece_en_el_listado(db_session):
    casa, admin_id = _armar_casa()

    auto = crear_auto(casa.id, "Toyota", "Corolla", admin_id, patente="AB123CD", anio=2020)

    assert auto.marca == "Toyota"
    assert auto.modelo == "Corolla"
    assert auto.patente == "AB123CD"
    assert auto.anio == 2020

    listado = listar_autos(casa.id)
    assert len(listado) == 1
    assert listado[0].id == auto.id


def test_alta_de_auto_sin_patente_ni_anio_es_valida(db_session):
    casa, admin_id = _armar_casa()

    auto = crear_auto(casa.id, "Ford", "Fiesta", admin_id)

    assert auto.patente is None
    assert auto.anio is None


def test_marca_vacia_es_rechazada(db_session):
    casa, admin_id = _armar_casa()

    with pytest.raises(ValidationError):
        crear_auto(casa.id, "", "Corolla", admin_id)


def test_modelo_vacio_es_rechazado(db_session):
    casa, admin_id = _armar_casa()

    with pytest.raises(ValidationError):
        crear_auto(casa.id, "Toyota", "", admin_id)


def test_crear_auto_sin_actor_miembro_activo_es_rechazado(db_session):
    casa, _admin_id = _armar_casa()
    ajeno = uuid.uuid4()

    with pytest.raises(PermissionDeniedError):
        crear_auto(casa.id, "Toyota", "Corolla", ajeno)


def test_crear_auto_sin_actor_miembro_activo_es_rechazado_con_permission_denied(db_session):
    # Mismo orden de guards que `crear_tarjeta`/`crear_item`: el actor debe
    # ser miembro activo de la casa antes de llegar al chequeo de
    # existencia de la casa — con un `casa_id`/`actor` inventados, el
    # guard de membresía es el que dispara (no hay test equivalente a
    # "casa inexistente" en `tarjeta_service.test.py` por la misma razón:
    # esa rama es inalcanzable vía la API pública, siempre gana el guard
    # de membresía primero).
    with pytest.raises(PermissionDeniedError):
        crear_auto(uuid.uuid4(), "Toyota", "Corolla", uuid.uuid4())


def test_listar_autos_de_casa_sin_autos_devuelve_vacio(db_session):
    casa, _admin_id = _armar_casa()

    assert listar_autos(casa.id) == []
