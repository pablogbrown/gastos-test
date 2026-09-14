# Task 2 — Frontend Dockerfile y proxy env-aware

## Scope
- `Dockerfile.frontend` — imagen del frontend en modo desarrollo.
- `vite.config.ts` — hacer el target del proxy configurable por variable de entorno.
- `.dockerignore` — (compartido con T1, agregar entradas de frontend si faltan: `dist/`, `node_modules/`).

## Changes
### Infra / Frontend
- `Dockerfile.frontend`: imagen base `node:20-slim`, copia `package.json`/`package-lock.json`, `npm install`, copia el código, expone el puerto 5173, comando `npm run dev -- --host 0.0.0.0`.
- `vite.config.ts`: el proxy de `/casas` (hoy fijo a `http://127.0.0.1:8000`) lee el target de `process.env.VITE_API_PROXY_TARGET`, con `http://127.0.0.1:8000` como default — así el mismo archivo sirve para desarrollo local sin Docker (default) y para Docker (`docker-compose` setea la variable al nombre del servicio `backend`).

## Design Rationale
Hacer el proxy configurable por env var (en vez de hardcodear el nombre del servicio Docker) evita que el archivo de configuración de Vite tenga que cambiar entre "corro esto con Docker" y "lo corro suelto en mi máquina" — un solo `vite.config.ts` sirve a ambos casos.

## Dependencies
Ninguna — independiente de T1 (mismo layer de infraestructura, sin overlap de archivos).

## Done When
- [ ] La imagen del frontend construye (`docker build -f Dockerfile.frontend .`) sin error.
- [ ] `npm run dev` local (sin Docker, sin la variable seteada) sigue apuntando a `127.0.0.1:8000` como antes — no debe romper el flujo ya verificado manualmente.
- [ ] Con `VITE_API_PROXY_TARGET=http://backend:8000`, el proxy reenvía correctamente (se verifica en T3/TC-005 una vez exista `docker-compose`).

## Interfaces Produced
Ninguno.

## Standalone Verifiable
Sí — la imagen construye y `npm run dev` local sigue funcionando exactamente igual que hoy; el comportamiento dentro de Docker se confirma en T3.
