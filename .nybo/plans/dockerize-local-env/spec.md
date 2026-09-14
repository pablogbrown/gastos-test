# Dockerizar el Entorno Local

## Intention

### What
Permite a un desarrollador levantar taskia completo (backend FastAPI, frontend Vite, base de datos PostgreSQL) en su máquina local con Docker, sin instalar Python, Node o Postgres directamente en el host.

### Why
Hoy correr la app localmente requiere un venv de Python, `npm install`, y confiar en el fallback de SQLite en memoria — nada de eso refleja producción (PostgreSQL) ni es reproducible entre máquinas. Un entorno dockerizado con comandos `make` simples baja la fricción de onboarding y acerca el desarrollo local a producción.

## Solution
Tres servicios orquestados por `docker-compose` (PostgreSQL, backend FastAPI, frontend Vite dev server) en una red común, con volúmenes montando el código fuente para hot-reload. Un Makefile expone los comandos de uso diario (`up`, `down`, `build`, `logs`, `test`, `migrate`) sobre esos servicios.
See **[Solution Overview](feat/00-overview.md)** for the full architecture, data model, contracts, and UX/UI.

## Outcome
Un desarrollador nuevo clona el repo, corre `make up`, y en minutos tiene el backend, el frontend y una base PostgreSQL real corriendo y hablando entre sí — con hot-reload en ambos lados — sin tocar su entorno de Python/Node local.

## Requirements

| ID | Requirement | Business Rules |
|---|---|---|
| REQ-001 | Un desarrollador debe poder levantar los 3 servicios (base de datos, backend, frontend) con un solo comando (`make up`). | `docker-compose` orquesta los 3 servicios en una red común; el backend espera a que PostgreSQL acepte conexiones antes de arrancar (`depends_on` con healthcheck). |
| REQ-002 | El backend debe conectarse a PostgreSQL cuando corre dentro de Docker, sin alterar el comportamiento actual de los tests. | `DATABASE_URL` se inyecta como variable de entorno del servicio `backend` en `docker-compose.yml`; el fallback `sqlite:///:memory:` de `src/db/base.py` permanece intacto para cuando no hay `DATABASE_URL` (tests, ejecución local sin Docker). |
| REQ-003 | Las 4 migraciones existentes deben correr limpias contra PostgreSQL, no solo contra la SQLite usada en tests. | Los tipos de columna ya son portables (GUID custom, `Enum` estándar de SQLAlchemy) — se valida contra un Postgres real antes de dar la tarea por terminada, no se asume por inspección. |
| REQ-004 | El frontend dockerizado debe consumir el backend dockerizado (no una URL de host fija) y reflejar cambios de código sin reconstruir la imagen. | El proxy de Vite apunta al nombre del servicio de `docker-compose` (no `127.0.0.1`) cuando corre en Docker; los volúmenes montan el código fuente de ambos servicios para hot-reload. |
| REQ-005 | Un desarrollador debe poder ejecutar las operaciones comunes (levantar, bajar, ver logs, correr tests, aplicar migraciones) con comandos `make` simples. | El Makefile expone al menos `up`, `down`, `build`, `logs`, `test`, `migrate`, cada uno como una única invocación sin flags que memorizar. |

## Test Cases

| ID | Given/When/Then | Type |
|---|---|---|
| TC-001 (REQ-001) | **Given** un checkout limpio del repo con Docker instalado **When** se corre `make up` **Then** los 3 servicios arrancan y `GET /health` del backend responde 200 | `[INTEGRATION]` |
| TC-002 (REQ-002) | **Given** el backend corriendo dentro de `docker-compose` con `DATABASE_URL` apuntando a Postgres **When** se registra un dato vía la API **Then** persiste en la base PostgreSQL del servicio `db` | `[INTEGRATION]` |
| TC-003 (REQ-002) | **Given** el backend corriendo sin la variable `DATABASE_URL` seteada (como en los tests) **When** arranca **Then** sigue usando `sqlite:///:memory:` exactamente como hoy | `[UNIT]` |
| TC-004 (REQ-003) | **Given** un PostgreSQL vacío **When** corren las 4 migraciones en orden **Then** las tablas y el enum de rol se crean sin error | `[INTEGRATION]` |
| TC-005 (REQ-004) | **Given** el frontend corriendo en el contenedor Vite dentro de `docker-compose` **When** un usuario completa el formulario de "Crear casa" en el navegador **Then** la request llega al backend dockerizado y la casa se crea, visible en la pantalla de Inicio | `[E2E]` |
| TC-006 (REQ-005) | **Given** el Makefile **When** se corre `make test` **Then** ejecuta la suite de pytest del backend contra el entorno dockerizado y reporta el resultado | `[INTEGRATION]` |

## Sources

| Type | Reference | Location |
|---|---|---|
| Session | Pedido del usuario: dockerizar la ejecución local + Makefile | Capturado en esta conversación, 2026-09-11. Decisiones confirmadas: PostgreSQL en el contenedor, frontend servido con Vite dev server + hot-reload. |
