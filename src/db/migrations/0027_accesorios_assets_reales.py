"""Fix `avatar-assets-fallback` (continuación): reemplaza las URLs
placeholder de `asset_overlay_url` sembradas por `0024_accesorio_catalogo`
por íconos SVG reales, servidos localmente desde `public/accesorios/`
(Vite los copia tal cual a `dist/` — accesibles en `/accesorios/<nombre>.svg`
tanto en la build web como en la app Android empaquetada, sin depender de
ninguna red externa que se pueda romper).

No se necesitaba esto para los accesorios (a diferencia de las 10 razas
de avatar, que sí requieren una animación Lottie real) — un ícono estático
simple ya resuelve el problema visual por completo, así que se resolvió
acá mismo en vez de depender de que el usuario consiga assets externos.

Migración de datos (UPDATE, no ALTER) — idempotente: cada `UPDATE ...
WHERE nombre = ...` fija el mismo valor si se corre más de una vez, mismo
criterio que el resto de las migraciones de este proyecto.
"""
from sqlalchemy import text
from sqlalchemy.engine import Engine

_REEMPLAZOS = {
    "Gorro de lana": "/accesorios/gorro-de-lana.svg",
    "Orejas de gato": "/accesorios/orejas-de-gato.svg",
    "Gorra deportiva": "/accesorios/gorra-deportiva.svg",
    "Corona de fiesta": "/accesorios/corona-de-fiesta.svg",
    "Casco de explorador": "/accesorios/casco-de-explorador.svg",
    "Diadema real": "/accesorios/diadema-real.svg",
    "Pañuelo básico": "/accesorios/panuelo-basico.svg",
    "Collar con cascabel": "/accesorios/collar-con-cascabel.svg",
    "Pajarita elegante": "/accesorios/pajarita-elegante.svg",
    "Bufanda de invierno": "/accesorios/bufanda-de-invierno.svg",
    "Collar de medallas": "/accesorios/collar-de-medallas.svg",
    "Collar de gemas legendario": "/accesorios/collar-de-gemas-legendario.svg",
    "Sweater básico": "/accesorios/sweater-basico.svg",
    "Capa de superhéroe": "/accesorios/capa-de-superheroe.svg",
    "Chaleco de explorador": "/accesorios/chaleco-de-explorador.svg",
    "Armadura de dragón": "/accesorios/armadura-de-dragon.svg",
    "Traje real legendario": "/accesorios/traje-real-legendario.svg",
    "Gorro navideño (temporada 2025)": "/accesorios/gorro-navideno.svg",
}


def upgrade(bind: Engine) -> None:
    with bind.begin() as conn:
        for nombre, url in _REEMPLAZOS.items():
            conn.execute(
                text("UPDATE accesorios_avatar SET asset_overlay_url = :url WHERE nombre = :nombre"),
                {"url": url, "nombre": nombre},
            )


def downgrade(bind: Engine) -> None:
    # Migración de datos, no de esquema — no hay nada estructural que
    # revertir (mismo criterio que cualquier UPDATE de datos en este
    # proyecto); las URLs viejas eran placeholders rotos, no un estado
    # válido al que volver.
    pass
