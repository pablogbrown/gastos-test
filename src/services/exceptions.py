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
