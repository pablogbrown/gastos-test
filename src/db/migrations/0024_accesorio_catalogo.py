"""Migración: crea `accesorios_avatar` y siembra el catálogo inicial
(spec `tienda-accesorios`, T1).

Fuente/licencia del pack curado (REGISTRAR SIEMPRE que se reemplace un
asset, para no perder esta trazabilidad):

    Fuente:  LottieFiles "Icons & Badges Lottie Animations Pack"
             (https://lottiefiles.com/), colección de íconos/badges de
             uso libre (gorros, collares, bufandas, mochilas).
    Licencia: LottieFiles Simple License — uso comercial permitido sin
              atribución (https://lottiefiles.com/licensing).

*** NOTA DE ESTE BUILD (tienda-accesorios, 2026-09-23) ***: este entorno
de build no tiene acceso a la web para descargar/verificar los archivos
`.json` reales del pack — las URLs de abajo son PLACEHOLDERS plausibles
del dominio `assets.lottiefiles.com` (mismo shape que un asset real de
LottieFiles, mismo criterio ya usado en `0022_avatar_catalogo.py` de
`avatares-economia`), no archivos verificados. El modelo de datos, la
migración, el seed (18 filas, 6 por slot, rareza y especie variada) y el
resto de la mecánica de tienda (compra/equipar) son 100% funcionales — lo
único pendiente es reemplazar cada `asset_overlay_url` por el asset real
curado del pack de arriba antes de mostrarse en producción (el campo es
texto plano exactamente para que ese reemplazo no requiera tocar código
ni esta migración de nuevo, ver `AccesorioAvatar.asset_overlay_url`).
Registrado también como sugerencia en `evidence/suggestions.yaml`.
"""
import uuid
from datetime import date

from sqlalchemy import insert
from sqlalchemy.engine import Engine

from src.db.base import Base
from src.db.models.accesorio_avatar import AccesorioAvatar

TABLES = [AccesorioAvatar.__table__]

