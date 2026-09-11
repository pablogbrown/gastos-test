<!-- nybo:managed:start:stack-summary -->
## Stack

react + PostgreSQL
<!-- nybo:managed:end:stack-summary -->

<!-- nybo:managed:start:quick-start -->
## Quick Start

```sh
npm install
npm run dev
```
<!-- nybo:managed:end:quick-start -->

## Backend (Python)

```sh
pip install -r requirements-dev.txt
python3 -m pytest
uvicorn src.api.main:app --reload
```

`DATABASE_URL` defaults to an in-memory SQLite (used by the test suite);
set it to a PostgreSQL DSN for real runs, e.g.
`postgresql+psycopg2://user:pass@localhost:5432/taskia`.

## Desarrollo local con Docker

Alternativa a los pasos de arriba (venv + npm) que no requiere instalar
Python, Node ni PostgreSQL en el host: levanta los 3 servicios (base de
datos PostgreSQL real, backend FastAPI, frontend Vite) con hot-reload en
ambos lados.

**Prerequisitos:** Docker + Docker Compose.

```sh
cp .env.example .env   # opcional — los defaults ya funcionan sin esto
make up                # levanta db + backend + frontend (docker compose up --build)
```

- Backend: http://localhost:8000 (`/health`, `/casas`, etc.)
- Frontend: http://localhost:5173

Comandos disponibles:

| Comando | Qué hace |
|---|---|
| `make up` | Levanta los 3 servicios (reconstruye imágenes si cambiaron). |
| `make down` | Detiene y elimina los 3 servicios (conserva el volumen de datos de Postgres). |
| `make build` | Reconstruye las imágenes de backend y frontend sin levantar nada. |
| `make logs` | Sigue los logs de los 3 servicios. |
| `make test` | Corre la suite de pytest del backend dentro del contenedor, contra el Postgres real del servicio `db`. |
| `make migrate` | Aplica las migraciones existentes contra el Postgres del servicio `db`. |

El código fuente de `src/` y `tests/` está montado como volumen dentro de
los contenedores — los cambios se reflejan sin reconstruir la imagen
(hot-reload de `uvicorn --reload` y de Vite). El fallback a
`sqlite:///:memory:` de la sección "Backend (Python)" de arriba no
cambia: `DATABASE_URL` solo se setea a Postgres dentro de
`docker-compose.yml`.