"""T2 (spec `gastos-en-cuotas`) — `registrar_gasto` genera N gastos
consecutivos mes a mes cuando `cuotas >= 2`.

Cubre TC-001 a TC-006. TC-006 ejercita `registrar_gasto` junto con
`calcular_balance` (spec `balance-mensual`, ya mergeada en la rama base
de este build) — confirma que una cuota futura no infla el balance del
mes actual.
"""
import importlib
import uuid
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models.usuario import Usuario
from src.services.balance_service import calcular_balance
from src.services.casa_service import crear_casa
from src.services.categoria_service import crear_categoria
from src.services.exceptions import ValidationError
from src.services.gasto_service import _sumar_meses, listar_gastos, registrar_gasto


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


@pytest.fixture()
def db_session(monkeypatch):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    migration_casas = importlib.import_module("src.db.migrations.0001_casas_miembros")
    migration_gastos = importlib.import_module("src.db.migrations.0002_gastos")
    # 0004 (spec `dashboard-actividad`): `registrar_gasto` dispara un hook
    # a `actividad_service.registrar_actividad`, que requiere la tabla
    # `historial_actividad`.
    migration_actividad = importlib.import_module("src.db.migrations.0004_historial_actividad")
    # 0005 (spec `usuarios-auth`): `agregar_miembro` ahora exige un
    # Usuario real (por email) para vincular al nuevo Miembro.
    migration_usuarios = importlib.import_module("src.db.migrations.0005_usuarios")
    # 0009 (spec `gastos-suscripcion-mensual`): `listar_gastos` ahora
    # dispara `suscripcion_service.generar_gastos_pendientes` como primera
    # línea, que requiere la tabla `suscripciones`.
    migration_suscripciones = importlib.import_module("src.db.migrations.0009_suscripciones")
    migration_casas.upgrade(engine)
    migration_gastos.upgrade(engine)
    migration_actividad.upgrade(engine)
    migration_usuarios.upgrade(engine)
    migration_suscripciones.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.categoria_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.gasto_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.balance_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.actividad_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.suscripcion_service.get_session", lambda: TestSession())
    yield TestSession


