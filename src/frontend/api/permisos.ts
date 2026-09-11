// Espejo de UI de la tabla de permisos de `src/services/permisos.py` (T2).
// Solo se usa para ocultar acciones no permitidas (defensa en profundidad).
// La autorización real vive en la API — ver Design Rationale de T4.
import type { Rol } from "./casasClient";

export function puedeGestionarMiembros(rol: Rol): boolean {
  return rol === "admin";
}
