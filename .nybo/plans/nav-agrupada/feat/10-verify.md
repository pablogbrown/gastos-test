# Verify — Menú superior agrupado por categoría

## T1 — Estructura de grupos + menú desktop desplegable

### Test Scenarios
- Desktop muestra 4 elementos de primer nivel (TC-001).
- Clic en "Casa" despliega Miembros/Ranking/Actividad, elegir uno navega y cierra el menú (TC-002).
- Clic en "Gastos" despliega Gastos/Balance/Tarjetas/Suscripciones (TC-003).
- Con `pantalla="tarjetas"`, el grupo "Gastos" se muestra activo (TC-004).
- Mobile sigue mostrando las 9 pantallas sin agrupar (TC-005, control).
- El TC-002 original de `ui-modernization` queda actualizado y en verde.

### Gate Criteria
- `[AUTO]` TC-001 a TC-005 en verde.
- `[AUTO]` `npm run build`/`npm run lint` sin errores.

## End-to-End Verification
1. `npm run test -- --run` en verde.
2. `npm run build` sin errores.
3. Smoke manual contra docker-compose: en desktop, navegar a Tarjetas
   vía "Gastos" → menú; confirmar que "Gastos" queda resaltado; achicar
   la ventana a mobile y confirmar que la barra inferior sigue mostrando
   las 9 pantallas sueltas, sin agrupar.

## Failure Triage

| If TC-XXX fails | Check first | Root cause pattern |
|---|---|---|
| TC-004 | ¿La comparación de "grupo activo" incluye TODAS las pantallas del grupo, o solo la primera? | Comparar `pantalla === grupo.pantallas[0]` en vez de `grupo.pantallas.includes(pantalla)` |
| TC-005 | ¿`BottomNavigation` sigue iterando `SECCIONES` (no `GRUPOS_DESKTOP`)? | Reusar por error la estructura agrupada también en mobile |
| TC-002 original (`ui-modernization`) | ¿Se actualizó la aserción de `tablist`/9 `tab`, o se dejó intacta esperando el comportamiento viejo? | Test desactualizado en vez de migrado al nuevo contrato desktop |
