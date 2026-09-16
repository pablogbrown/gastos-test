"""T2 (spec `mantenimiento-casa`) — Servicio de mantenimiento: alta con
materiales, completar con recurrencia y gate de fecha, cálculo de alerta.

Cubre TC-001 a TC-008.
"""
import importlib
import uuid
from datetime import date, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.services.casa_service import crear_casa
from src.services.exceptions import ConflictError, NotFoundError, PermissionDeniedError, ValidationError
from src.services.mantenimiento_service import (
    UMBRAL_ALERTA_DIAS,
    actualizar_material,
    agregar_material,
    completar_item,
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
    migration_casas.upgrade(engine)
    migration_mantenimiento.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.mantenimiento_service.get_session", lambda: TestSession())
    yield TestSession


def _armar_casa():
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    return casa, admin_id


def test_tc001_alta_con_datos_validos_persiste_en_pendiente(db_session):
    casa, admin_id = _armar_casa()

    item = crear_item(
        casa.id,
        "Arreglar el reflector de la entrada",
        None,
        None,
        False,
        None,
        admin_id,
    )

    assert item.estado == "pendiente"
    assert item.nombre == "Arreglar el reflector de la entrada"

    listado = listar_items(casa.id)
    assert len(listado) == 1
    assert listado[0].id == item.id


def test_tc002_recurrente_sin_periodicidad_es_rechazado(db_session):
    casa, admin_id = _armar_casa()

    with pytest.raises(ValidationError):
        crear_item(
            casa.id,
            "Poner membrana al techo",
            None,
            date.today() + timedelta(days=90),
            True,
            None,
            admin_id,
        )


def test_tc002_recurrente_sin_fecha_estimada_es_rechazado(db_session):
    casa, admin_id = _armar_casa()

    with pytest.raises(ValidationError):
        crear_item(
            casa.id,
            "Poner membrana al techo",
            None,
            None,
            True,
            "anual",
            admin_id,
        )


def test_tc003_materiales_al_crear_persisten_con_conseguido_false(db_session):
    casa, admin_id = _armar_casa()

    item = crear_item(
        casa.id,
        "Poner membrana al techo",
        None,
        date.today() + timedelta(days=90),
        True,
        "anual",
        admin_id,
        materiales=[
            {"nombre": "Membrana asfáltica", "cantidad": 2},
            {"nombre": "Silicona", "cantidad": 1},
        ],
    )

    assert len(item.materiales) == 2
    nombres = {m.nombre: m for m in item.materiales}
    assert nombres["Membrana asfáltica"].cantidad == 2
    assert nombres["Membrana asfáltica"].conseguido is False
    assert nombres["Silicona"].cantidad == 1
    assert nombres["Silicona"].conseguido is False


def test_tc004_marcar_material_como_conseguido_persiste(db_session):
    casa, admin_id = _armar_casa()
    item = crear_item(casa.id, "Pintar el living", None, None, False, None, admin_id)
    material = agregar_material(casa.id, item.id, "Pintura blanca", 3, admin_id)

    actualizado = actualizar_material(casa.id, item.id, material.id, True, admin_id)

    assert actualizado.conseguido is True

    releido = listar_items(casa.id)[0]
    assert releido.materiales[0].conseguido is True


def test_tc005_completar_no_recurrente_no_genera_nueva_instancia(db_session):
    casa, admin_id = _armar_casa()
    item = crear_item(casa.id, "Pintar el living", None, None, False, None, admin_id)

    completado = completar_item(casa.id, item.id, admin_id)

    assert completado.estado == "completado"
    listado = listar_items(casa.id)
    assert [i.id for i in listado] == [completado.id]


def test_tc006_completar_recurrente_mensual_genera_la_siguiente_con_30_dias(db_session):
    casa, admin_id = _armar_casa()
    fecha_inicial = date.today()
    item = crear_item(
        casa.id,
        "Limpiar canaletas",
        None,
        fecha_inicial,
        True,
        "mensual",
        admin_id,
    )

    completar_item(casa.id, item.id, admin_id)

    listado = listar_items(casa.id)
    assert len(listado) == 2
    nueva = next(i for i in listado if i.id != item.id)
    assert nueva.estado == "pendiente"
    assert nueva.recurrente is True
    assert nueva.periodicidad == "mensual"
    assert nueva.fecha_estimada == fecha_inicial + timedelta(days=30)


def test_tc007_completar_antes_de_su_fecha_estimada_es_rechazado(db_session):
    casa, admin_id = _armar_casa()
    fecha_inicial = date.today()
    item = crear_item(
        casa.id,
        "Limpiar canaletas",
        None,
        fecha_inicial,
        True,
        "mensual",
        admin_id,
    )
    completar_item(casa.id, item.id, admin_id)
    nueva = next(i for i in listar_items(casa.id) if i.id != item.id)

    with pytest.raises(ConflictError):
        completar_item(casa.id, nueva.id, admin_id)


def test_completar_item_ya_completado_es_rechazado(db_session):
    casa, admin_id = _armar_casa()
    item = crear_item(casa.id, "Pintar el living", None, None, False, None, admin_id)
    completar_item(casa.id, item.id, admin_id)

    with pytest.raises(ConflictError):
        completar_item(casa.id, item.id, admin_id)


def test_completar_recurrente_en_su_fecha_estimada_se_permite(db_session):
    casa, admin_id = _armar_casa()
    item = crear_item(
        casa.id,
        "Limpiar canaletas",
        None,
        date.today(),
        True,
        "semanal",
        admin_id,
    )

    completado = completar_item(casa.id, item.id, admin_id)

    assert completado.estado == "completado"


def test_crear_item_sin_actor_miembro_activo_es_rechazado(db_session):
    casa, _admin_id = _armar_casa()
    ajeno = uuid.uuid4()

    with pytest.raises(PermissionDeniedError):
        crear_item(casa.id, "Pintar el living", None, None, False, None, ajeno)


def test_completar_item_inexistente_lanza_not_found(db_session):
    casa, admin_id = _armar_casa()

    with pytest.raises(NotFoundError):
        completar_item(casa.id, uuid.uuid4(), admin_id)


def test_tc008_vence_en_5_dias_aparece_en_alerta(db_session):
    casa, admin_id = _armar_casa()
    item = crear_item(
        casa.id,
        "Arreglar el reflector",
        None,
        date.today() + timedelta(days=5),
        False,
        None,
        admin_id,
    )

    alertas = obtener_items_con_alerta(casa.id)

    assert len(alertas) == 1
    assert alertas[0].id == item.id
    assert alertas[0].dias_para_vencimiento == 5
    assert alertas[0].vencido is False


def test_tc008_vence_en_20_dias_no_aparece_en_alerta(db_session):
    casa, admin_id = _armar_casa()
    crear_item(
        casa.id,
        "Arreglar el reflector",
        None,
        date.today() + timedelta(days=20),
        False,
        None,
        admin_id,
    )

    assert obtener_items_con_alerta(casa.id) == []


def test_item_ya_vencido_aparece_marcado_como_vencido(db_session):
    casa, admin_id = _armar_casa()
    item = crear_item(
        casa.id,
        "Arreglar el reflector",
        None,
        date.today() - timedelta(days=2),
        False,
        None,
        admin_id,
    )

    alertas = obtener_items_con_alerta(casa.id)

    assert len(alertas) == 1
    assert alertas[0].id == item.id
    assert alertas[0].vencido is True


def test_item_completado_no_aparece_en_alerta(db_session):
    casa, admin_id = _armar_casa()
    item = crear_item(
        casa.id,
        "Arreglar el reflector",
        None,
        date.today() + timedelta(days=1),
        False,
        None,
        admin_id,
    )
    completar_item(casa.id, item.id, admin_id)

    assert obtener_items_con_alerta(casa.id) == []


def test_item_sin_fecha_estimada_nunca_genera_alerta(db_session):
    casa, admin_id = _armar_casa()
    crear_item(casa.id, "Pintar el living", None, None, False, None, admin_id)

    assert obtener_items_con_alerta(casa.id) == []


def test_vence_justo_en_el_umbral_aparece_en_alerta(db_session):
    casa, admin_id = _armar_casa()
    item = crear_item(
        casa.id,
        "Arreglar el reflector",
        None,
        date.today() + timedelta(days=UMBRAL_ALERTA_DIAS),
        False,
        None,
        admin_id,
    )

    alertas = obtener_items_con_alerta(casa.id)

    assert len(alertas) == 1
    assert alertas[0].id == item.id
