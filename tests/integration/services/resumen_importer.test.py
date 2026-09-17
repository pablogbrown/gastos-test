"""T2 (spec `importar-resumen-tarjeta`) — `resumen_importer_service`:
orquestación completa de la importación de un resumen de tarjeta en PDF.

Cubre TC-001 a TC-007 a nivel de servicio (sin HTTP). Reutiliza el mismo
layout de PDF sintético que `tests/unit/services/pdf_resumen_parser.
test.py` (columnas fijas, `reportlab`) — self-contained acá también,
mismo criterio de "cada test file arma su propia fixture" que el resto
del proyecto.
"""
import importlib
import io
import uuid
from datetime import date

import pytest
from reportlab.pdfgen import canvas
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models.gasto import Gasto
from src.db.models.suscripcion import Suscripcion
from src.db.models.usuario import Usuario
from src.services.casa_service import crear_casa
from src.services.miembro_service import agregar_miembro
from src.services.resumen_importer_service import importar_resumen
from src.services.tarjeta_service import crear_tarjeta

_X_FECHA = 40
_X_DESC = 110
_X_CUPON = 320
_X_ARS = 400
_X_USD = 470


def _fila(c, y, fecha="", desc="", cupon="", ars="", usd=""):
    if fecha:
        c.drawString(_X_FECHA, y, fecha)
    if desc:
        c.drawString(_X_DESC, y, desc)
    if cupon:
        c.drawString(_X_CUPON, y, cupon)
    if ars:
        c.drawString(_X_ARS, y, ars)
    if usd:
        c.drawString(_X_USD, y, usd)


def _construir_pdf_resumen_bbva(cierre="27-Ago-26", vencimiento="07-Sep-26") -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)

    y = 800
    c.drawString(40, y, "BBVA Visa Platinum")
    y -= 30
    # Encabezado real: las 5 etiquetas van en una línea y sus 5 valores
    # en la línea SIGUIENTE — nunca etiqueta y valor en la misma línea
    # (bug real encontrado al importar un resumen real por primera vez,
    # ver `.nybo/plans/importar-resumen-tarjeta/evidence/decisions.yaml`).
    c.drawString(
        40, y, "CIERRE ACTUAL     VENCIMIENTO ACTUAL     SALDO ACTUAL $     "
        "SALDO ACTUAL U$S     PAGO MÍNIMO $"
    )
    y -= 16
    # `cierre`/`vencimiento` parametrizables (spec `resumen-tarjeta-pago`):
    # REQ-002 ahora rechaza una segunda importación con el mismo
    # (tarjeta_id, fecha_cierre) — algunos tests de ESTA spec necesitan
    # variar el cierre entre dos importaciones para no chocar con ese
    # guard nuevo (ver test_tc006 más abajo).
    c.drawString(40, y, f"{cierre}     {vencimiento}     125.430,50     340,00     50.000,00")
    y -= 30
    c.drawString(40, y, "Consumos")
    y -= 20

    _fila(c, y, "01-Ago-26", "SUPERMERCADO DIA", "1234", "15.200,00", "")
    y -= 16
    _fila(c, y, "03-Ago-26", "AMAZON.COM", "5678", "", "45,00")
    y -= 16
    _fila(c, y, "04-Ago-26", "ELECTRODOMESTICOS SA C.04/06", "9012", "22.000,00", "")
    y -= 16
    _fila(c, y, "05-Ago-26", "NETFLIX.COM", "3456", "3.999,00", "")
    y -= 16
    y -= 4

    _fila(c, y, "", "TOTAL CONSUMOS", "", "41.199,00", "45,00")
    y -= 20
    c.drawString(40, y, "Impuestos, cargos e intereses")
    y -= 20
    _fila(c, y, "06-Ago-26", "COMISION PLATINUM", "0000", "2.500,00", "")
    y -= 16
    _fila(c, y, "07-Ago-26", "IMPUESTO DE SELLOS", "0000", "850,00", "")

    c.save()
    return buffer.getvalue()


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
        "src.services.tarjeta_service",
        # Spec `resumen-tarjeta-pago`: idem arriba — `resumen_importer_
        # service` ahora abre su propia sesión.
        "src.services.resumen_importer_service",
    ):
        monkeypatch.setattr(f"{modulo}.get_session", lambda: TestSession())

    yield TestSession


