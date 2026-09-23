"""T1 (spec `gamificacion-puntos`) — niveles, rachas y ranking por mes.

Cubre TC-001 (niveles cruzando cada umbral), TC-002 (racha consecutiva se
acumula, sin duplicar por más de una tarea el mismo día) y TC-003/TC-004
(un día sin actividad corta la racha; `calcular_ranking` filtrado por mes
vs. sin filtro, regresión de `dashboard_service`).
"""
import importlib
import uuid
from datetime import date, datetime, time, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models.historial_tarea import HistorialTarea
from src.db.models.usuario import Usuario
from src.services.casa_service import crear_casa
from src.services.miembro_service import agregar_miembro
from src.services.ranking_service import _nivel_de, calcular_racha, calcular_ranking
from src.services.tarea_service import completar_tarea, crear_tarea


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
    migracion_casas = importlib.import_module("src.db.migrations.0001_casas_miembros")
    migracion_tareas = importlib.import_module("src.db.migrations.0003_tareas")
    migracion_actividad = importlib.import_module("src.db.migrations.0004_historial_actividad")
    migracion_usuarios = importlib.import_module("src.db.migrations.0005_usuarios")
    # 0021 (spec `avatares-economia`): `completar_tarea` ahora también
    # otorga créditos (`avatar_service.otorgar_creditos`), que requiere la
    # tabla `credito_transacciones`.
    migracion_creditos = importlib.import_module("src.db.migrations.0021_creditos")
    migracion_casas.upgrade(engine)
    migracion_tareas.upgrade(engine)
    migracion_actividad.upgrade(engine)
    migracion_usuarios.upgrade(engine)
    migracion_creditos.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.tarea_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.ranking_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.actividad_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.avatar_service.get_session", lambda: TestSession())
    yield TestSession


def _completar_en_fecha(session_factory, tarea_id, miembro_id, actor_id, fecha: date):
    """Completa una tarea y luego fuerza `completada_en` a `fecha` (mediodía
    UTC ingenuo) — `completar_tarea` no acepta una fecha explícita, así que
    los tests de racha reescriben la columna directo, mismo criterio ya
    usado por otras specs para simular actividad en fechas puntuales."""
    historial = completar_tarea(tarea_id, miembro_id, actor_id)
    session = session_factory()
    try:
        fila = session.get(HistorialTarea, historial.id)
        fila.completada_en = datetime.combine(fecha, time(12, 0))
        session.commit()
    finally:
        session.close()
    return historial


def test_niveles_cruzando_cada_umbral(db_session):
    """TC-001: 0 puntos -> Novato; 50 -> Activo; 150 -> Comprometido; 300 ->
    Campeón de la casa. Un miembro con 0 puntos no tiene ninguna fila en
    `HistorialTarea` todavía, así que no aparece en `calcular_ranking`
    (mismo comportamiento ya establecido) — se prueba `_nivel_de`
    directamente para ese caso."""
    assert _nivel_de(0) == "Novato"

    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)

    for umbral_puntos, nivel_esperado in ((50, "Activo"), (100, "Comprometido"), (150, "Campeón de la casa")):
        tarea = crear_tarea(casa.id, "Tarea", umbral_puntos, actor=admin_id)
        completar_tarea(tarea.id, ana.id, ana.id)
        ranking = calcular_ranking(casa.id)
        entrada_ana = next(fila for fila in ranking if fila["miembroId"] == ana.id)
        assert entrada_ana["nivel"] == nivel_esperado


def test_racha_consecutiva_se_acumula_sin_duplicar_por_dia(db_session):
    """TC-002/TC-003: 3 días consecutivos con actividad (uno de ellos con
    dos tareas) acumulan racha de 3, no de 4."""
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)

    hoy = date.today()
    for offset in (2, 1, 0):
        tarea = crear_tarea(casa.id, "Tarea", 5, actor=admin_id)
        _completar_en_fecha(db_session, tarea.id, ana.id, ana.id, hoy - timedelta(days=offset))

    # Segunda tarea completada HOY también — no debe sumar un segundo día.
    tarea_extra = crear_tarea(casa.id, "Tarea extra", 5, actor=admin_id)
    _completar_en_fecha(db_session, tarea_extra.id, ana.id, ana.id, hoy)

    assert calcular_racha(casa.id, ana.id) == 3