def _armar_casa(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    categoria = crear_categoria(casa.id, "Electrodomésticos", admin_id)
    return casa, admin_id, categoria


def test_tc001_tres_cuotas_con_fechas_consecutivas_mes_a_mes(db_session):
    casa, admin_id, categoria = _armar_casa(db_session)

    primer_gasto = registrar_gasto(
        casa.id,
        "Heladera",
        Decimal("120000.00"),
        date(2026, 9, 15),
        categoria.id,
        admin_id,
        admin_id,
        participantes=[admin_id],
        cuotas=3,
    )

    gastos = sorted(listar_gastos(casa.id), key=lambda g: g.fecha)
    assert len(gastos) == 3
    assert [g.fecha for g in gastos] == [date(2026, 9, 15), date(2026, 10, 15), date(2026, 11, 15)]
    assert all(g.importe == Decimal("40000.00") for g in gastos)
    assert primer_gasto.fecha == date(2026, 9, 15)


def test_tc002_redondeo_ajustado_en_la_ultima_cuota(db_session):
    casa, admin_id, categoria = _armar_casa(db_session)

    registrar_gasto(
        casa.id,
        "Compra grande",
        Decimal("100"),
        date(2026, 1, 1),
        categoria.id,
        admin_id,
        admin_id,
        participantes=[admin_id],
        cuotas=3,
    )

    gastos = sorted(listar_gastos(casa.id), key=lambda g: g.cuota_numero)
    assert len(gastos) == 3
    assert sum(g.importe for g in gastos) == Decimal("100.00")
    assert gastos[0].importe == Decimal("33.33")
    assert gastos[1].importe == Decimal("33.33")
    assert gastos[2].importe == Decimal("33.34")


def test_tc003_las_cuotas_comparten_grupo_y_tienen_numero_total_correctos(db_session):
    casa, admin_id, categoria = _armar_casa(db_session)

    registrar_gasto(
        casa.id,
        "Heladera",
        Decimal("120000.00"),
        date(2026, 9, 15),
        categoria.id,
        admin_id,
        admin_id,
        participantes=[admin_id],
        cuotas=3,
    )

    gastos = sorted(listar_gastos(casa.id), key=lambda g: g.cuota_numero)
    grupos = {g.cuota_grupo_id for g in gastos}
    assert len(grupos) == 1
    assert None not in grupos

    assert [g.cuota_numero for g in gastos] == [1, 2, 3]
    assert all(g.cuota_total == 3 for g in gastos)
    assert [g.descripcion for g in gastos] == [
        "Heladera (1/3)",
        "Heladera (2/3)",
        "Heladera (3/3)",
    ]


def test_tc004_sin_cuotas_se_comporta_exactamente_igual_que_hoy(db_session):
    casa, admin_id, categoria = _armar_casa(db_session)

    gasto = registrar_gasto(
        casa.id,
        "Compra semanal",
        Decimal("20000.00"),
        date(2026, 1, 1),
        categoria.id,
        admin_id,
        admin_id,
        participantes=[admin_id],
    )

    gastos = listar_gastos(casa.id)
    assert len(gastos) == 1
    assert gasto.cuota_grupo_id is None
    assert gasto.cuota_numero is None
    assert gasto.cuota_total is None
    assert gasto.descripcion == "Compra semanal"


def test_cuotas_1_se_comporta_igual_que_ausente(db_session):
    """Regresión de REQ-003: `cuotas=1`, enviado explícitamente, no es
    "0 o negativo" (REQ-004) — se comporta exactamente igual que
    `cuotas` ausente, sin ningún dato de cuota poblado."""
    casa, admin_id, categoria = _armar_casa(db_session)

    gasto = registrar_gasto(
        casa.id,
        "Compra puntual",
        Decimal("5000.00"),
        date(2026, 1, 1),
        categoria.id,
        admin_id,
        admin_id,
        participantes=[admin_id],
        cuotas=1,
    )

    gastos = listar_gastos(casa.id)
    assert len(gastos) == 1
    assert gasto.cuota_grupo_id is None
    assert gasto.cuota_numero is None
    assert gasto.cuota_total is None
    assert gasto.descripcion == "Compra puntual"


def test_tc005_cuotas_cero_es_rechazado(db_session):
    casa, admin_id, categoria = _armar_casa(db_session)

    with pytest.raises(ValidationError):
        registrar_gasto(
            casa.id,
            "Compra",
            Decimal("100.00"),
            date(2026, 1, 1),
            categoria.id,
            admin_id,
            admin_id,
            participantes=[admin_id],
            cuotas=0,
        )

    assert listar_gastos(casa.id) == []


def test_cuotas_negativo_es_rechazado(db_session):
    casa, admin_id, categoria = _armar_casa(db_session)

    with pytest.raises(ValidationError):
        registrar_gasto(
            casa.id,
            "Compra",
            Decimal("100.00"),
            date(2026, 1, 1),
            categoria.id,
            admin_id,
            admin_id,
            participantes=[admin_id],
            cuotas=-1,
        )


def test_tc006_una_cuota_futura_no_infla_el_balance_del_mes_actual(db_session):
    casa, admin_id, categoria = _armar_casa(db_session)
    hoy = date.today()

    registrar_gasto(
        casa.id,
        "Heladera",
        Decimal("120000.00"),
        hoy,
        categoria.id,
        admin_id,
        admin_id,
        participantes=[admin_id],
        cuotas=3,
    )

    mes_actual = f"{hoy.year:04d}-{hoy.month:02d}"
    fecha_dentro_de_2_meses = _sumar_meses(hoy, 2)
    mes_futuro = f"{fecha_dentro_de_2_meses.year:04d}-{fecha_dentro_de_2_meses.month:02d}"

    balance_actual = calcular_balance(casa.id, mes=mes_actual)
    por_id_actual = {b.miembro_id: b for b in balance_actual}
    assert por_id_actual[admin_id].pago == Decimal("40000.00")

    balance_futuro = calcular_balance(casa.id, mes=mes_futuro)
    por_id_futuro = {b.miembro_id: b for b in balance_futuro}
    assert por_id_futuro[admin_id].pago == Decimal("40000.00")


def test_sumar_meses_cruza_el_fin_de_anio():
    """Failure Triage (10-verify.md, TC-001): `_sumar_meses` debe manejar
    el cambio de año (dic -> ene) sin ajustes especiales."""
    assert _sumar_meses(date(2026, 11, 15), 1) == date(2026, 12, 15)
    assert _sumar_meses(date(2026, 11, 15), 2) == date(2027, 1, 15)
    assert _sumar_meses(date(2026, 12, 31), 2) == date(2027, 2, 28)
