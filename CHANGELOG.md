# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added

- feat(gestion-domestica): creación de casas y gestión de miembros con roles Administrador/Miembro — permite armar el grupo que comparte gastos y tareas, con desactivación de miembros que preserva su historial.
- feat(gestion-domestica): registro de gastos compartidos con división automática entre participantes y balance por miembro — responde quién pagó, quién debe, y cuánto transferir para saldar cuentas.
- feat(gestion-domestica): gestión de tareas domésticas con estados, asignación, recurrencia, sistema de puntos y ranking de participación.
- feat(gestion-domestica): pantalla principal de la casa (miembros, gastos recientes, balance, tareas pendientes/completadas, ranking) e historial general de actividad.
- feat(dockerize-local-env): entorno local dockerizado (PostgreSQL, backend, frontend con hot-reload) más un Makefile (`up`/`down`/`build`/`logs`/`test`/`migrate`) — baja la fricción de onboarding y acerca el desarrollo local a producción.
