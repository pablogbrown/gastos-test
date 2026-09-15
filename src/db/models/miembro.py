import enum
import uuid

from sqlalchemy import Boolean, Column, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship

from src.db.base import Base
from src.db.types import GUID


class RolEnum(str, enum.Enum):
    """Roles reconocidos dentro de una casa (REQ-004)."""

    ADMIN = "admin"
    MEMBER = "member"


class Miembro(Base):
    """Una persona perteneciente a una Casa, con un rol y estado activo.

    `id` es la identidad *dentro de esa casa*: es el valor que las specs
    dependientes (gastos, tareas-puntos, dashboard-actividad) usan como
    `usuario_id`/`actor` al llamar a `requiere_membresia_activa` y a los
    demás guards de esos servicios — ninguno de ellos cambia con la spec
    `usuarios-auth`.

    `usuario_id` (spec `usuarios-auth`) es la FK a la identidad global
    (`Usuario`, email+contraseña). Una misma persona (mismo `Usuario`)
    puede pertenecer a varias casas (REQ-004 de `usuarios-auth`) con un
    `Miembro.id` distinto — y por lo tanto sus propios balances/puntos
    independientes — en cada una, todas compartiendo el mismo
    `usuario_id`. Nullable porque filas sembradas antes de esta spec no
    tienen un Usuario asociado; toda alta nueva vía `crear_casa`/
    `agregar_miembro` la completa siempre.

    `email_invitacion` (spec `invitar-miembro-pendiente`) guarda,
    normalizado (recortado, minúsculas), el email con el que un
    Administrador invitó a esta persona cuando todavía no tenía un
    `Usuario` registrado — mientras tanto `usuario_id` queda `NULL` y la
    fila está "pendiente". `registrar_usuario` busca por esta columna
    para vincular `usuario_id` automáticamente en cuanto esa persona se
    registra. Se conserva después de vincularse (nunca se borra), como
    registro de auditoría de quién invitó a quién.
    """

    __tablename__ = "miembros"
    __table_args__ = (
        UniqueConstraint("casa_id", "identificacion", name="uq_miembro_casa_identificacion"),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    casa_id = Column(GUID(), ForeignKey("casas.id"), nullable=False)
    usuario_id = Column(GUID(), ForeignKey("usuarios.id"), nullable=True)
    email_invitacion = Column(String, nullable=True)
    nombre = Column(String, nullable=False)
    identificacion = Column(String, nullable=False)
    rol = Column(Enum(RolEnum), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)

    casa = relationship("Casa", back_populates="miembros")
    usuario = relationship("Usuario", back_populates="miembros")

    def __repr__(self):  # pragma: no cover - solo para debugging
        return f"<Miembro id={self.id} nombre={self.nombre!r} rol={self.rol}>"
