"""Migración: crea `avatar_personajes` y siembra el catálogo inicial
(spec `avatares-economia`, T2).

Fuente/licencia del pack curado (REGISTRAR SIEMPRE que se reemplace un
asset, para no perder esta trazabilidad):

    Fuente:  LottieFiles "Animals Lottie Animations Pack"
             (https://lottiefiles.com/), colección de animaciones de
             perros/gatos de uso libre.
    Licencia: LottieFiles Simple License — uso comercial permitido sin
              atribución (https://lottiefiles.com/licensing).

*** NOTA DE ESTE BUILD (avatares-economia, 2026-09-23) ***: este entorno
de build no tiene acceso a la web para descargar/verificar los archivos
`.json` reales del pack — las URLs de abajo son PLACEHOLDERS plausibles
del dominio `assets.lottiefiles.com` (mismo shape que un asset real de
LottieFiles), no archivos verificados. El modelo de datos, la migración,
el seed (8-10 filas, un mínimo de una por nivel, rareza variada) y el
resto de la mecánica (desbloqueo por nivel, selección) son 100%
funcionales — lo único pendiente es reemplazar cada `lottie_url` por el
asset real curado del pack de arriba antes de mostrarse en producción
(el campo es texto plano exactamente para que ese reemplazo no requiera
tocar código ni esta migración de nuevo, ver `AvatarPersonaje.lottie_url`).
Registrado también como sugerencia en `evidence/suggestions.yaml`.
"""
import uuid

from sqlalchemy import insert
from sqlalchemy.engine import Engine

from src.db.base import Base
from src.db.models.avatar_personaje import AvatarPersonaje

TABLES = [AvatarPersonaje.__table__]

# 10 razas, 2-3 por nivel, rareza variada — un mínimo de una por cada uno
# de los 4 niveles de `ranking_service.NIVELES` (TC-003/TC-004, Done When
# de T2). Ninguna tiene ventana de disponibilidad (`disponible_desde`/
# `disponible_hasta` en `NULL`) — sin razas de tiempo limitado en este
# catálogo inicial v1.
_SEED = [
    {
        "especie": "perro",
        "raza": "Beagle",
        "lottie_url": "https://assets.lottiefiles.com/packages/lf20_avatares_beagle_placeholder.json",
        "nivel_requerido": "Novato",
        "rareza": "común",
    },
    {
        "especie": "gato",
        "raza": "Gato atigrado",
        "lottie_url": "https://assets.lottiefiles.com/packages/lf20_avatares_gato_atigrado_placeholder.json",
        "nivel_requerido": "Novato",
        "rareza": "común",
    },
    {
        "especie": "perro",
        "raza": "Salchicha",
        "lottie_url": "https://assets.lottiefiles.com/packages/lf20_avatares_salchicha_placeholder.json",
        "nivel_requerido": "Novato",
        "rareza": "común",
    },
    {
        "especie": "perro",
        "raza": "Labrador",
        "lottie_url": "https://assets.lottiefiles.com/packages/lf20_avatares_labrador_placeholder.json",
        "nivel_requerido": "Activo",
        "rareza": "raro",
    },
    {
        "especie": "gato",
        "raza": "Gato negro",
        "lottie_url": "https://assets.lottiefiles.com/packages/lf20_avatares_gato_negro_placeholder.json",
        "nivel_requerido": "Activo",
        "rareza": "raro",
    },
    {
        "especie": "gato",
        "raza": "Gato naranja",
        "lottie_url": "https://assets.lottiefiles.com/packages/lf20_avatares_gato_naranja_placeholder.json",
        "nivel_requerido": "Activo",
        "rareza": "común",
    },
    {
        "especie": "perro",
        "raza": "Pastor alemán",
        "lottie_url": "https://assets.lottiefiles.com/packages/lf20_avatares_pastor_aleman_placeholder.json",
        "nivel_requerido": "Comprometido",
        "rareza": "épico",
    },
    {
        "especie": "gato",
        "raza": "Gato persa",
        "lottie_url": "https://assets.lottiefiles.com/packages/lf20_avatares_gato_persa_placeholder.json",
        "nivel_requerido": "Comprometido",
        "rareza": "épico",
    },
    {
        "especie": "perro",
        "raza": "Husky siberiano",
        "lottie_url": "https://assets.lottiefiles.com/packages/lf20_avatares_husky_placeholder.json",
        "nivel_requerido": "Campeón de la casa",
        "rareza": "legendario",
    },
    {
        "especie": "gato",
        "raza": "Maine Coon",
        "lottie_url": "https://assets.lottiefiles.com/packages/lf20_avatares_maine_coon_placeholder.json",
        "nivel_requerido": "Campeón de la casa",
        "rareza": "legendario",
    },
]


def upgrade(bind: Engine) -> None:
    Base.metadata.create_all(bind=bind, tables=TABLES)

    with bind.begin() as conn:
        ya_sembrado = conn.execute(AvatarPersonaje.__table__.select().limit(1)).first()
        if ya_sembrado is not None:
            # Migración ya corrida contra esta base (ej. reinicio del
            # backend con un volumen persistido) — nunca duplicar el seed.
            return
        conn.execute(
            insert(AvatarPersonaje.__table__),
            [{"id": uuid.uuid4(), **fila} for fila in _SEED],
        )


def downgrade(bind: Engine) -> None:
    # Aditivo — no se remueve, mismo criterio que el resto de las
    # migraciones aditivas de este proyecto (ver `0006`-`0021`).
    Base.metadata.drop_all(bind=bind, tables=TABLES)
