# Solution Overview — Crear tarea sin puntos crea una tarea de 0 puntos

## File Index
- [../spec.md](../spec.md)
- [10-verify.md](10-verify.md)
- [99-progress.md](99-progress.md)

### Task Index

| Task | File | Description | Dependencies |
|---|---|---|---|
| T1 | [01-plan-01-puntos-opcional.md](01-plan-01-puntos-opcional.md) | `Tareas.tsx` envía `undefined` en vez de `0` cuando Puntos está vacío | — |

## Problema y solución
`handleCrear` en `Tareas.tsx` llama `crearTarea(casaId, { ...,
puntos: Number(puntos), ... })` incondicionalmente. `Number("")` es
`0` en JavaScript — un valor perfectamente válido para el esquema
(`puntos: Optional[int] = None` en el backend, con la regla `puntos <
0` como único rechazo). El campo vacío nunca llega como "ausente"
porque ya se convirtió en un número antes de salir del componente. El
fix es puramente de conversión de tipo en el cliente: solo convertir a
número cuando el campo tiene contenido.

## Arquitectura
Sin cambios — ningún endpoint ni regla de negocio del backend cambia
(la regla ya existe y ya es correcta); el fix corrige el dato que el
frontend arma antes de enviarlo.

## API/Data Contracts
- `CrearTareaInput.puntos` (tareasClient.ts): cambia de `number`
  (requerido) a `number | undefined` (opcional) — refleja que
  `JSON.stringify` omite una clave `undefined`, dejando que el body
  llegue sin `puntos` cuando corresponde, igual que ya soporta
  `descripcion`/`responsableId`/`fechaPrevista`/`frecuencia` en la misma
  interfaz.