def _armar_casa_con_tarjeta(db_session):
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
    return casa, admin_id, tarjeta


def _agregar_miembro_no_admin(db_session, casa_id, admin_id, email="ana@example.com"):
    session = db_session()
    try:
        usuario = Usuario(id=uuid.uuid4(), email=email, password_hash="hash-de-prueba")
        session.add(usuario)
        session.commit()
    finally:
        session.close()
    return agregar_miembro(casa_id, "Ana", "ANA1", email, admin_id)


def _gastos_de(db_session, casa_id):
    """Lee los `Gasto` persistidos directo del modelo — nunca vía
    `listar_gastos` (dispararía la generación perezosa mensual de
    cualquier Suscripcion activa creada en el test, ensuciando el conteo
    de gastos con uno extra del mes calendario real de cuando corre la
    suite)."""
    session = db_session()
    try:
        return (
            session.query(Gasto)
            .filter(Gasto.casa_id == casa_id)
            .order_by(Gasto.fecha)
            .all()
        )
    finally:
        session.close()


def test_tc001_importar_actualiza_cierre_vencimiento_saldo_de_la_tarjeta(db_session):
    casa, admin_id, tarjeta = _armar_casa_con_tarjeta(db_session)

    resultado = importar_resumen(casa.id, tarjeta.id, _construir_pdf_resumen_bbva(), admin_id)

    assert resultado.tarjeta.fecha_cierre_actual.isoformat() == "2026-08-27"
    assert resultado.tarjeta.fecha_vencimiento_actual.isoformat() == "2026-09-07"
    assert str(resultado.tarjeta.saldo_actual_ars) == "125430.50"
    assert str(resultado.tarjeta.saldo_actual_usd) == "340.00"


def test_tc002_consumo_en_pesos_crea_gasto_ars(db_session):
    casa, admin_id, tarjeta = _armar_casa_con_tarjeta(db_session)

    importar_resumen(casa.id, tarjeta.id, _construir_pdf_resumen_bbva(), admin_id)

    gastos = _gastos_de(db_session, casa.id)
    supermercado = next(g for g in gastos if "SUPERMERCADO" in g.descripcion)
    assert supermercado.moneda == "ARS"
    assert str(supermercado.importe) == "15200.00"
    assert supermercado.fecha.isoformat() == "2026-08-01"
    assert supermercado.tarjeta_id == tarjeta.id


def test_tc003_consumo_en_dolares_crea_gasto_usd(db_session):
    casa, admin_id, tarjeta = _armar_casa_con_tarjeta(db_session)

    importar_resumen(casa.id, tarjeta.id, _construir_pdf_resumen_bbva(), admin_id)

    gastos = _gastos_de(db_session, casa.id)
    amazon = next(g for g in gastos if "AMAZON" in g.descripcion)
    assert amazon.moneda == "USD"
    assert str(amazon.importe) == "45.00"


def test_tc004_linea_en_cuotas_crea_solo_las_cuotas_restantes(db_session):
    casa, admin_id, tarjeta = _armar_casa_con_tarjeta(db_session)

    resultado = importar_resumen(casa.id, tarjeta.id, _construir_pdf_resumen_bbva(), admin_id)

    gastos = _gastos_de(db_session, casa.id)
    cuotas = sorted(
        (g for g in gastos if "ELECTRODOMESTICOS" in g.descripcion), key=lambda g: g.cuota_numero
    )
    assert len(cuotas) == 3
    assert [c.cuota_numero for c in cuotas] == [4, 5, 6]
    assert all(c.cuota_total == 6 for c in cuotas)
    assert all(str(c.importe) == "22000.00" for c in cuotas)
    # Regresión (reportado en vivo): sin el sufijo "(N/M)" en la
    # descripción, las 3 cuotas quedaban indistinguibles en el listado.
    assert [c.descripcion for c in cuotas] == [
        "ELECTRODOMESTICOS SA (4/6)",
        "ELECTRODOMESTICOS SA (5/6)",
        "ELECTRODOMESTICOS SA (6/6)",
    ]
    assert [c.fecha.isoformat() for c in cuotas] == ["2026-08-04", "2026-09-04", "2026-10-04"]
    grupos = {c.cuota_grupo_id for c in cuotas}
    assert len(grupos) == 1
    assert resultado.cuotas_creadas == 3