def test_un_dia_sin_actividad_corta_la_racha(db_session):
    """Un hueco en la secuencia de días corta el conteo ahí — no sigue
    contando actividad más antigua que el hueco."""
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)

    hoy = date.today()
    # Actividad hoy y ayer, pero NO anteayer (hueco), y sí hace 3 días.
    for offset in (3, 1, 0):
        tarea = crear_tarea(casa.id, "Tarea", 5, actor=admin_id)
        _completar_en_fecha(db_session, tarea.id, ana.id, ana.id, hoy - timedelta(days=offset))

    assert calcular_racha(casa.id, ana.id) == 2


def test_racha_es_cero_sin_actividad_reciente(db_session):
    """Si la actividad más reciente no es de hoy ni de ayer, la racha es 0."""
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)

    tarea = crear_tarea(casa.id, "Tarea", 5, actor=admin_id)
    _completar_en_fecha(db_session, tarea.id, ana.id, ana.id, date.today() - timedelta(days=3))

    assert calcular_racha(casa.id, ana.id) == 0


def test_racha_es_cero_sin_ninguna_actividad(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    assert calcular_racha(casa.id, casa.miembros[0].id) == 0


def test_ranking_filtrado_por_mes_vs_sin_filtro(db_session):
    """TC-004: `calcular_ranking(casa_id, mes="2026-09")` solo cuenta puntos
    de ese mes; sin `mes`, sigue siendo el total histórico (regresión)."""
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)

    tarea_agosto = crear_tarea(casa.id, "Tarea de agosto", 20, actor=admin_id)
    _completar_en_fecha(db_session, tarea_agosto.id, ana.id, ana.id, date(2026, 8, 15))
    tarea_septiembre = crear_tarea(casa.id, "Tarea de septiembre", 10, actor=admin_id)
    _completar_en_fecha(db_session, tarea_septiembre.id, ana.id, ana.id, date(2026, 9, 1))

    ranking_septiembre = calcular_ranking(casa.id, mes="2026-09")
    entrada_septiembre = next(fila for fila in ranking_septiembre if fila["miembroId"] == ana.id)
    assert entrada_septiembre["puntos"] == 10

    ranking_agosto = calcular_ranking(casa.id, mes="2026-08")
    entrada_agosto = next(fila for fila in ranking_agosto if fila["miembroId"] == ana.id)
    assert entrada_agosto["puntos"] == 20

    ranking_total = calcular_ranking(casa.id)
    entrada_total = next(fila for fila in ranking_total if fila["miembroId"] == ana.id)
    assert entrada_total["puntos"] == 30


def test_nivel_de_entrada_de_ranking_usa_total_historico_no_el_filtrado_por_mes(db_session):
    """El `nivel` de cada entrada se calcula sobre el total histórico del
    miembro, nunca sobre el total filtrado por mes (00-overview.md)."""
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)

    tarea_agosto = crear_tarea(casa.id, "Tarea de agosto", 200, actor=admin_id)
    _completar_en_fecha(db_session, tarea_agosto.id, ana.id, ana.id, date(2026, 8, 15))
    tarea_septiembre = crear_tarea(casa.id, "Tarea de septiembre", 5, actor=admin_id)
    _completar_en_fecha(db_session, tarea_septiembre.id, ana.id, ana.id, date(2026, 9, 1))

    # Filtrado por septiembre: solo 5 puntos ese mes (Novato), pero el nivel
    # sigue reflejando el total histórico (205 puntos -> Comprometido).
    ranking_septiembre = calcular_ranking(casa.id, mes="2026-09")
    entrada = next(fila for fila in ranking_septiembre if fila["miembroId"] == ana.id)
    assert entrada["puntos"] == 5
    assert entrada["nivel"] == "Comprometido"


# Regresión de `dashboard_service.armar_dashboard` (llama a
# `calcular_ranking(casa_id)` sin `mes`): cubierta por la propia suite de
# `tests/unit/services/dashboard_service.test.py`, que no se modifica en
# esta spec — ver `run-plan.json`'s contract y `Done When` de T1.
