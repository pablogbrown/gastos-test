# Verify — Membresía duplicada crashea la resolución de actor

## T1 — Validar membresía única

### Test Scenarios
- Happy path: agregar un email nunca antes agregado a la casa → 201, como siempre.
- Edge: agregar el mismo email dos veces a casas distintas → ambas 201 (TC-002).
- Error: agregar un email ya activo en la misma casa → 400 "El usuario ya es miembro activo de esta casa." (TC-001).

### Gate Criteria
- `[AUTO]` TC-001, TC-002 en verde.
- `[AUTO]` Suite completa de `pytest tests/` sigue en verde (sin regresión en casas-miembros/gastos/tareas/dashboard existentes).

## T2 — Endurecer resolver_actor_en_casa

### Test Scenarios
- Happy path (sin duplicados): cualquier request autenticado normal — comportamiento idéntico al actual, cero regresión.
- Edge: dos filas activas para el mismo `(casa_id, usuario_id)`, sembradas directo — el request resuelve sin 500 (TC-003).
- Repetibilidad: el mismo escenario de duplicados, 5 requests seguidos, siempre el mismo `Miembro.id` resuelto (TC-004).

### Gate Criteria
- `[AUTO]` TC-003, TC-004 en verde.
- `[AUTO]` Ningún test preexistente que dependa de `resolver_actor_en_casa` cambia de resultado.
- `[HUMAN]` Confirmar manualmente contra el entorno dockerizado: repetir el escenario original (Pablo intentando desactivar al Administrador) no debe volver a producir un 200 — debe ser 403, de forma estable en varios intentos.

## End-to-End Verification
1. `pytest tests/` completo en verde.
2. Smoke manual (curl o Chrome) contra el docker-compose local: registrar 2 usuarios, agregar ambos a la misma casa por email dos veces → la segunda falla con 400 claro.
3. Sembrar duplicado directo en Postgres (bypaseando la API) → cualquier request de ese usuario a esa casa responde 200/403 según corresponda, nunca 500.
4. Repetir el intento original del incidente (member intenta desactivar admin) 5 veces seguidas → siempre 403.

## Failure Triage

| If TC-XXX fails | Check first | Root cause pattern |
|---|---|---|
| TC-001 | La query de validación en `agregar_miembro` — ¿se ejecuta antes o después del insert? | Validación agregada en el orden equivocado, o comparando `identificacion` en vez de `usuario_id` |
| TC-003 | El `.order_by(...).first()` de `resolver_actor_en_casa` — ¿sigue habiendo un `.one()`/`.one_or_none()` en otra rama? | Cambio aplicado solo a una de las dos llamadas de esa query en el archivo |
| TC-004 | ¿El orden usado es realmente determinístico (columna con valores únicos y estables)? | Ordenar por una columna que no garantiza unicidad (ej. `nombre`) en vez de `id` |
