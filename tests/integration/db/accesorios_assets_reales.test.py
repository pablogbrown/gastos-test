"""Fix `avatar-assets-fallback` (continuación) — migración `0027_
accesorios_assets_reales`: reemplaza las URLs placeholder de
`asset_overlay_url` sembradas por `0024_accesorio_catalogo` por íconos
SVG reales servidos localmente (`public/accesorios/*.svg`).
"""
import importlib

from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

from src.db.models.accesorio_avatar import AccesorioAvatar  # noqa: F401
from src.db.models.avatar_personaje import AvatarPersonaje  # noqa: F401
from src.db.models.miembro_avatar_seleccionado import MiembroAvatarSeleccionado  # noqa: F401

# Mismo motivo que en `tienda_catalogo.test.py`: registrar los mappers
# pendientes antes de tocar cualquier tabla bajo `src.db.models.*`.
from src.db.models.usuario import Usuario  # noqa: F401


def _engine_con_migraciones():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    for nombre in (
        "0001_casas_miembros",
        "0003_tareas",
        "0004_historial_actividad",
        "0020_gamificacion",
        "0022_avatar_catalogo",
        "0023_avatar_seleccionado",
        "0024_accesorio_catalogo",
        "0027_accesorios_assets_reales",
    ):
        importlib.import_module(f"src.db.migrations.{nombre}").upgrade(engine)
    return engine


def test_reemplaza_urls_placeholder_por_iconos_locales():
    engine = _engine_con_migraciones()

    with engine.connect() as conn:
        filas = conn.execute(
            text("SELECT nombre, asset_overlay_url FROM accesorios_avatar")
        ).fetchall()

    assert len(filas) == 18
    for nombre, url in filas:
        assert url.startswith("/accesorios/"), f"{nombre!r} sigue apuntando a {url!r}"
        assert "lottiefiles.com" not in url, f"{nombre!r} sigue siendo un placeholder externo"
        assert url.endswith(".svg")


def test_es_idempotente_correr_dos_veces():
    engine = _engine_con_migraciones()
    # Volver a correr la misma migración de datos no debe romper ni
    # duplicar nada — mismo criterio que cualquier UPDATE idempotente de
    # este proyecto.
    importlib.import_module("src.db.migrations.0027_accesorios_assets_reales").upgrade(engine)

    with engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM accesorios_avatar")).scalar()
        url_gorro = conn.execute(
            text("SELECT asset_overlay_url FROM accesorios_avatar WHERE nombre = 'Gorro de lana'")
        ).scalar()

    assert total == 18
    assert url_gorro == "/accesorios/gorro-de-lana.svg"
