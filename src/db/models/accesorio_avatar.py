import uuid

from sqlalchemy import Column, Date, Integer, String

from src.db.base import Base
from src.db.types import GUID


class AccesorioAvatar(Base):
    """Catálogo de accesorios (ropa/objetos) comprables con créditos
    (spec `tienda-accesorios`, REQ-001).

    `asset_overlay_url` es texto plano (URL/path del ícono/badge del
    accesorio) — nunca integrado a la animación Lottie del cuerpo
    (decisión ya tomada, ver spec.md REQ-001) — mismo criterio ya
    establecido para `AvatarPersonaje.lottie_url` (spec
    `avatares-economia`): reemplazar el asset no requiere tocar código
    ni migrar de nuevo.

    `slot` es uno de `"cabeza"`/`"cuello"`/`"cuerpo"` — a lo sumo un
    accesorio equipado por slot y por miembro (REQ-003,
    `MiembroAccesorioEquipado`, T3).

    `rareza` reusa los mismos 4 valores ya establecidos por
    `AvatarPersonaje.rareza` (`avatares-economia`) — nunca un catálogo de
    valores separado, para que ambos catálogos se sientan consistentes
    (Design Rationale de T1).

    `especie_compatible` es `"perro"`/`"gato"`/`"ambos"` — filtrado contra
    la especie del avatar actualmente seleccionado del miembro
    (`avatar_service.obtener_avatar_seleccionado`, nunca reimplementado
    acá, ver spec.md Constraints).

    `disponible_desde`/`disponible_hasta` (`NULL` = sin límite) acotan un
    accesorio de tiempo limitado (REQ-004) — mismo criterio ya
    establecido por `AvatarPersonaje`.
    """

    __tablename__ = "accesorios_avatar"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    nombre = Column(String, nullable=False)
    slot = Column(String, nullable=False)
    rareza = Column(String, nullable=False)
    precio_creditos = Column(Integer, nullable=False)
    especie_compatible = Column(String, nullable=False)
    asset_overlay_url = Column(String, nullable=False)
    disponible_desde = Column(Date, nullable=True)
    disponible_hasta = Column(Date, nullable=True)

    # Sin `relationship()` hacia `MiembroAccesorioComprado`/
    # `MiembroAccesorioEquipado` (T2/T3) a propósito: mismo criterio ya
    # establecido por `AvatarPersonaje` — joins explícitos en el service
    # layer, no relaciones ORM declarativas, así T1 no depende de que los
    # modelos de T2/T3 ya existan para configurar sus mappers.

    def __repr__(self):  # pragma: no cover - solo para debugging
        return (
            f"<AccesorioAvatar id={self.id} nombre={self.nombre!r} "
            f"slot={self.slot!r} especie_compatible={self.especie_compatible!r}>"
        )
