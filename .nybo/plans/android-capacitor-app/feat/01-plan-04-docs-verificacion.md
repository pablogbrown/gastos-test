# T4 — Documentación + verificación end-to-end

## Scope
- Nuevo `docs/android.md` con la secuencia completa, en orden, para que
  el usuario compile y corra la app en un dispositivo/emulador real:
  1. Prerrequisitos: Android Studio, JDK 17, Android SDK.
  2. Conseguir la IP de LAN del backend (`make up` ya corriendo).
  3. Build de producción con la base URL: `VITE_API_BASE_URL=http://
     <ip-de-lan>:8000 npm run build`.
  4. `npx cap sync android`.
  5. `npx cap open android` (abre Android Studio) → correr en
     emulador/dispositivo, o generar el APK (`Build > Generate Signed
     Bundle/APK`).
  6. Alternativa para iterar rápido sin recompilar: descomentar el
     bloque `server` de `capacitor.config.ts` apuntando a `http://
     <ip-de-lan>:5173` (Vite dev server con `--host`), `npx cap sync
     android` de nuevo, correr — cada cambio de código se refleja sin
     rebuildear el APK.
  7. Troubleshooting: qué hacer si la app no conecta (verificar CORS
     origins, cleartext, que el backend/frontend estén escuchando en
     `0.0.0.0` y no solo `127.0.0.1`, firewall del sistema operativo).
- Actualizar `.nybo/foundation/stack.yaml`'s `dev_runbook` con una
  referencia a `docs/android.md` (un `run_targets` adicional o una nota
  — no duplicar el contenido ahí).

## Dependencies
T1, T2, T3 (documenta el resultado de las tres).

## Done When
- Suite completa (backend + frontend) en verde, incluyendo los tests
  nuevos de T1/T2/T3.
- `npm run build`/`npm run lint` sin errores.
- Smoke: con `VITE_API_BASE_URL` apuntando al backend dockerizado local
  (IP de loopback alcanza para este smoke, no hace falta LAN real) y
  `CORS_ALLOWED_ORIGINS` incluyendo `http://localhost:5173` de prueba,
  un login real desde un build servido en otro puerto (simulando un
  origen distinto) confirma que CORS + base URL configurable funcionan
  juntos end-to-end — sin esto, T1 y T2 solo se probaron por separado.

## Verifiability
Documentación + verificación manual/smoke — no genera un test
automatizado nuevo propio (T1/T2/T3 ya cubren su parte con tests).
