"""Rutas HTTP de autenticación: registro y login (spec `usuarios-auth`).

Adaptador delgado sobre `auth_service`, mismo patrón que el resto de los
routers del proyecto: ninguna regla de negocio vive acá.
"""
from typing import Optional

from pydantic import BaseModel

from fastapi import APIRouter, HTTPException, status

from src.services.auth_service import autenticar_usuario, emitir_token, registrar_usuario
from src.services.exceptions import ConflictError, InvalidCredentialsError, ValidationError

auth_router = APIRouter(prefix="/auth", tags=["auth"])


class RegistroRequest(BaseModel):
    email: str
    password: str
    nombre: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class UsuarioOut(BaseModel):
    id: str
    email: str

    class Config:
        orm_mode = True


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


@auth_router.post("/registro", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def registro_endpoint(payload: RegistroRequest):
    try:
        usuario = registrar_usuario(payload.email, payload.password, payload.nombre)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return UsuarioOut(id=str(usuario.id), email=usuario.email)


@auth_router.post("/login", response_model=TokenOut)
def login_endpoint(payload: LoginRequest):
    try:
        usuario = autenticar_usuario(payload.email, payload.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    token = emitir_token(usuario.id)
    return TokenOut(access_token=token)
