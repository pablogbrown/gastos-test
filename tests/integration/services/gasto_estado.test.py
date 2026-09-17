"""T2 (spec `gastos-estado-pago`) -- `registrar_gasto`/`actualizar_estado_
gasto` validan y persisten `estado`; los generadores automaticos
(suscripcion, importacion de resumen) siempre pasan `estado="a_pagar"`.

Cubre TC-001, TC-002, TC-003, TC-004, TC-005, TC-006 y TC-008 (control:
`calcular_balance` no se ve afectado por `estado`).
"""
import importlib
import io
import uuid
from datetime import date
from decimal import Decimal

import pytest
from reportlab.pdfgen import canvas
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models.usuario import Usuario
from src.services.balance_service import calcular_balance
from src.services.casa_service import crear_casa
from src.services.categoria_service import crear_categoria
from src.services.exceptions import NotFoundError, ValidationError
from src.services.gasto_service import (
    actualizar_estado_gasto,
    listar_gastos,
    registrar_gasto,
)
from src.services.resumen_importer_service import importar_resumen
from src.services.suscripcion_service import crear_suscripcion, generar_gastos_pendientes
from src.services.tarjeta_service import crear_tarjeta


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
    for nombre in (
        "0001_casas_miembros",
        "0002_gastos",
        "0004_historial_actividad",
        "0005_usuarios",
        "0009_suscripciones",
        "0010_gasto_suscripcion_moneda",
        "0011_tarjetas_credito",
        "0012_gasto_tarjeta_id",
        # Spec `resumen-tarjeta-pago`: `resumen_importer_service` ahora
        # persiste su propio `ResumenTarjeta` (chequeo de duplicado +
        # registro), así que necesita la tabla `resumenes_tarjeta`.
        "0019_resumen_tarjeta",
    ):
        importlib.import_module(f"src.db.migrations.{nombre}").upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    for modulo in (
        "src.services.casa_service",
        "src.services.miembro_service",
        "src.services.categoria_service",
        "src.services.gasto_service",
        "src.services.actividad_service",
        "src.services.suscripcion_service",
        "src.services.balance_service",
        "src.services.tarjeta_service",
        # Spec `resumen-tarjeta-pago`: idem arriba — `resumen_importer_
        # service` ahora abre su propia sesión.
        "src.services.resumen_importer_service",
    ):
        monkeypatch.setattr(f"{modulo}.get_session", lambda: TestSession())
    yield TestSession


def _armar_casa(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    categoria = crear_categoria(casa.id, "Supermercado", admin_id)
    return casa, admin_id, categoria


def test_tc001_gasto_sin_estado_persiste_pagado_por_default(db_session):
    casa, admin_id, categoria = _armar_casa(db_session)

    gasto = registrar_gasto(
        casa.id,
        "Compra semanal",
        Decimal("20000.00"),
        date(2026, 1, 1),
        categoria.id,
        admin_id,
        admin_id,
    )

    assert gasto.estado == "pagado"
    (persistido,) = listar_gastos(casa.id)
    assert persistido.estado == "pagado"


def test_tc002_gasto_con_estado_a_pagar_persiste_asi(db_session):
    casa, admin_id, categoria = _armar_casa(db_session)

    gasto = registrar_gasto(
        casa.id,
        "Cuota futura",
        Decimal("5000.00"),
        date(2026, 1, 1),
        categoria.id,
        admin_id,
        admin_id,
        estado="a_pagar",
    )

    assert gasto.estado == "a_pagar"
    (persistido,) = listar_gastos(casa.id)
    assert persistido.estado == "a_pagar"


def test_tc003_las_3_cuotas_heredan_el_mismo_estado_a_pagar(db_session):
    casa, admin_id, categoria = _armar_casa(db_session)

    registrar_gasto(
        casa.id,
        "Heladera",
        Decimal("300.00"),
        date(2026, 9, 15),
        categoria.id,
        admin_id,
        admin_id,
        cuotas=3,
        estado="a_pagar",
    )

    gastos = sorted(listar_gastos(casa.id), key=lambda g: g.cuota_numero)
    assert len(gastos) == 3
    assert all(g.estado == "a_pagar" for g in gastos)


def test_tc004_gasto_generado_por_suscripcion_nace_a_pagar(db_session):
    casa, admin_id, categoria = _armar_casa(db_session)

    suscripcion = crear_suscripcion(
        casa.id, "Netflix", Decimal("5000.00"), categoria.id, admin_id
    )
    (gasto_inicial,) = listar_gastos(casa.id)
    assert gasto_inicial.estado == "a_pagar"

    # `generar_gastos_pendientes` es el otro punto de entrada de
    # generacion automatica (mes siguiente) -- fuerza que corra de nuevo
    # marcando el mes ya generado como pasado, para confirmar el mismo
    # comportamiento sobre ese call-site tambien.
    from src.services.suscripcion_service import get_session as _get_session
    from src.db.models.suscripcion import Suscripcion

    session = _get_session()
    try:
        s = session.get(Suscripcion, suscripcion.id)
        s.ultimo_mes_generado = "2000-01"
        session.commit()
    finally:
        session.close()

    generar_gastos_pendientes(casa.id)
    gastos = listar_gastos(casa.id)
    assert len(gastos) == 2
    assert all(g.estado == "a_pagar" for g in gastos)


def test_tc006_actualizar_estado_gasto_cambia_en_ambos_sentidos(db_session):
    casa, admin_id, categoria = _armar_casa(db_session)

    gasto = registrar_gasto(
        casa.id,
        "Cuota futura",
        Decimal("5000.00"),
        date(2026, 1, 1),
        categoria.id,
        admin_id,
        admin_id,
        estado="a_pagar",
    )

    actualizado = actualizar_estado_gasto(casa.id, gasto.id, "pagado", admin_id)
    assert actualizado.estado == "pagado"

    actualizado_de_nuevo = actualizar_estado_gasto(casa.id, gasto.id, "a_pagar", admin_id)
    assert actualizado_de_nuevo.estado == "a_pagar"


def test_tc007_actualizar_estado_gasto_con_valor_invalido_es_rechazado(db_session):
    casa, admin_id, categoria = _armar_casa(db_session)

    gasto = registrar_gasto(
        casa.id,
        "Compra",
        Decimal("100.00"),
        date(2026, 1, 1),
        categoria.id,
        admin_id,
        admin_id,
    )

    with pytest.raises(ValidationError):
        actualizar_estado_gasto(casa.id, gasto.id, "otro", admin_id)


def test_estado_invalido_en_registrar_gasto_es_rechazado_con_validation_error(db_session):
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
            estado="otro",
        )

    assert listar_gastos(casa.id) == []


