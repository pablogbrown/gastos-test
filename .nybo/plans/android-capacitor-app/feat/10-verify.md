# Verify — android-capacitor-app

## T1 — Base URL de API configurable

### Test Scenarios
- Sin `VITE_API_BASE_URL`: rutas idénticas a hoy (TC-001).
- Con `VITE_API_BASE_URL` seteada: rutas con el prefijo absoluto
  (TC-002).

### Gate Criteria
- `[AUTO]` TC-001/TC-002 en verde.
- `[AUTO]` Suite frontend completa sin regresión (ningún cliente de API
  cambia).

## T2 — CORS en el backend

### Test Scenarios
- Origen permitido recibe el header correcto (TC-003).
- Origen no permitido no lo recibe; request sin `Origin` no cambia
  (TC-004).

### Gate Criteria
- `[AUTO]` TC-003/TC-004 en verde.
- `[AUTO]` Suite backend completa (363+ tests) sin regresión.

## T3 — Proyecto Android + Capacitor

### Gate Criteria
- `[AUTO]` TC-005/TC-006 en verde (chequeos estructurales, sin SDK).
- `[AUTO]` `.gitignore` cubre los artifacts de build de Android — `git
  status` limpio después de `cap add`/`cap sync`.

## T4 — Docs + verificación

### Gate Criteria
- `[AUTO]` Suite completa (backend + frontend) en verde.
- `[AUTO]` `npm run build`/`npm run lint` sin errores.
- `[MANUAL]` Smoke de CORS + base URL combinados (ver Done When de T4).

## End-to-End Verification
1. `docker compose exec backend python -m pytest tests/` y `npm run
   test -- --run` en verde.
2. `npm run build`/`npm run lint` sin errores.
3. `npx cap sync android` corre sin errores.
4. Smoke combinado de T4 (CORS + base URL sirviendo desde un origen
   distinto).
5. **Fuera de este entorno, a cargo del usuario**: abrir `android/` en
   Android Studio (`npx cap open android`), correr en un emulador o
   dispositivo real, confirmar que la app carga y el login/registro
   funcionan contra el backend dockerizado por IP de LAN.

## Failure Triage

| If TC-XXX falla | Revisar primero | Patrón de causa raíz |
|---|---|---|
| TC-002 | ¿`fetchAutenticado` chequea `input.startsWith("/")` antes de anteponer, o rompe una URL ya absoluta (ej. una pasada por un test)? | Doble-prefijo si no se chequea que `input` sea relativo |
| TC-003 | ¿`CORSMiddleware` está registrado ANTES de los routers, o el orden de `add_middleware` importa acá? | FastAPI aplica middlewares en orden de registro — confirmar que corre sobre todas las rutas |
| TC-005 | ¿`npm run build` corrió antes de `npx cap add android`? | `cap add` necesita que `webDir` (`dist/`) ya exista |
| Smoke de Android Studio (manual) | ¿La app no conecta pese a CORS+base URL correctos? | Firewall del SO bloqueando el puerto, o backend/frontend escuchando solo en `127.0.0.1` en vez de `0.0.0.0` |
