"""Fix `avatar-assets-fallback` (continuación): reemplaza 4 de las 10
razas placeholder de `avatar_personajes` (0022_avatar_catalogo) por
animaciones Lottie reales provistas por el usuario — servidas localmente
desde `public/avatares/` (mismo criterio que `public/accesorios/`, sin
depender de ninguna red externa).

Se usa el nombre REAL de cada animación como `raza` (pedido explícito del
usuario) en vez de mantener el nombre de raza inventado que tenía el
placeholder — ya no tiene sentido decir "Beagle" cuando la animación real
que se muestra ahí se llama "Happy Dog". Las 6 razas restantes quedan
exactamente como estaban (siguen siendo placeholders) — el frontend
(`MiAvatar.tsx`) las trata como "Próximamente" detectando que su
`lottie_url` todavía contiene `_placeholder.json`, sin necesidad de un
flag nuevo en el esquema.

"Cat_in_Box" queda como premium (pedido explícito del usuario) — ya
ocupaba el rareza tope ("legendario") en el placeholder que reemplaza
(Maine Coon, Campeón de la casa), así que no hace falta tocar
`rareza`/`nivel_requerido`, solo `raza`/`lottie_url`.

Nota de assets: "Norm The Dog" referencia una imagen externa
(`images/img_0.png`) que el usuario no proveyó junto al JSON — la
animación funciona igual (el resto de sus capas son vectoriales), pero
esa capa puntual no va a tener su imagen hasta que se agregue ese
archivo. Ver `evidence`/aviso al usuario, no bloqueante.

Migración de datos (UPDATE, no ALTER) — idempotente, mismo criterio que
`0027_accesorios_assets_reales`.
"""
from sqlalchemy import text
from sqlalchemy.engine import Engine

_REEMPLAZOS = {
    "Beagle": {"raza": "Happy Dog", "lottie_url": "/avatares/happy-dog.json"},
    "Labrador": {"raza": "Norm The Dog", "lottie_url": "/avatares/norm-the-dog.json"},
    "Pastor alemán": {
        "raza": "Boxing with Bone - Angry Puppy",
        "lottie_url": "/avatares/boxing-with-bone-angry-puppy.json",
    },
    "Maine Coon": {"raza": "Cat_in_Box", "lottie_url": "/avatares/cat-in-box.json"},
}


def upgrade(bind: Engine) -> None:
    with bind.begin() as conn:
        for raza_vieja, campos in _REEMPLAZOS.items():
            conn.execute(
                text(
                    "UPDATE avatar_personajes SET raza = :raza, lottie_url = :lottie_url "
                    "WHERE raza = :raza_vieja"
                ),
                {**campos, "raza_vieja": raza_vieja},
            )


def downgrade(bind: Engine) -> None:
    # Migración de datos, no de esquema — no hay nada estructural que
    # revertir (mismo criterio que `0027`).
    pass
