"""Excepciones de dominio compartidas por los servicios de casas/miembros.

Se definen como clases propias (en vez de reusar `PermissionError` del
lenguaje) para no chocar con la excepción built-in de Python, que tiene
semántica de sistema operativo (OSError), y para que las rutas de la API
(T3) puedan mapearlas a códigos HTTP sin ambigüedad.
"""


class ValidationError(Exception):
    """Datos de entrada inválidos (p. ej. nombre vacío, identificación duplicada)."""


class PermissionDeniedError(Exception):
    """El actor no tiene el rol/permiso requerido para la acción."""


class NotFoundError(Exception):
    """La casa o el miembro referenciado no existe."""


class ConflictError(Exception):
    """La operación entra en conflicto con el estado actual del recurso
    (p. ej. completar una tarea que ya está Completada — TC-006). Se
    distingue de `ValidationError` porque las rutas de la API (T3) la
    mapean a 409 en vez de 400."""


class InvalidCredentialsError(Exception):
    """Credenciales de login inválidas, o un JWT ausente/inválido/expirado
    (spec `usuarios-auth`).

    Un único mensaje genérico cubre tanto "el email no existe" como "la
    contraseña no matchea" (REQ-002/TC-004): revelar cuál de las dos causas
    ocurrió permitiría enumerar emails registrados. Las rutas de la API
    (T3) la mapean siempre a 401.
    """
