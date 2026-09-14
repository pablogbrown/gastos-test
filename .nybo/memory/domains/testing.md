# Domain: testing

testing domain

## Conventions
<!-- Each convention has metadata as an HTML comment -->
<!-- added: YYYY-MM-DD | feature: feature-name | confidence: high|medium|low | verified: YYYY-MM-DD -->

<!-- TEST-01 | added: 2026-09-14 | feature: fix-nombres-miembro-ranking-dashboard | confidence: high | verified: 2026-09-14 -->
- Live/manual smoke environment: `cp .env.example .env` (optional —
  defaults work) then `make up` (`docker compose up --build`) brings up
  Postgres + FastAPI backend + Vite frontend with hot reload. Backend:
  `http://localhost:8000` (`/health`, `/casas`, ...). Frontend:
  `http://localhost:5173`. `make down` tears it down (keeps the Postgres
  volume). No seed data/test users are provisioned — reaching any screen
  requires `POST /auth/registro` then `POST /auth/login` through the
  Login/Registro screens (or directly against the API) to obtain a JWT,
  then creating/joining a Casa via the app's own flow. See README.md
  "Desarrollo local con Docker".
