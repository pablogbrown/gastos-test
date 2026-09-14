"""T1 (dockerize-local-env) — TC-004: las 4 migraciones existentes corren
limpias contra un PostgreSQL real, no solo contra el SQLite usado por el
resto de la suite.

Reutiliza `run_migrations` (`src/db/migrate.py`) sin reimplementar el
orden de migraciones — ver Design Rationale de T1.

Cómo obtiene un Postgres real:
1. Si `TEST_DATABASE_URL` (o `DATABASE_URL`, cuando ya apunta a Postgres —
   caso `docker compose exec backend pytest`, con el servicio `db` ya
   arriba) está seteada, se usa tal cual: no se administra su ciclo de
   vida, se asume que ya está lista para aceptar conexiones.
2. Si no, se levanta un contenedor `postgres:16-alpine` efímero vía
   `docker run` en un puerto libre del host, se espera a que acepte
   conexiones, y se lo destruye al terminar.
3. Si el binario `docker` no está disponible o el daemon no responde, el
   test se skippea con un motivo explícito — no se asume el resultado por
   inspección de código, pero tampoco se rompe la suite en un entorno sin
   Docker.
"""
import os
import shutil
import socket
import subprocess
import time
import uuid

import pytest
import sqlalchemy

from src.db.migrate import run_migrations

_CONTAINER_NAME = "taskia-test-postgres-migrations"


def _puerto_libre() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _docker_disponible() -> bool:
    if shutil.which("docker") is None:
        return False
    try:
        subprocess.run(
            ["docker", "info"], capture_output=True, timeout=10, check=True
        )
    except Exception:
        return False
    return True


def _esperar_postgres(dsn: str, intentos: int = 60) -> None:
    ultimo_error = None
    for _ in range(intentos):
        try:
            engine = sqlalchemy.create_engine(dsn)
            with engine.connect():
                engine.dispose()
                return
        except Exception as exc:  # noqa: BLE001 - reintenta hasta el timeout
            ultimo_error = exc
            time.sleep(1)
    raise RuntimeError(f"Postgres no aceptó conexiones a tiempo: {ultimo_error}")


@pytest.fixture(scope="module")
def postgres_dsn():
    externa = os.environ.get("TEST_DATABASE_URL") or (
        os.environ.get("DATABASE_URL")
        if (os.environ.get("DATABASE_URL") or "").startswith("postgresql")
        else None
    )
    if externa:
        yield externa
        return

    if not _docker_disponible():
        pytest.skip("Docker no disponible en este entorno — TC-004 requiere un Postgres real.")

    subprocess.run(["docker", "rm", "-f", _CONTAINER_NAME], capture_output=True)
    puerto = _puerto_libre()
    dsn = f"postgresql+psycopg2://taskia:taskia@127.0.0.1:{puerto}/taskia"

    proc = subprocess.run(
        [
            "docker", "run", "-d", "--rm",
            "--name", _CONTAINER_NAME,
            "-e", "POSTGRES_USER=taskia",
            "-e", "POSTGRES_PASSWORD=taskia",
            "-e", "POSTGRES_DB=taskia",
            "-p", f"{puerto}:5432",
            "postgres:16-alpine",
        ],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        pytest.skip(f"No se pudo levantar Postgres efímero para TC-004: {proc.stderr}")

    try:
        _esperar_postgres(dsn)
        yield dsn
    finally:
        subprocess.run(["docker", "rm", "-f", _CONTAINER_NAME], capture_output=True)


def test_las_4_migraciones_corren_limpias_contra_postgres_real(postgres_dsn):
    engine = sqlalchemy.create_engine(postgres_dsn)
    try:
        # No debe lanzar sobre una base Postgres vacía.
        run_migrations(engine)

        inspector = sqlalchemy.inspect(engine)
        tablas = set(inspector.get_table_names())
        assert {"casas", "miembros", "gastos", "tareas", "historial_actividad"} <= tablas

        # El enum de rol se creó como tipo nativo de Postgres, no como texto libre.
        columnas_miembro = {c["name"]: c for c in inspector.get_columns("miembros")}
        assert "rol" in columnas_miembro

        # Correr las migraciones dos veces debe ser idempotente (create_all
        # con checkfirst=True) — relevante porque main.py las corre en cada
        # arranque del backend dentro de docker-compose.
        run_migrations(engine)
    finally:
        engine.dispose()


def test_migracion_0006_agrega_miembro_desactivado_a_un_enum_ya_existente(postgres_dsn):
    """Regresión (spec `fix-historial-desactivacion-miembro`): un Postgres
    con `historial_actividad` ya creado ANTES de este fix (tipo enum
    nativo con solo los 5 valores originales, como el volumen persistente
    de `docker-compose` de este proyecto) debe poder registrar
    `MIEMBRO_DESACTIVADO` después de correr las migraciones — sin
    recrear el esquema ni perder datos. `0006` fue agregada precisamente
    porque el smoke test en vivo contra ese entorno encontró
    `psycopg2.errors.InvalidTextRepresentation` antes de que existiera.
    """
    engine = sqlalchemy.create_engine(postgres_dsn)
    try:
        # `postgres_dsn` es module-scoped y comparte el Postgres con el test
        # anterior, que ya corrió las migraciones (incluida `historial_
        # actividad`/`tipoactividadenum` con el enum ya al día) — se
        # descartan acá para recrear desde cero el escenario "enum viejo,
        # sin MIEMBRO_DESACTIVADO" que este test necesita.
        with engine.begin() as conn:
            conn.execute(sqlalchemy.text("DROP TABLE IF EXISTS historial_actividad"))
            conn.execute(sqlalchemy.text("DROP TYPE IF EXISTS tipoactividadenum"))
        with engine.begin() as conn:
            conn.execute(
                sqlalchemy.text(
                    "CREATE TYPE tipoactividadenum AS ENUM ("
                    "'GASTO_REGISTRADO', 'TAREA_CREADA', 'TAREA_COMPLETADA', "
                    "'PUNTOS_OBTENIDOS', 'MIEMBRO_AGREGADO')"
                )
            )
            conn.execute(
                sqlalchemy.text(
                    "CREATE TABLE historial_actividad ("
                    "id UUID PRIMARY KEY, casa_id UUID NOT NULL, "
                    "tipo tipoactividadenum NOT NULL, miembro_id UUID, "
                    "fecha TIMESTAMP NOT NULL, descripcion VARCHAR NOT NULL)"
                )
            )

        # Corre TODAS las migraciones, incluida 0006, sobre esta base que
        # ya tenía `historial_actividad` con el enum viejo.
        run_migrations(engine)

        # Antes no aceptaba este valor (InvalidTextRepresentation) — ahora sí.
        with engine.begin() as conn:
            conn.execute(
                sqlalchemy.text(
                    "INSERT INTO historial_actividad "
                    "(id, casa_id, tipo, miembro_id, fecha, descripcion) VALUES "
                    "(:id, :casa_id, 'MIEMBRO_DESACTIVADO', NULL, now(), 'test')"
                ),
                {"id": str(uuid.uuid4()), "casa_id": str(uuid.uuid4())},
            )
    finally:
        with engine.begin() as conn:
            conn.execute(sqlalchemy.text("DROP TABLE IF EXISTS historial_actividad"))
            conn.execute(sqlalchemy.text("DROP TYPE IF EXISTS tipoactividadenum"))
        engine.dispose()
