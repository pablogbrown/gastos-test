"""T1 (dockerize-local-env) — TC-004: las 4 migraciones existentes corren
limpias contra un PostgreSQL real, no solo contra el SQLite usado por el
resto de la suite.

Reutiliza `run_migrations` (`src/db/migrate.py`) sin reimplementar el
orden de migraciones — ver Design Rationale de T1.

Cómo obtiene un Postgres real:
1. Si `TEST_DATABASE_URL` (o `DATABASE_URL`, cuando ya apunta a Postgres —
   caso `docker compose exec backend pytest`, con el servicio `db` ya
   arriba) está seteada, se usa como *servidor* (no como base de datos):
   se crea una base de datos temporal nueva en ese mismo server y se
   opera solo sobre ella — nunca directamente sobre la base apuntada por
   la URL (fix `fix-test-migraciones-borra-tabla-real`: antes, un test de
   este archivo hacía `DROP TABLE`/`DROP TYPE` en su `finally` contra la
   base real del docker-compose de desarrollo, borrando `historial_
   actividad` de la base compartida cada vez que corría la suite contra
   Postgres real).
2. Si no, se levanta un contenedor `postgres:16-alpine` efímero vía
   `docker run` en un puerto libre del host, se espera a que acepte
   conexiones, y se lo destruye al terminar (ya aislado por diseño — no
   toca el punto 1).
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
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from src.db.migrate import run_migrations


def _crear_base_temporal(dsn_servidor: str) -> str:
    """Crea una base de datos nueva y vacía en el mismo server que `dsn_servidor`
    apunta, y devuelve la URL a esa base — nunca opera sobre la base original."""
    url_base = make_url(dsn_servidor)
    nombre_temporal = f"test_migrations_{uuid.uuid4().hex[:12]}"
    admin_engine = sqlalchemy.create_engine(
        url_base.set(database="postgres"), isolation_level="AUTOCOMMIT"
    )
    try:
        with admin_engine.connect() as conn:
            conn.execute(sqlalchemy.text(f'CREATE DATABASE "{nombre_temporal}"'))
    finally:
        admin_engine.dispose()
    # `str(URL)`/`repr(URL)` enmascaran la contraseña como "***" a propósito
    # (no filtrarla en logs) — hay que pedir el string real explícitamente.
    return url_base.set(database=nombre_temporal).render_as_string(hide_password=False)


def _borrar_base_temporal(dsn_servidor: str, dsn_temporal: str) -> None:
    nombre_temporal = make_url(dsn_temporal).database
    url_base = make_url(dsn_servidor)
    admin_engine = sqlalchemy.create_engine(
        url_base.set(database="postgres"), isolation_level="AUTOCOMMIT"
    )
    try:
        with admin_engine.connect() as conn:
            conn.execute(
                sqlalchemy.text(f'DROP DATABASE IF EXISTS "{nombre_temporal}" WITH (FORCE)')
            )
    finally:
        admin_engine.dispose()

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
        # Nunca operar directamente sobre la base apuntada por `externa` —
        # en `docker compose exec backend pytest` eso ES la base real de
        # desarrollo. Crear una base temporal en el mismo server y usar
        # solo esa; se borra al terminar, la base real queda intacta.
        temporal = _crear_base_temporal(externa)
        try:
            yield temporal
        finally:
            _borrar_base_temporal(externa, temporal)
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


def test_dsn_externa_nunca_se_toca_directamente():
    """Regresión (fix `fix-test-migraciones-borra-tabla-real`): cuando
    `DATABASE_URL` ya apunta a Postgres (caso `docker compose exec backend
    pytest`, contra la base real de desarrollo), el fixture `postgres_dsn`
    debe operar sobre una base temporal nueva — nunca sobre la base
    original — y esa base temporal debe desaparecer al terminar, dejando
    la original completamente intacta.

    No usa el fixture `postgres_dsn` (module-scoped, ya consumido por los
    tests de arriba) — ejercita `_crear_base_temporal`/`_borrar_base_temporal`
    directo, contra `DATABASE_URL` si está seteada a Postgres, para poder
    inspeccionar el nombre de la base ANTES de que el fixture la reemplace.
    """
    externa = os.environ.get("DATABASE_URL")
    if not (externa or "").startswith("postgresql"):
        pytest.skip("Requiere DATABASE_URL apuntando a Postgres real (docker-compose).")

    nombre_original = make_url(externa).database

    temporal = _crear_base_temporal(externa)
    try:
        assert make_url(temporal).database != nombre_original

        # La base temporal debe existir y ser distinta de la original.
        temp_engine = sqlalchemy.create_engine(temporal)
        with temp_engine.connect() as conn:
            assert conn.execute(sqlalchemy.text("select current_database()")).scalar() == make_url(
                temporal
            ).database
        temp_engine.dispose()
    finally:
        _borrar_base_temporal(externa, temporal)

    # La base temporal ya no debe existir tras el cleanup.
    admin_engine = sqlalchemy.create_engine(
        make_url(externa).set(database="postgres"), isolation_level="AUTOCOMMIT"
    )
    try:
        with admin_engine.connect() as conn:
            existe = conn.execute(
                sqlalchemy.text("SELECT 1 FROM pg_database WHERE datname = :nombre"),
                {"nombre": make_url(temporal).database},
            ).scalar()
        assert existe is None
    finally:
        admin_engine.dispose()

    # La base ORIGINAL sigue intacta — sigue existiendo y sigue siendo la
    # misma (no fue reemplazada ni renombrada).
    original_engine = sqlalchemy.create_engine(externa)
    try:
        with original_engine.connect() as conn:
            assert (
                conn.execute(sqlalchemy.text("select current_database()")).scalar()
                == nombre_original
            )
    finally:
        original_engine.dispose()


def test_las_4_migraciones_corren_limpias_contra_postgres_real(postgres_dsn):
    engine = sqlalchemy.create_engine(postgres_dsn)
    try:
        # No debe lanzar sobre una base Postgres vacía.
        run_migrations(engine)

        inspector = sqlalchemy.inspect(engine)
        tablas = set(inspector.get_table_names())
        assert {
            "casas",
            "miembros",
            "gastos",
            "tareas",
            "historial_actividad",
            "suscripciones",
        } <= tablas

        # El enum de rol se creó como tipo nativo de Postgres, no como texto libre.
        columnas_miembro = {c["name"]: c for c in inspector.get_columns("miembros")}
        assert "rol" in columnas_miembro

        # T1 (spec `gastos-suscripcion-mensual`): `gastos.suscripcion_id`
        # existe como columna nullable tras la migración 0009.
        columnas_gasto = {c["name"]: c for c in inspector.get_columns("gastos")}
        assert "suscripcion_id" in columnas_gasto
        assert columnas_gasto["suscripcion_id"]["nullable"] is True

        # T1 (spec `gastos-multi-moneda`): `gastos.moneda`/
        # `suscripciones.moneda` existen tras la migración 0010, NOT NULL
        # con default 'ARS'.
        assert "moneda" in columnas_gasto
        assert columnas_gasto["moneda"]["nullable"] is False
        columnas_suscripcion = {c["name"]: c for c in inspector.get_columns("suscripciones")}
        assert "moneda" in columnas_suscripcion
        assert columnas_suscripcion["moneda"]["nullable"] is False

        # Correr las migraciones dos veces debe ser idempotente (create_all
        # con checkfirst=True, y los ALTER TABLE ... ADD COLUMN IF NOT
        # EXISTS de 0008-0010) — relevante porque main.py las corre en cada
        # arranque del backend dentro de docker-compose.
        run_migrations(engine)

        # Una tercera pasada (spec `gastos-multi-moneda`, T1 "Done When":
        # verificar idempotencia explícitamente para la migración nueva)
        # tampoco debe lanzar.
        run_migrations(engine)

        # Comportamiento de default 'ARS' contra Postgres real: insertar un
        # Gasto/Suscripcion sin `moneda` explícita (vía el ORM, mismo
        # criterio que `Suscripcion.activa` — default de Python en el
        # `Column`, no `server_default`) persiste "ARS", igual que ya
        # cubre `tests/unit/db/gasto_suscripcion_moneda.test.py` contra
        # SQLite.
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            from src.db.models.casa import Casa
            from src.db.models.categoria import Categoria
            from src.db.models.gasto import Gasto
            from src.db.models.miembro import Miembro, RolEnum
            from src.db.models.suscripcion import Suscripcion

            casa = Casa(id=uuid.uuid4(), nombre="Casa Postgres")
            session.add(casa)
            session.flush()
            miembro = Miembro(
                id=uuid.uuid4(),
                casa_id=casa.id,
                nombre="Pablo",
                identificacion="P-1",
                rol=RolEnum.ADMIN,
            )
            session.add(miembro)
            categoria = Categoria(id=uuid.uuid4(), casa_id=casa.id, nombre="Supermercado")
            session.add(categoria)
            session.flush()
            casa_id, miembro_id, categoria_id = casa.id, miembro.id, categoria.id

            gasto = Gasto(
                id=uuid.uuid4(),
                casa_id=casa_id,
                descripcion="Sin moneda explícita",
                importe=10,
                fecha=sqlalchemy.func.current_date(),
                pagado_por=miembro_id,
                categoria_id=categoria_id,
            )
            session.add(gasto)
            suscripcion = Suscripcion(
                id=uuid.uuid4(),
                casa_id=casa_id,
                descripcion="Sin moneda explícita",
                importe=10,
                categoria_id=categoria_id,
                pagado_por=miembro_id,
            )
            session.add(suscripcion)
            session.commit()

            session.refresh(gasto)
            session.refresh(suscripcion)
            assert gasto.moneda == "ARS"
            assert suscripcion.moneda == "ARS"
        finally:
            session.close()
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
