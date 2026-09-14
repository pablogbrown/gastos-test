# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added

- feat(frontend): Added Login/Registro screens and JWT-based session storage on the frontend, replacing the X-Usuario-Id header. (`.nybo/plans/auth-frontend/`)

- feat(auth): Added global Usuario entity with email/password registration and JWT login, replacing X-Usuario-Id header with real multi-casa membership resolution. (`.nybo/plans/auth-backend/`)

- feat(frontend): Restyled all 8 screens with Material UI; added a responsive BottomNavigation/AppBar shell at the sm (600px) breakpoint, preserving existing behavior. (`.nybo/plans/ui-modernization/`)

- feat(db): Dockerized local dev environment (Postgres, backend, frontend) orchestrated via docker-compose with a Makefile wrapper. (`.nybo/plans/dockerize-local-env/`)

- feat(gestion-domestica): creación de casas y gestión de miembros con roles Administrador/Miembro — permite armar el grupo que comparte gastos y tareas, con desactivación de miembros que preserva su historial.
- feat(gestion-domestica): registro de gastos compartidos con división automática entre participantes y balance por miembro — responde quién pagó, quién debe, y cuánto transferir para saldar cuentas.
- feat(gestion-domestica): gestión de tareas domésticas con estados, asignación, recurrencia, sistema de puntos y ranking de participación.
- feat(gestion-domestica): pantalla principal de la casa (miembros, gastos recientes, balance, tareas pendientes/completadas, ranking) e historial general de actividad.
- feat(dockerize-local-env): entorno local dockerizado (PostgreSQL, backend, frontend con hot-reload) más un Makefile (`up`/`down`/`build`/`logs`/`test`/`migrate`) — baja la fricción de onboarding y acerca el desarrollo local a producción.

### Changed

- feat(ui-modernization): las 8 pantallas y la navegación se rediseñaron con Material UI — bottom tab bar en mobile, barra superior en desktop, sin cambiar ningún comportamiento funcional existente.

### Added

- feat(usuarios-auth): pantallas de registro y login, y un Usuario global que puede pertenecer a más de una Casa (selector de casas al ingresar).

### Security

- feat(usuarios-auth): reemplaza el header placeholder `X-Usuario-Id` (cualquier UUID sin verificar) por autenticación real con JWT (email + contraseña hasheada) en todas las rutas de casas, gastos, tareas y dashboard.
- fix(auth): la UI ya no muestra "Agregar miembro"/"Desactivar" a un usuario con rol `member`, ni "Marcar completada" en tareas ajenas — el rol y la identidad de miembro se resuelven del JWT real en vez de estar hardcodeados a "admin".

### Fixed

- fix(services): un Usuario ya no puede terminar con más de una membresía activa en la misma casa — evita que un crash `MultipleResultsFound` (500) rompa cualquier request autenticado de ese usuario a esa casa.
- fix(services): agregar o desactivar un miembro ahora queda registrado en el Historial de actividad de la casa (antes ninguna de las dos acciones dejaba rastro).