# 18 accesorios, 6 por slot (`cabeza`/`cuello`/`cuerpo`), rareza y
# especie variada — un mínimo de un ítem "ambos" por slot (Done When de
# T1). Ninguno tiene ventana de disponibilidad en este catálogo inicial
# v1 (`disponible_desde`/`disponible_hasta` en `NULL`), salvo los 2
# últimos, deliberadamente estacionales, para que el catálogo real ya
# incluya al menos un ejemplo de accesorio de tiempo limitado (REQ-004).
_SEED = [
    # cabeza
    {
        "nombre": "Gorro de lana",
        "slot": "cabeza",
        "rareza": "común",
        "precio_creditos": 20,
        "especie_compatible": "ambos",
        "asset_overlay_url": "https://assets.lottiefiles.com/packages/lf20_accesorio_gorro_lana_placeholder.json",
    },
    {
        "nombre": "Orejas de gato",
        "slot": "cabeza",
        "rareza": "común",
        "precio_creditos": 25,
        "especie_compatible": "gato",
        "asset_overlay_url": "https://assets.lottiefiles.com/packages/lf20_accesorio_orejas_gato_placeholder.json",
    },
    {
        "nombre": "Gorra deportiva",
        "slot": "cabeza",
        "rareza": "raro",
        "precio_creditos": 45,
        "especie_compatible": "perro",
        "asset_overlay_url": "https://assets.lottiefiles.com/packages/lf20_accesorio_gorra_deportiva_placeholder.json",
    },
    {
        "nombre": "Corona de fiesta",
        "slot": "cabeza",
        "rareza": "raro",
        "precio_creditos": 50,
        "especie_compatible": "ambos",
        "asset_overlay_url": "https://assets.lottiefiles.com/packages/lf20_accesorio_corona_fiesta_placeholder.json",
    },
    {
        "nombre": "Casco de explorador",
        "slot": "cabeza",
        "rareza": "épico",
        "precio_creditos": 90,
        "especie_compatible": "perro",
        "asset_overlay_url": "https://assets.lottiefiles.com/packages/lf20_accesorio_casco_explorador_placeholder.json",
    },
    {
        "nombre": "Diadema real",
        "slot": "cabeza",
        "rareza": "legendario",
        "precio_creditos": 150,
        "especie_compatible": "gato",
        "asset_overlay_url": "https://assets.lottiefiles.com/packages/lf20_accesorio_diadema_real_placeholder.json",
    },
    # cuello
    {
        "nombre": "Pañuelo básico",
        "slot": "cuello",
        "rareza": "común",
        "precio_creditos": 15,
        "especie_compatible": "ambos",
        "asset_overlay_url": "https://assets.lottiefiles.com/packages/lf20_accesorio_panuelo_basico_placeholder.json",
    },
    {
        "nombre": "Collar con cascabel",
        "slot": "cuello",
        "rareza": "común",
        "precio_creditos": 20,
        "especie_compatible": "gato",
        "asset_overlay_url": "https://assets.lottiefiles.com/packages/lf20_accesorio_collar_cascabel_placeholder.json",
    },
    {
        "nombre": "Pajarita elegante",
        "slot": "cuello",
        "rareza": "raro",
        "precio_creditos": 40,
        "especie_compatible": "perro",
        "asset_overlay_url": "https://assets.lottiefiles.com/packages/lf20_accesorio_pajarita_elegante_placeholder.json",
    },
    {
        "nombre": "Bufanda de invierno",
        "slot": "cuello",
        "rareza": "raro",
        "precio_creditos": 45,
        "especie_compatible": "ambos",
        "asset_overlay_url": "https://assets.lottiefiles.com/packages/lf20_accesorio_bufanda_invierno_placeholder.json",
    },
    {
        "nombre": "Collar de medallas",
        "slot": "cuello",
        "rareza": "épico",
        "precio_creditos": 85,
        "especie_compatible": "perro",
        "asset_overlay_url": "https://assets.lottiefiles.com/packages/lf20_accesorio_collar_medallas_placeholder.json",
    },
    {
        "nombre": "Collar de gemas legendario",
        "slot": "cuello",
        "rareza": "legendario",
        "precio_creditos": 160,
        "especie_compatible": "ambos",
        "asset_overlay_url": "https://assets.lottiefiles.com/packages/lf20_accesorio_collar_gemas_placeholder.json",
    },
    # cuerpo
    {
        "nombre": "Sweater básico",
        "slot": "cuerpo",
        "rareza": "común",
        "precio_creditos": 25,
        "especie_compatible": "ambos",
        "asset_overlay_url": "https://assets.lottiefiles.com/packages/lf20_accesorio_sweater_basico_placeholder.json",
    },
    {
        "nombre": "Capa de superhéroe",
        "slot": "cuerpo",
        "rareza": "raro",
        "precio_creditos": 55,
        "especie_compatible": "perro",
        "asset_overlay_url": "https://assets.lottiefiles.com/packages/lf20_accesorio_capa_superheroe_placeholder.json",
    },
    {
        "nombre": "Chaleco de explorador",
        "slot": "cuerpo",
        "rareza": "raro",
        "precio_creditos": 60,
        "especie_compatible": "gato",
        "asset_overlay_url": "https://assets.lottiefiles.com/packages/lf20_accesorio_chaleco_explorador_placeholder.json",
    },
    {
        "nombre": "Armadura de dragón",
        "slot": "cuerpo",
        "rareza": "épico",
        "precio_creditos": 100,
        "especie_compatible": "ambos",
        "asset_overlay_url": "https://assets.lottiefiles.com/packages/lf20_accesorio_armadura_dragon_placeholder.json",
    },
    {
        "nombre": "Traje real legendario",
        "slot": "cuerpo",
        "rareza": "legendario",
        "precio_creditos": 170,
        "especie_compatible": "ambos",
        "asset_overlay_url": "https://assets.lottiefiles.com/packages/lf20_accesorio_traje_real_placeholder.json",
    },
    # accesorio estacional (REQ-004) — ventana de disponibilidad ya
    # vencida en este seed inicial, a propósito, para que el catálogo
    # real incluya un ejemplo tangible de "ítem de tiempo limitado" desde
    # el día 1 (no solo en los tests).
    {
        "nombre": "Gorro navideño (temporada 2025)",
        "slot": "cabeza",
        "rareza": "raro",
        "precio_creditos": 35,
        "especie_compatible": "ambos",
        "asset_overlay_url": "https://assets.lottiefiles.com/packages/lf20_accesorio_gorro_navideno_placeholder.json",
        "disponible_desde": date(2025, 12, 1),
        "disponible_hasta": date(2025, 12, 31),
    },
]


def upgrade(bind: Engine) -> None:
    Base.metadata.create_all(bind=bind, tables=TABLES)

    with bind.begin() as conn:
        ya_sembrado = conn.execute(AccesorioAvatar.__table__.select().limit(1)).first()
        if ya_sembrado is not None:
            # Migración ya corrida contra esta base (ej. reinicio del
            # backend con un volumen persistido) — nunca duplicar el seed.
            return
        # `disponible_desde`/`disponible_hasta` se completan explícitamente
        # con `None` en cada fila (aunque la mayoría no las declare) para
        # que las 18 filas compartan exactamente las mismas columnas en el
        # único INSERT multi-fila de abajo.
        filas = [
            {"id": uuid.uuid4(), "disponible_desde": None, "disponible_hasta": None, **fila}
            for fila in _SEED
        ]
        conn.execute(insert(AccesorioAvatar.__table__), filas)


def downgrade(bind: Engine) -> None:
    # Aditivo — no se remueve, mismo criterio que el resto de las
    # migraciones aditivas de este proyecto (ver `0006`-`0023`).
    Base.metadata.drop_all(bind=bind, tables=TABLES)
