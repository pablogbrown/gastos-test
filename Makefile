.PHONY: up down build logs test migrate

# Entorno local dockerizado de taskia — ver README "Desarrollo local con
# Docker" y .nybo/plans/dockerize-local-env/. Un solo punto de entrada
# para no tener que recordar flags de `docker compose`.

up: ## Levanta db + backend + frontend (reconstruye imágenes si cambiaron).
	docker compose up --build

down: ## Detiene y elimina los 3 servicios (conserva el volumen de datos).
	docker compose down

build: ## Reconstruye las imágenes de backend y frontend sin levantar nada.
	docker compose build

logs: ## Sigue los logs de los 3 servicios.
	docker compose logs -f

test: ## Corre la suite de pytest del backend dentro del contenedor.
	docker compose exec backend python3 -m pytest

migrate: ## Aplica las migraciones existentes contra el Postgres del servicio db.
	docker compose exec backend python3 -c "from src.db.base import engine; from src.db.migrate import run_migrations; run_migrations(engine)"
