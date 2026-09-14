"""Dependencies de FastAPI para la identidad autenticada (spec `usuarios-auth`).

Reemplaza el header placeholder `X-Usuario-Id` que usaban `casas.py`,
`gastos.py`, `tareas.py` y `dashboard.py`: centraliza acá la extracción y
validación del JWT una única vez, en vez de duplicar la lógica en cada
router — cambia acá, se propaga a los 4.
"""
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status

from src.services.auth_service import decodificar_token
from src.services.exceptions import InvalidCredentialsError, NotFoundError, PermissionDeniedError
from src.services.miembro_service import resolver_actor_en_casa as _resolver_actor_en_casa

_PREFIJO_BEARER = "Bearer "


def get_current_usuario(authorization: str = Header(default=None)) -> UUID:
    """Decodifica el JWT del header `Authorization: Bearer <token>` y
    devuelve el `usuario_id` (identidad global) del Usuario autenticado.

    Sin header, con un esquema distinto de `Bearer`, o con un token
    inválido/expirado, responde 401 (TC-005) — reemplaza el 422 genérico
    que devolvía un `X-Usuario-Id` ausente.
    """
    if not authorization or not authorization.startswith(_PREFIJO_BEARER):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado."
        )

    token = authorization[len(_PREFIJO_BEARER) :].strip()
    try:
        return decodificar_token(token)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)
        ) from exc


def resolver_actor_en_casa(
    casa_id: UUID, usuario_id: UUID = Depends(get_current_usuario)
) -> UUID:
    """Dependency compuesta: resuelve el Usuario autenticado (JWT) y lo
    traduce al `Miembro.id` que tiene en la Casa `casa_id` de la ruta.

    Es lo que reciben como `actor`/`usuario_id` los handlers de
    `casas.py`/`gastos.py`/`tareas.py`/`dashboard.py` que operan sobre una
    Casa puntual (REQ-003, REQ-005): 401 si no hay JWT válido (delegado a
    `get_current_usuario`), 404 si la Casa no existe, 403 si el Usuario no
    es miembro activo de ella (TC-009).
    """
    try:
        return _resolver_actor_en_casa(casa_id, usuario_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
