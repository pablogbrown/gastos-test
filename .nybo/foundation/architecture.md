# Architecture — taskia

## Stack

```mermaid
graph TD
  Browser([Browser]) --> FE
  FE["React"] --> API
  API["Python"] --> DB
  DB[("PostgreSQL")]
  FE --> Hosting["AWS"]
```

## Data Model

```mermaid
erDiagram
  %% No entities defined
```

## Key Decisions

- File structure: feature-based
- Error handling: Result pattern
- Auth model: RBAC

<!-- nybo:managed-block:start v1 -->
### Dockerized local development environment (added 2026-09-14, feature: dockerize-local-env)
Local development runs via docker-compose orchestrating three services (PostgreSQL, FastAPI backend, Vite frontend) on a shared network, with source volumes mounted for hot-reload.
The backend reads DATABASE_URL to connect to the dockerized PostgreSQL service; the existing sqlite:///:memory: fallback in src/db/base.py is preserved when DATABASE_URL is unset (tests, non-Docker local runs).
The Vite dev server proxies to the backend's docker-compose service name rather than a fixed host URL.
A Makefile wraps day-to-day operations (up, down, build, logs, test, migrate) as single-invocation commands.
**Rationale:** Hoy correr la app localmente requiere un venv de Python, `npm install`, y confiar en el fallback de SQLite en memoria — nada de eso refleja producción (PostgreSQL) ni es reproducible entre máquinas. Un entorno dockerizado con comandos `make` simples baja la fricción de onboarding y acerca el desarrollo local a producción.
### Material UI adoption for responsive navigation (added 2026-09-14, feature: ui-modernization)
The app adopts Material UI (MUI) as its component and theming system, with a single ThemeProvider (`src/frontend/theme.ts`) defining a consistent palette and typography across all screens.
The navigation shell (`App.tsx`) switches between a `BottomNavigation` (mobile, viewport &lt; 600px) and an `AppBar` with tabs (desktop, ≥ 600px) via `useMediaQuery` on MUI's default `sm` breakpoint, covering the same 7 existing sections.
All 8 existing screens were rebuilt on MUI components (TextField, Button, List, Table, Card) in place of unstyled native HTML elements, while existing API client calls and data logic were left unchanged.
Touch targets for bottom-navigation items are configured at the theme level to meet a 44x44px minimum tap-target size.
**Rationale:** La UI actual es HTML plano sin estilos, con una fila de botones como navegación — no es utilizable cómodamente en mobile y no transmite un producto terminado. Esto bloquea que cualquier usuario real (no solo quien la construyó) la use desde su teléfono.
**Rejected:** Se elige Material UI sobre Chakra (ambas eran opciones válidas) por su componente `BottomNavigation` nativo, que resuelve directamente el patrón de navegación pedido sin construirlo a mano.
<!-- nybo:managed-block:end v1 -->
