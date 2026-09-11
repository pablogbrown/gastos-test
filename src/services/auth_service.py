"""Servicio de autenticación: registro, login, hashing y JWT (spec
`usuarios-auth`).

Aislado de `casa_service`/`miembro_service` (un servicio por
responsabilidad, mismo principio ya establecido en el proyecto —
`permisos.py` sigue el mismo patrón). Nada de esto conoce Casa/Miembro:
resuelve únicamente la identidad global (`Usuario`).
"""
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

import bcrypt
import jwt
from sqlalchemy.exc import IntegrityError

from src.db.base import get_session
from src.db.models.usuario import Usuario
from src.services.exceptions import ConflictError, InvalidCredentialsError, ValidationError

# Mismo patrón que `DATABASE_URL` en `src/db/base.py`: variable de entorno
# con un default de desarrollo si no está seteada. En un despliegue real
# (`.nybo/foundation/stack.yaml`) `JWT_SECRET` se configura explícitamente.
JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-no-usar-en-produccion")
JWT_ALGORITHM = "HS256"
JWT_EXPIRACION = timedelta(hours=24)


def _hashear_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verificar_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        # Hash corrupto/con formato inesperado: nunca autentica, pero
        # tampoco es un 500 — se trata igual que credenciales inválidas.
        return False


def registrar_usuario(email: str, password: str, nombre: Optional[str] = None) -> Usuario:
    """Crea un Usuario nuevo (REQ-001).

    La contraseña se hashea con `bcrypt` antes de persistirse — nunca en
    texto plano (TC-001). Rechaza un email ya registrado con
    `ConflictError` (409, TC-002) — no una `ValidationError` (400), para
    distinguir "dato con forma inválida" de "el recurso ya existe".
    """
    if not email or not str(email).strip():
        raise ValidationError("El email no puede estar vacío.")
    if not password:
        raise ValidationError("La contraseña no puede estar vacía.")

    email_normalizado = email.strip().lower()

    session = get_session()
    try:
        existente = (
            session.query(Usuario).filter(Usuario.email == email_normalizado).one_or_none()
        )
        if existente is not None:
            raise ConflictError(f"Ya existe un usuario registrado con el email {email_normalizado!r}.")

        usuario = Usuario(
            id=uuid.uuid4(),
            email=email_normalizado,
            password_hash=_hashear_password(password),
            nombre=nombre.strip() if nombre else None,
        )
        session.add(usuario)
        try:
            session.commit()
        except IntegrityError as exc:
            session.rollback()
            raise ConflictError(
                f"Ya existe un usuario registrado con el email {email_normalizado!r}."
            ) from exc
        session.refresh(usuario)
        return usuario
    except (ValidationError, ConflictError):
        session.rollback()
        raise
    finally:
        session.close()


def autenticar_usuario(email: str, password: str) -> Usuario:
    """Verifica credenciales (REQ-002).

    Si el email no existe o la contraseña no matchea, lanza siempre la
    misma `InvalidCredentialsError` con el mismo mensaje (TC-004) — nunca
    revela cuál de las dos causas ocurrió.
    """
    email_normalizado = (email or "").strip().lower()

    session = get_session()
    try:
        usuario = session.query(Usuario).filter(Usuario.email == email_normalizado).one_or_none()
        if usuario is None or not _verificar_password(password or "", usuario.password_hash):
            raise InvalidCredentialsError("Email o contraseña incorrectos.")
        return usuario
    finally:
        session.close()


def emitir_token(usuario_id: UUID) -> str:
    """Genera un JWT con `sub=usuario_id` y expiración corta (24h)."""
    ahora = datetime.now(timezone.utc)
    payload = {
        "sub": str(usuario_id),
        "iat": ahora,
        "exp": ahora + JWT_EXPIRACION,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decodificar_token(token: str) -> UUID:
    """Verifica firma y expiración de `token`, devuelve el `usuario_id`.

    Lanza `InvalidCredentialsError` si el token es inválido, está mal
    formado o expiró (TC-005) — nunca deja pasar una excepción cruda de
    `pyjwt` hacia la capa de rutas.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return UUID(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise InvalidCredentialsError("Token inválido o expirado.") from exc
