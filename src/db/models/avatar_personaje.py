import uuid

from sqlalchemy import Column, Date, String

from src.db.base import Base
from src.db.types import GUID


class AvatarPersonaje(Base):
    """Catálogo de razas de avatar seleccionables (spec `avatares-economia`,
    REQ-002).

    `lottie_url` es texto plano (URL o path del asset Lottie) — nunca un
    enum ni un asset embebido — para que reemplazar la animación de una
    raza no requiera tocar código ni migrar de nuevo (decisión explícita
    del usuario, ver spec.md Sources).

    `nivel_requerido` es uno de los 4 nombres de nivel de
    `ranking_service.NIVELES` ("Novato"/"Activo"/"Comprometido"/"Campeón
    de la casa") — nunca se duplica el umbral numérico acá, solo se
    guarda el nombre, comparado en `avatar_service` contra el orden ya
    establecido por esa lista.

    `disponible_desde`/`disponible_hasta` (`NULL` = sin límite) acotan una
    raza de tiempo limitado a futuro — fuera de ventana, la raza no
    aparece en el catálogo seleccionable para quien todavía no la eligió
    (REQ-002), pero un miembro que ya la tenía seleccionada la conserva.
    """

    __tablename__ = "avatar_personajes"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    especie = Column(String, nullable=False)
    raza = Column(String, nullable=False)
    lottie_url = Column(String, nullable=False)
    nivel_requerido = Column(String, nullable=False)
    rareza = Column(String, nullable=False)
    disponible_desde = Column(Date, nullable=True)
    disponible_hasta = Column(Date, nullable=True)

    # Sin `relationship()` hacia `MiembroAvatarSeleccionado` (T3) a
    # propósito: esta spec usa joins explícitos en las consultas del
    # servicio (mismo criterio ya establecido en `ranking_service`/
    # `logro_service`), no relaciones ORM declarativas — así T2 no
    # depende de que el modelo de T3 ya exista para configurar sus mappers.

    def __repr__(self):  # pragma: no cover - solo para debugging
        return (
            f"<AvatarPersonaje id={self.id} especie={self.especie!r} "
            f"raza={self.raza!r} nivel_requerido={self.nivel_requerido!r}>"
        )
