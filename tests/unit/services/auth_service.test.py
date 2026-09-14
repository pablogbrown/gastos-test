"""T2 — Service Layer: auth_service (registro, login, hashing y JWT).

Cubre TC-001, TC-002, TC-003, TC-004 y el guard de token (usado por T3 en
`get_current_usuario`).
"""
import importlib
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import src.db.base as db_base
from src.services.auth_service import (
    autenticar_usuario,
    decodificar_token,
    emitir_token,
    registrar_usuario,
)
from src.services.exceptions import ConflictError, InvalidCredentialsError, ValidationError


@pytest.fixture(autouse=True)
def _sqlite_engine(monkeypatch):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    importlib.import_module("src.db.migrations.0001_casas_miembros").upgrade(engine)
    importlib.import_module("src.db.migrations.0005_usuarios").upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr(db_base, "engine", engine)
    monkeypatch.setattr(db_base, "SessionLocal", TestSession)
    monkeypatch.setattr("src.services.auth_service.get_session", lambda: TestSession())
    yield


def test_registrar_usuario_hashea_la_contrasena(monkeypatch):
    usuario = registrar_usuario("pablo@example.com", "hunter2", "Pablo")

    assert usuario.email == "pablo@example.com"
    assert usuario.password_hash != "hunter2"
    assert "hunter2" not in usuario.password_hash


def test_registrar_usuario_con_email_vacio_es_rechazado():
    with pytest.raises(ValidationError):
        registrar_usuario("", "hunter2")


def test_registrar_usuario_con_email_duplicado_es_rechazado():
    registrar_usuario("dup@example.com", "hunter2")

    with pytest.raises(ConflictError):
        registrar_usuario("dup@example.com", "otraClave")


def test_registrar_usuario_normaliza_email_a_minusculas_para_la_unicidad():
    registrar_usuario("Pablo@Example.com", "hunter2")

    with pytest.raises(ConflictError):
        registrar_usuario("pablo@example.com", "otraClave")


def test_autenticar_usuario_con_credenciales_correctas_devuelve_el_usuario():
    registrar_usuario("pablo@example.com", "hunter2", "Pablo")

    usuario = autenticar_usuario("pablo@example.com", "hunter2")

    assert usuario.email == "pablo@example.com"


def test_autenticar_usuario_con_password_incorrecta_lanza_invalid_credentials():
    registrar_usuario("pablo@example.com", "hunter2")

    with pytest.raises(InvalidCredentialsError):
        autenticar_usuario("pablo@example.com", "incorrecta")


def test_autenticar_usuario_con_email_inexistente_lanza_el_mismo_error():
    registrar_usuario("pablo@example.com", "hunter2")

    with pytest.raises(InvalidCredentialsError) as exc_email_incorrecto:
        autenticar_usuario("noexiste@example.com", "hunter2")

    with pytest.raises(InvalidCredentialsError) as exc_password_incorrecta:
        autenticar_usuario("pablo@example.com", "incorrecta")

    # Mismo mensaje en ambos casos (TC-004): no revela cuál email existe.
    assert str(exc_email_incorrecto.value) == str(exc_password_incorrecta.value)


def test_emitir_y_decodificar_token_devuelve_el_mismo_usuario_id():
    usuario = registrar_usuario("pablo@example.com", "hunter2")

    token = emitir_token(usuario.id)
    usuario_id_decodificado = decodificar_token(token)

    assert usuario_id_decodificado == usuario.id


def test_decodificar_token_invalido_lanza_invalid_credentials():
    with pytest.raises(InvalidCredentialsError):
        decodificar_token("esto-no-es-un-jwt")


def test_decodificar_token_expirado_lanza_invalid_credentials(monkeypatch):
    import jwt as pyjwt
    from datetime import datetime, timedelta, timezone

    import src.services.auth_service as auth_service

    usuario_id = uuid.uuid4()
    payload = {
        "sub": str(usuario_id),
        "iat": datetime.now(timezone.utc) - timedelta(hours=48),
        "exp": datetime.now(timezone.utc) - timedelta(hours=24),
    }
    token_expirado = pyjwt.encode(payload, auth_service.JWT_SECRET, algorithm=auth_service.JWT_ALGORITHM)

    with pytest.raises(InvalidCredentialsError):
        decodificar_token(token_expirado)
