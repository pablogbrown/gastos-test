"""T2 (spec `mantenimiento-autos`) — `mantenimiento_service` extendido
con `auto_id`: alta asociada a un auto, filtrado por auto, rechazo de un
auto de otra casa, y alerta con `auto_id`/`auto_nombre`.

Cubre TC-002 a TC-005.
"""
import importlib
import uuid
from datetime import date, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.services.auto_service import crear_auto
from src.services.casa_service import crear_casa
from src.services.exceptions import NotFoundError
from src.services.mantenimiento_service import (
    crear_item,
    listar_items,
    obtener_items_con_alerta,
)


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
    monkeypatch.setattr("src.services.mantenimiento_service.get_session", lambda: TestSession())
    yield TestSession


def _armar_casa():
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    return casa, admin_id


def test_tc002_item_con_auto_id_valido_queda_asociado_a_ese_auto(db_session):
    casa, admin_id = _armar_casa()
    auto = crear_auto(casa.id, "Toyota", "Corolla", admin_id)

    item = crear_item(
        casa.id, "Cambio de aceite", None, None, False, None, admin_id, auto_id=auto.id
    )

    assert item.auto_id == auto.id


def test_tc003_listar_sin_filtro_devuelve_solo_los_de_la_casa(db_session):
    casa, admin_id = _armar_casa()
    auto = crear_auto(casa.id, "Toyota", "Corolla", admin_id)

    item_casa = crear_item(casa.id, "Pintar el living", None, None, False, None, admin_id)
    crear_item(
        casa.id, "Cambio de aceite", None, None, False, None, admin_id, auto_id=auto.id
    )

    listado_casa = listar_items(casa.id)
    assert [i.id for i in listado_casa] == [item_casa.id]


def test_tc003_listar_filtrando_por_auto_devuelve_solo_los_de_ese_auto(db_session):
    casa, admin_id = _armar_casa()
    auto1 = crear_auto(casa.id, "Toyota", "Corolla", admin_id)
    auto2 = crear_auto(casa.id, "Ford", "Fiesta", admin_id)

    crear_item(casa.id, "Pintar el living", None, None, False, None, admin_id)
    item_auto1 = crear_item(
        casa.id, "Cambio de aceite", None, None, False, None, admin_id, auto_id=auto1.id
    )
    crear_item(
        casa.id, "Rotación de neumáticos", None, None, False, None, admin_id, auto_id=auto2.id
    )

    listado_auto1 = listar_items(casa.id, auto_id=auto1.id)
    assert [i.id for i in listado_auto1] == [item_auto1.id]


def test_tc004_alerta_incluye_items_de_auto_con_auto_id_y_auto_nombre(db_session):
    casa, admin_id = _armar_casa()
    auto = crear_auto(casa.id, "Toyota", "Corolla", admin_id)

    item = crear_item(
        casa.id,
        "Cambio de aceite",
        None,
        date.today() + timedelta(days=3),
        False,
        None,
        admin_id,
        auto_id=auto.id,
    )

    alertas = obtener_items_con_alerta(casa.id)

    assert len(alertas) == 1
    assert alertas[0].id == item.id
    assert alertas[0].auto_id == auto.id
    assert alertas[0].auto_nombre == "Toyota Corolla"


def test_tc004_alerta_de_item_de_casa_no_lleva_auto_id_ni_auto_nombre(db_session):
    casa, admin_id = _armar_casa()

    crear_item(
        casa.id, "Pintar el living", None, date.today() + timedelta(days=3), False, None, admin_id
    )

    alertas = obtener_items_con_alerta(casa.id)

    assert len(alertas) == 1
    assert alertas[0].auto_id is None
    assert alertas[0].auto_nombre is None


def test_tc005_auto_de_otra_casa_es_rechazado_con_not_found(db_session):
    casa1, admin1 = _armar_casa()
    casa2, admin2 = _armar_casa()
    auto_de_casa2 = crear_auto(casa2.id, "Toyota", "Corolla", admin2)

    with pytest.raises(NotFoundError):
        crear_item(
            casa1.id,
            "Cambio de aceite",
            None,
            None,
            False,
            None,
            admin1,
            auto_id=auto_de_casa2.id,
        )


def test_crear_item_con_auto_id_inexistente_es_rechazado_con_not_found(db_session):
    casa, admin_id = _armar_casa()

    with pytest.raises(NotFoundError):
        crear_item(
            casa.id, "Cambio de aceite", None, None, False, None, admin_id, auto_id=uuid.uuid4()
        )