def test_tc005_comercio_reconocido_sin_suscripcion_previa_admin_crea_suscripcion_nueva(
    db_session,
):
    casa, admin_id, tarjeta = _armar_casa_con_tarjeta(db_session)

    resultado = importar_resumen(casa.id, tarjeta.id, _construir_pdf_resumen_bbva(), admin_id)

    session = db_session()
    try:
        suscripciones = (
            session.query(Suscripcion)
            .filter(Suscripcion.casa_id == casa.id, Suscripcion.descripcion == "NETFLIX.COM")
            .all()
        )
    finally:
        session.close()
    assert len(suscripciones) == 1

    gastos = _gastos_de(db_session, casa.id)
    netflix = next(g for g in gastos if "NETFLIX" in g.descripcion)
    assert netflix.suscripcion_id == suscripciones[0].id
    assert resultado.suscripciones_vinculadas == 1


def test_tc006_comercio_reconocido_con_suscripcion_activa_existente_la_reutiliza(db_session):
    casa, admin_id, tarjeta = _armar_casa_con_tarjeta(db_session)

    primera = importar_resumen(casa.id, tarjeta.id, _construir_pdf_resumen_bbva(), admin_id)
    session = db_session()
    try:
        (suscripcion_existente,) = (
            session.query(Suscripcion)
            .filter(Suscripcion.casa_id == casa.id, Suscripcion.descripcion == "NETFLIX.COM")
            .all()
        )
        suscripcion_id_original = suscripcion_existente.id
    finally:
        session.close()

    # Cierre distinto en la segunda importación (spec `resumen-tarjeta-
    # pago`, REQ-002): reimportar EXACTAMENTE el mismo resumen (mismo
    # cierre) ahora se rechaza — este test ejercita "reutiliza la
    # suscripción activa existente" con un ciclo de facturación nuevo,
    # no con un resumen duplicado.
    segunda = importar_resumen(
        casa.id,
        tarjeta.id,
        _construir_pdf_resumen_bbva(cierre="27-Sep-26", vencimiento="07-Oct-26"),
        admin_id,
    )

    session = db_session()
    try:
        suscripciones = (
            session.query(Suscripcion)
            .filter(Suscripcion.casa_id == casa.id, Suscripcion.descripcion == "NETFLIX.COM")
            .all()
        )
    finally:
        session.close()
    assert len(suscripciones) == 1
    assert suscripciones[0].id == suscripcion_id_original
    assert primera.suscripciones_vinculadas == 1
    assert segunda.suscripciones_vinculadas == 1


def test_tc007_comercio_reconocido_sin_permiso_cae_a_gasto_suelto_sin_fallar_el_resto(
    db_session,
):
    casa, admin_id, tarjeta = _armar_casa_con_tarjeta(db_session)
    ana = _agregar_miembro_no_admin(db_session, casa.id, admin_id)

    resultado = importar_resumen(casa.id, tarjeta.id, _construir_pdf_resumen_bbva(), ana.id)

    session = db_session()
    try:
        suscripciones = (
            session.query(Suscripcion)
            .filter(Suscripcion.casa_id == casa.id, Suscripcion.descripcion == "NETFLIX.COM")
            .all()
        )
    finally:
        session.close()
    assert suscripciones == []

    gastos = _gastos_de(db_session, casa.id)
    netflix = next(g for g in gastos if "NETFLIX" in g.descripcion)
    assert netflix.suscripcion_id is None
    assert str(netflix.importe) == "3999.00"
    assert resultado.suscripciones_vinculadas == 0
    # El resto de la importación no se vio afectado por la degradación de
    # esta línea puntual (REQ-004): las demás líneas se importaron igual.
    assert any("SUPERMERCADO" in g.descripcion for g in gastos)
    assert any("AMAZON" in g.descripcion for g in gastos)
    assert len([g for g in gastos if "ELECTRODOMESTICOS" in g.descripcion]) == 3


def test_tc008_lineas_de_impuestos_y_cargos_nunca_generan_gastos(db_session):
    casa, admin_id, tarjeta = _armar_casa_con_tarjeta(db_session)

    importar_resumen(casa.id, tarjeta.id, _construir_pdf_resumen_bbva(), admin_id)

    gastos = _gastos_de(db_session, casa.id)
    assert not any("COMISION" in g.descripcion for g in gastos)
    assert not any("SELLOS" in g.descripcion for g in gastos)
