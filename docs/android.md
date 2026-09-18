# App Android (Capacitor)

Empaqueta el frontend web existente (`dist/`) como una app Android
instalable, vía [Capacitor](https://capacitorjs.com/). No es un segundo
frontend: el mismo build de producción de siempre corre dentro de un
WebView nativo. Ver `.nybo/plans/android-capacitor-app/spec.md` para el
detalle completo de la feature.

## Prerrequisitos

- **Android Studio** (incluye el Android SDK y un emulador).
- **JDK 17**.
- **Android SDK** (instalado vía Android Studio → SDK Manager) — este
  repo/entorno de desarrollo NO trae el SDK instalado; compilar y correr
  el APK es, por ahora, un paso manual fuera de lo que la automatización
  de esta spec puede hacer.

## 1. Conseguir la IP de LAN del backend

Con el stack dockerizado local corriendo (`make up`), el backend escucha
en `0.0.0.0:8000` dentro del contenedor, publicado en el host en
`localhost:8000`. Un emulador/dispositivo Android real necesita la IP de
LAN de la máquina que corre Docker (no `localhost`/`127.0.0.1`, que
dentro del dispositivo apuntaría a sí mismo):

```bash
# macOS/Linux
ipconfig getifaddr en0   # o: hostname -I / ip addr
```

## 2. Build de producción con la base URL configurada

La app empaquetada no tiene el proxy de Vite que hoy resuelve `/casas`,
`/auth`, etc. contra el backend — necesita una URL absoluta, vía
`VITE_API_BASE_URL` (T1, spec `android-capacitor-app`):

```bash
VITE_API_BASE_URL=http://<ip-de-lan>:8000 npm run build
```

Sin esta variable, el build es idéntico al de siempre (rutas relativas)
— no rompe el despliegue web existente.

## 3. Sincronizar el proyecto Android

```bash
npx cap sync android
```

Copia el `dist/` recién generado al proyecto nativo (`android/app/src/
main/assets/public`) y propaga `capacitor.config.ts`.

## 4. Abrir en Android Studio y correr

```bash
npx cap open android
```

Desde Android Studio:
- **Emulador/dispositivo real**: botón ▶ Run.
- **APK firmado**: `Build > Generate Signed Bundle / APK`.

## 5. Alternativa: live-reload sin recompilar (modo desarrollo)

Para iterar sin regenerar el APK en cada cambio de código, Vite puede
servir el frontend en modo dev y la app apuntar directamente a él:

1. Levantar Vite con `--host` (expone el dev server en la LAN):
   ```bash
   npm run dev -- --host
   ```
2. Descomentar el bloque `server` en `capacitor.config.ts`, apuntando a
   la IP de LAN del dev server:
   ```typescript
   server: { url: "http://<ip-de-lan>:5173", cleartext: true },
   ```
3. `npx cap sync android` de nuevo y correr la app — cada cambio de
   código en el frontend se refleja al instante, sin rebuildear el APK.
4. Al terminar, volver a comentar el bloque `server` antes de generar un
   build de producción real (paso 2 de arriba) — con `server` activo, la
   app siempre carga desde el dev server, nunca desde el `dist/`
   empaquetado.

## Troubleshooting

- **La app no conecta al backend**:
  - **CORS**: confirmar que `CORS_ALLOWED_ORIGINS` (env var del backend,
    ver `src/api/main.py`) incluye el origen real desde el que corre la
    app — por default cubre `capacitor://localhost`,
    `http://localhost`, `https://localhost`. Si se prueba en modo
    live-reload contra el dev server de Vite, agregar también ese
    origen (ej. `http://<ip-de-lan>:5173`).
  - **Cleartext**: si el backend corre sin TLS (HTTP plano, el caso
    normal en desarrollo/LAN), confirmar que `android/app/src/main/res/
    xml/network_security_config.xml` sigue permitiendo
    `cleartextTrafficPermitted="true"` y que `AndroidManifest.xml`
    sigue referenciándolo (`android:networkSecurityConfig`).
  - **Bind address**: el backend/frontend dockerizados deben escuchar
    en `0.0.0.0`, no solo `127.0.0.1` — si escuchan solo en loopback, un
    dispositivo externo (el emulador o un teléfono real) no puede
    alcanzarlos aunque estén en la misma red. `docker-compose.yml` ya
    publica los puertos correctamente para este caso.
  - **Firewall**: el firewall del sistema operativo del host puede
    bloquear conexiones entrantes a los puertos 8000/5173 desde otros
    dispositivos de la LAN (un emulador corre como proceso local, pero
    un teléfono real sí cruza la red física) — revisar las reglas de
    firewall si el emulador conecta pero un dispositivo real no.
