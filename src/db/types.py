"""Tipos de columna portables entre PostgreSQL y SQLite (usado en tests)."""
import uuid

from sqlalchemy.types import CHAR, TypeDecorator


class GUID(TypeDecorator):
    """Columna UUID almacenada como CHAR(36), portable entre backends.

    PostgreSQL soporta un tipo UUID nativo, pero SQLite (usado en los tests
    unitarios/integración de esta spec) no. Se normaliza a string para que
    el mismo modelo funcione contra ambos motores sin cambiar el esquema.
    """

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(uuid.UUID(str(value)))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return uuid.UUID(str(value))
