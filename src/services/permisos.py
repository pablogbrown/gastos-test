"""Tabla de permisos por rol (REQ-004).

Vive en la capa de servicio (no en la UI ni en las rutas) para que
cualquier consumidor de la API quede protegido igual sin importar el
cliente — agregar un permiso nuevo no obliga a tocar cada ruta (OCP).
"""
from src.db.models.miembro import RolEnum

# Acciones reconocidas. Las de gastos/tareas/puntos son consumidas por las
# specs dependientes (gastos, tareas-puntos), que reutilizan esta misma
# tabla en vez de definir la suya.
ACCIONES_ADMIN = {
    "modificar_casa",
    "agregar_miembro",
    "eliminar_miembro",
    "crear_tarea",
    "modificar_tarea",
    "gestionar_categorias",
    "consultar_todos_gastos",
    "consultar_ranking",
}

ACCIONES_MIEMBRO = {
    "consultar_casa",
    "registrar_gasto",
    "consultar_balances",
    "realizar_tarea",
    "completar_tarea",
    "consultar_puntos",
    "consultar_ranking",
}

_PERMISOS = {
    RolEnum.ADMIN: ACCIONES_ADMIN | ACCIONES_MIEMBRO,
    RolEnum.MEMBER: ACCIONES_MIEMBRO,
}


def puede(rol, accion: str) -> bool:
    """Indica si `rol` (RolEnum o su valor string) puede realizar `accion`."""
    rol_normalizado = RolEnum(rol) if not isinstance(rol, RolEnum) else rol
    return accion in _PERMISOS.get(rol_normalizado, set())
