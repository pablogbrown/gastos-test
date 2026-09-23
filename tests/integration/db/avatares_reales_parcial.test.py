"""Fix `avatar-assets-fallback` (continuación) — migración `0028_
avatares_reales_parcial`: reemplaza 4 de las 10 razas placeholder por
animaciones Lottie reales provistas por el usuario, dejando las 6
restantes como están (tratadas como "Próximamente" en el frontend).
"""
import importlib

from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

from src.db.models.accesorio_avatar import AccesorioAvatar  # noqa: F401
from src.db.models.avatar_personaje import AvatarPersonaje  # noqa: F401
from src.db.models.miembro_avatar_seleccionado import MiembroAvatarSeleccionado  # noqa: F401
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
        "0028_avatares_reales_parcial",
    ):
        importlib.import_module(f"src.db.migrations.{nombre}").upgrade(engine)
    return engine


def test_reemplaza_4_razas_con_animaciones_reales_y_deja_6_como_placeholder():
    engine = _engine_con_migraciones()

    with engine.connect() as conn:
        filas = conn.execute(text("SELECT raza, lottie_url, rareza FROM avatar_personajes")).fetchall()

    assert len(filas) == 10
    por_raza = {raza: (url, rareza) for raza, url, rareza in filas}

    reales = {
        "Happy Dog": "/avatares/happy-dog.json",
        "Norm The Dog": "/avatares/norm-the-dog.json",
        "Boxing with Bone - Angry Puppy": "/avatares/boxing-with-bone-angry-puppy.json",
        "Cat_in_Box": "/avatares/cat-in-box.json",
    }
    for raza, url_esperada in reales.items():
        assert raza in por_raza, f"falta la raza real {raza!r}"
        url, _ = por_raza[raza]
        assert url == url_esperada
        assert "lottiefiles.com" not in url

    # "Cat_in_Box" queda premium — mismo rareza tope que la raza que
    # reemplazó (Maine Coon, ya "legendario").
    assert por_raza["Cat_in_Box"][1] == "legendario"

    # Las 6 razas que no se tocan siguen siendo placeholder — el
    # frontend las trata como "Próximamente" a partir de esto.
    razas_viejas_reemplazadas = {"Beagle", "Labrador", "Pastor alemán", "Maine Coon"}
    restantes = set(por_raza) - set(reales)
    assert len(restantes) == 6
    assert razas_viejas_reemplazadas.isdisjoint(restantes)
    for raza in restantes:
        url, _ = por_raza[raza]
        assert "_placeholder.json" in url, f"{raza!r} debería seguir siendo placeholder"


def test_es_idempotente_correr_dos_veces():
    engine = _engine_con_migraciones()
    importlib.import_module("src.db.migrations.0028_avatares_reales_parcial").upgrade(engine)

    with engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM avatar_personajes")).scalar()
        url_happy_dog = conn.execute(
            text("SELECT lottie_url FROM avatar_personajes WHERE raza = 'Happy Dog'")
        ).scalar()

    assert total == 10
    assert url_happy_dog == "/avatares/happy-dog.json"
