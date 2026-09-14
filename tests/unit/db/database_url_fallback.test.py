"""T1 (dockerize-local-env) — Confirma que src/db/base.py no cambió su
comportamiento de fallback al agregar el wiring de Docker.

TC-003: sin DATABASE_URL seteada, el engine sigue usando sqlite:///:memory:
exactamente como antes de esta spec (los tests unitarios/integración de
otras specs dependen de ese default). Se corre en un subproceso limpio
porque src/db/base.py lee la variable de entorno una sola vez, al
importarse — el proceso de pytest ya puede tener el módulo importado (o
la variable seteada por otro test) y eso enmascararía el resultado.
"""
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def _run_en_subproceso(codigo: str, env_overrides: dict) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env.pop("DATABASE_URL", None)
    env.update(env_overrides)
    return subprocess.run(
        [sys.executable, "-c", codigo],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
    )


def test_sin_database_url_usa_sqlite_en_memoria():
    codigo = (
        "from src.db.base import DATABASE_URL, engine\n"
        "assert DATABASE_URL == 'sqlite:///:memory:', DATABASE_URL\n"
        "assert str(engine.url) == 'sqlite:///:memory:', str(engine.url)\n"
    )
    result = _run_en_subproceso(codigo, {})
    assert result.returncode == 0, result.stderr


def test_con_database_url_seteada_el_engine_la_respeta():
    dsn = "postgresql+psycopg2://taskia:taskia@db:5432/taskia"
    codigo = (
        "from src.db.base import DATABASE_URL, engine\n"
        f"assert DATABASE_URL == {dsn!r}, DATABASE_URL\n"
        # engine.url oculta el password al castear a str; se compara con
        # render_as_string(hide_password=False) para no falsear el test.
        f"assert engine.url.render_as_string(hide_password=False) == {dsn!r}, "
        "engine.url.render_as_string(hide_password=False)\n"
    )
    result = _run_en_subproceso(codigo, {"DATABASE_URL": dsn})
    assert result.returncode == 0, result.stderr
