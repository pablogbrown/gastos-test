"""T2 (spec `tarjetas-credito`) — Servicio de tarjetas de crédito: CRUD y
cálculo de alerta de vencimiento.

Cubre TC-001 a TC-007.
"""
import importlib
import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.services.casa_service import crear_casa
from src.services.exceptions import NotFoundError, ValidationError
from src.services.tarjeta_service import (
    UMBRAL_ALERTA_DIAS,
    actualizar_tarjeta,
    crear_tarjeta,
    eliminar_tarjeta,
    listar_tarjetas,
    obtener_tarjetas_con_alerta,
)


@pytest.fixture()
def db_session(monkeypatch):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    migration_casas = importlib.import_module("src.db.migrations.0001_casas_miembros")
    migration_tarjetas = importlib.import_module("src.db.migrations.0011_tarjetas_credito")
    migration_casas.upgrade(engine)
    migration_tarjetas.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.tarjeta_service.get_session", lambda: TestSession())
    yield TestSession


def _armar_casa():
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    return casa, admin_id


def _crear_tarjeta_de_prueba(casa_id, admin_id, dias_para_vencer=30, **overrides):
    hoy = date.today()
    kwargs = dict(
        banco="BBVA",
        nombre="Visa Platinum",
        ultimos_digitos="1234",
        fecha_cierre_actual=hoy - timedelta(days=10),
        fecha_vencimiento_actual=hoy + timedelta(days=dias_para_vencer),
    )
    kwargs.update(overrides)
    return crear_tarjeta(
        casa_id,
        admin_id,
        kwargs["banco"],
        kwargs["nombre"],
        kwargs["ultimos_digitos"],
        kwargs["fecha_cierre_actual"],
        kwargs["fecha_vencimiento_actual"],
        admin_id,
    )


def test_tc001_alta_con_datos_validos_persiste_y_aparece_en_el_listado(db_session):
    casa, admin_id = _armar_casa()

    tarjeta = _crear_tarjeta_de_prueba(casa.id, admin_id)

    assert tarjeta.activa is True
    assert tarjeta.saldo_actual_ars is None
    assert tarjeta.saldo_actual_usd is None

    listado = listar_tarjetas(casa.id)
    assert len(listado) == 1
    assert listado[0].id == tarjeta.id
    assert listado[0].nombre == "Visa Platinum"


def test_tc002_alta_sin_banco_es_rechazada(db_session):
    casa, admin_id = _armar_casa()
    hoy = date.today()

    with pytest.raises(ValidationError):
        crear_tarjeta(
            casa.id,
            admin_id,
            "",
            "Visa Platinum",
            "1234",
            hoy,
            hoy + timedelta(days=30),
            admin_id,
        )

    assert listar_tarjetas(casa.id) == []


def test_tc003_edicion_de_vencimiento_persiste(db_session):
    casa, admin_id = _armar_casa()
    tarjeta = _crear_tarjeta_de_prueba(casa.id, admin_id)
    nuevo_vencimiento = date.today() + timedelta(days=45)

    actualizada = actualizar_tarjeta(
        casa.id,
        tarjeta.id,
        admin_id,
        fecha_vencimiento_actual=nuevo_vencimiento,
    )

    assert actualizada.fecha_vencimiento_actual == nuevo_vencimiento

    releida = listar_tarjetas(casa.id)[0]
    assert releida.fecha_vencimiento_actual == nuevo_vencimiento


def test_tc003_actualizar_tarjeta_inexistente_lanza_not_found(db_session):
    casa, admin_id = _armar_casa()

    with pytest.raises(NotFoundError):
        actualizar_tarjeta(casa.id, uuid.uuid4(), admin_id, saldo_actual_ars=Decimal("100.00"))


def test_tc004_baja_saca_la_tarjeta_del_listado_activo(db_session):
    casa, admin_id = _armar_casa()
    tarjeta = _crear_tarjeta_de_prueba(casa.id, admin_id)

    eliminar_tarjeta(casa.id, tarjeta.id, admin_id)

    assert listar_tarjetas(casa.id) == []


def test_tc005_vence_en_3_dias_aparece_en_alerta_no_vencida(db_session):
    casa, admin_id = _armar_casa()
    tarjeta = _crear_tarjeta_de_prueba(casa.id, admin_id, dias_para_vencer=3)

    alertas = obtener_tarjetas_con_alerta(casa.id)

    assert len(alertas) == 1
    assert alertas[0].id == tarjeta.id
    assert alertas[0].dias_para_vencimiento == 3
    assert alertas[0].vencida is False


def test_tc006_ya_vencida_aparece_marcada_como_vencida(db_session):
    casa, admin_id = _armar_casa()
    tarjeta = _crear_tarjeta_de_prueba(casa.id, admin_id, dias_para_vencer=-2)

    alertas = obtener_tarjetas_con_alerta(casa.id)

    assert len(alertas) == 1
    assert alertas[0].id == tarjeta.id
    assert alertas[0].dias_para_vencimiento == -2
    assert alertas[0].vencida is True


def test_tc006_vence_hoy_mismo_no_se_marca_como_vencida(db_session):
    casa, admin_id = _armar_casa()
    _crear_tarjeta_de_prueba(casa.id, admin_id, dias_para_vencer=0)

    alertas = obtener_tarjetas_con_alerta(casa.id)

    assert len(alertas) == 1
    assert alertas[0].dias_para_vencimiento == 0
    assert alertas[0].vencida is False


def test_tc007_vence_en_20_dias_no_aparece_en_alerta(db_session):
    casa, admin_id = _armar_casa()
    _crear_tarjeta_de_prueba(casa.id, admin_id, dias_para_vencer=20)

    assert obtener_tarjetas_con_alerta(casa.id) == []


def test_tc007_vence_justo_en_el_umbral_aparece_en_alerta(db_session):
    casa, admin_id = _armar_casa()
    tarjeta = _crear_tarjeta_de_prueba(casa.id, admin_id, dias_para_vencer=UMBRAL_ALERTA_DIAS)

    alertas = obtener_tarjetas_con_alerta(casa.id)

    assert len(alertas) == 1
    assert alertas[0].id == tarjeta.id


def test_tarjeta_desactivada_no_aparece_en_alertas(db_session):
    casa, admin_id = _armar_casa()
    tarjeta = _crear_tarjeta_de_prueba(casa.id, admin_id, dias_para_vencer=1)

    eliminar_tarjeta(casa.id, tarjeta.id, admin_id)

    assert obtener_tarjetas_con_alerta(casa.id) == []