def test_actualizar_estado_gasto_inexistente_lanza_not_found(db_session):
    casa, admin_id, _categoria = _armar_casa(db_session)

    with pytest.raises(NotFoundError):
        actualizar_estado_gasto(casa.id, uuid.uuid4(), "pagado", admin_id)


def _construir_pdf_resumen_bbva_minimo() -> bytes:
    """Mismo layout sintetico que `resumen_importer.test.py` -- un
    consumo normal (SUPERMERCADO), uno en cuotas restantes
    (ELECTRODOMESTICOS) y uno de suscripcion reconocida (NETFLIX), para
    ejercitar las 3 rutas reales de creacion de gasto dentro de
    `importar_resumen` (TC-005)."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)

    y = 800
    c.drawString(40, y, "BBVA Visa Platinum")
    y -= 30
    c.drawString(
        40, y, "CIERRE ACTUAL     VENCIMIENTO ACTUAL     SALDO ACTUAL $     "
        "SALDO ACTUAL U$S     PAGO MÍNIMO $"
    )
    y -= 16
    c.drawString(40, y, "27-Ago-26     07-Sep-26     125.430,50     340,00     50.000,00")
    y -= 30
    c.drawString(40, y, "Consumos")
    y -= 20

    c.drawString(40, y, "01-Ago-26")
    c.drawString(110, y, "SUPERMERCADO DIA")
    c.drawString(320, y, "1234")
    c.drawString(400, y, "15.200,00")
    y -= 16
    c.drawString(40, y, "04-Ago-26")
    c.drawString(110, y, "ELECTRODOMESTICOS SA C.04/06")
    c.drawString(320, y, "9012")
    c.drawString(400, y, "22.000,00")
    y -= 16
    c.drawString(40, y, "05-Ago-26")
    c.drawString(110, y, "NETFLIX.COM")
    c.drawString(320, y, "3456")
    c.drawString(400, y, "3.999,00")
    y -= 16
    y -= 4

    c.drawString(110, y, "TOTAL CONSUMOS")
    c.drawString(400, y, "41.199,00")

    c.save()
    return buffer.getvalue()


def test_tc005_gastos_creados_al_importar_un_resumen_nacen_a_pagar(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    tarjeta = crear_tarjeta(
        casa.id,
        admin_id,
        "BBVA",
        "Visa Platinum",
        "1234",
        date(2026, 7, 27),
        date(2026, 8, 7),
        admin_id,
    )

    importar_resumen(casa.id, tarjeta.id, _construir_pdf_resumen_bbva_minimo(), admin_id)

    gastos = listar_gastos(casa.id)
    # Las 3 rutas: consumo normal (SUPERMERCADO), cuotas restantes
    # (ELECTRODOMESTICOS, 3 filas) y suscripcion detectada (NETFLIX) --
    # ninguna nace "pagado".
    assert len(gastos) >= 3
    assert all(g.estado == "a_pagar" for g in gastos)


def test_tc008_cambiar_estado_no_afecta_calcular_balance(db_session):
    """Control (REQ-006): registrar gastos con distintos `estado`, cambiar
    alguno via `actualizar_estado_gasto`, y confirmar que `calcular_
    balance` devuelve exactamente los mismos montos antes y despues --
    `balance_service.py` no se toca en esta spec."""
    casa, admin_id, categoria = _armar_casa(db_session)

    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    from src.services.miembro_service import agregar_miembro

    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)

    gasto_pagado = registrar_gasto(
        casa.id,
        "Super",
        Decimal("40000.00"),
        date(2026, 1, 1),
        categoria.id,
        admin_id,
        admin_id,
        estado="pagado",
    )
    gasto_a_pagar = registrar_gasto(
        casa.id,
        "Cuota tarjeta",
        Decimal("10000.00"),
        date(2026, 1, 2),
        categoria.id,
        ana.id,
        admin_id,
        estado="a_pagar",
    )

    balance_antes = calcular_balance(casa.id, "2026-01")

    actualizar_estado_gasto(casa.id, gasto_a_pagar.id, "pagado", admin_id)
    actualizar_estado_gasto(casa.id, gasto_pagado.id, "a_pagar", admin_id)

    balance_despues = calcular_balance(casa.id, "2026-01")

    totales_antes = {fila.moneda: fila.total_gastos for fila in balance_antes.totales}
    totales_despues = {fila.moneda: fila.total_gastos for fila in balance_despues.totales}
    assert totales_antes == totales_despues

    def _clave(fila):
        return (fila.miembro_id, fila.moneda)

    aportes_antes = {_clave(fila): fila.total for fila in balance_antes.aportes}
    aportes_despues = {_clave(fila): fila.total for fila in balance_despues.aportes}
    assert aportes_antes == aportes_despues
