# Spec: android-capacitor-app

## Feature
android-capacitor-app

### What
Empaquetar el frontend ya existente (React + Vite) como una app Android
instalable vía Capacitor, sin tocar el comportamiento de la versión web
actual. Incluye la configuración necesaria para que la app compilada
pueda hablar con el backend (base URL configurable, CORS) y los pasos
para compilarla/probarla en un emulador o dispositivo real.

### Why
La app está pensada desde el diseño para uso mobile (nav responsive,
bottom bar). El usuario quiere probarla como una app Android instalable
de verdad, no solo el sitio responsive en el navegador del teléfono
(ya posible hoy sin cambios).

## Solution
Se agrega Capacitor (`@capacitor/core`, `@capacitor/android`,
`@capacitor/cli`) sobre el build de producción ya existente
(`npm run build` → `dist/`), sin crear un segundo frontend ni duplicar
pantallas. Dos cambios de código, ambos aditivos y con default idéntico
al comportamiento actual:

1. **Base URL de API configurable** (`VITE_API_BASE_URL`, default
   `""` = comportamiento actual sin cambios): la app empaquetada no
   tiene el proxy de Vite que hoy resuelve `/casas`/`/auth` contra el
   backend, así que necesita una URL absoluta.
2. **CORS en el backend**: la app empaquetada corre en un origen propio
   (`capacitor://localhost` en Android), distinto del origen del
   backend — sin CORS, el navegador embebido bloquea la respuesta.

El proyecto Android (`android/`) se genera con `npx cap add android` y
se commitea (convención estándar de Capacitor), con cleartext HTTP
habilitado para poder hablar con el backend dockerizado local (HTTP
plano, sin certificado) durante desarrollo/pruebas.

## Requirements

- REQ-001: La URL base de la API es configurable vía una variable de
  entorno de build (`VITE_API_BASE_URL`); sin configurarla, el
  comportamiento es exactamente el actual (rutas relativas, sin cambio
  para el despliegue web).
- REQ-002: El backend acepta requests cross-origin desde los orígenes
  de la app Capacitor (`CORSMiddleware`), configurable vía variable de
  entorno, sin afectar el flujo same-origin de la web existente.
- REQ-003: Existe un proyecto Android nativo (`android/`, generado por
  Capacitor) que carga el build de producción del frontend por
  default, con un modo opcional de live-reload contra el servidor de
  desarrollo de Vite documentado para iterar sin recompilar.
- REQ-004: El tráfico HTTP plano (sin TLS) está permitido en Android
  para poder hablar con el backend local/LAN durante pruebas.
- REQ-005: Documentación paso a paso para compilar y correr la app en
  un emulador o dispositivo Android real vía Android Studio — el único
  paso que no se puede automatizar en este entorno (requiere Android
  SDK/Gradle/Android Studio instalados).

## Test Cases

- TC-001 (REQ-001): sin `VITE_API_BASE_URL`, `fetchAutenticado` y los
  dos `fetch` directos de `authClient.ts` arman exactamente las mismas
  rutas relativas que hoy (regresión: la web no cambia).
- TC-002 (REQ-001): con `VITE_API_BASE_URL` seteada, esas mismas
  llamadas anteponen la URL absoluta a cada ruta relativa.
- TC-003 (REQ-002): una request con un origen permitido (ej.
  `capacitor://localhost`) recibe el header `Access-Control-Allow-
  Origin` correcto.
- TC-004 (REQ-002): una request sin header `Origin` (el flujo web
  same-origin de siempre) responde exactamente igual que antes — sin
  regresión en la suite existente.
- TC-005 (REQ-003): `npx cap sync android` corre sin errores y el
  proyecto generado referencia el `appId`/`appName` configurados y
  `webDir: "dist"`.
- TC-006 (REQ-004): la configuración de red de Android (network
  security config / manifest) permite tráfico cleartext.

## Dependencies
- Nuevas dependencias: `@capacitor/core`, `@capacitor/android`
  (`dependencies`), `@capacitor/cli` (`devDependencies`) — aprobadas
  explícitamente por el usuario al pedir esta implementación.
- Requiere Android Studio + JDK 17 + Android SDK instalados en la
  máquina donde se compile/corra el APK (fuera del alcance de lo que
  este entorno puede instalar o verificar).

## Out of Scope
- Publicación en Google Play Store (firma de release, ficha de store).
- Una versión iOS (Capacitor lo soportaría, pero no se pidió).
- Notificaciones push, biometría, u otras capacidades nativas más allá
  de mostrar el WebView.
- Un backend desplegado públicamente — el target de esta spec es el
  backend dockerizado local, alcanzable por IP de LAN, igual que ya lo
  es hoy para probar la web responsive en el navegador del teléfono.
