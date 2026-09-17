# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added

- feat(gastos-multi-moneda): los gastos, cuotas y suscripciones ahora admiten pesos (ARS) o dólares (USD) — el balance de la casa se calcula y muestra por separado para cada moneda, sin sumar ni convertir entre sí, y las transferencias sugeridas nunca cruzan monedas.

- feat(tarjetas-credito): nueva pantalla "Tarjetas" para registrar tarjetas de crédito (banco, últimos dígitos, cierre/vencimiento, saldo) y un banner de alerta en Inicio cuando el vencimiento de alguna tarjeta está a 7 días o menos, o ya venció.

- feat(importar-resumen-tarjeta): subir el PDF de un resumen (BBVA Visa Platinum) actualiza la tarjeta y crea automáticamente cada gasto del resumen, sin ningún paso de revisión — detecta compras en cuotas en curso (importando solo las cuotas restantes) y suscripciones conocidas (Netflix, Spotify, Disney+), vinculándolas a los mecanismos ya existentes; las líneas de impuestos y cargos nunca se importan.

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
- fix(frontend): Ranking y el inicio de la casa muestran el nombre del miembro en vez de su UUID crudo, tanto en la tabla completa de Ranking como en el mini-ranking de la pantalla de Inicio.
- fix(frontend): crear una tarea con el campo Puntos vacío ahora muestra el error de validación correspondiente en vez de crear silenciosamente una tarea de 0 puntos.

### Changed

- feat(services): el Balance ahora se filtra por mes (selector en la pantalla, mes actual por defecto) en vez de sumar todo el historial de gastos desde siempre — base necesaria para que un gasto futuro (cuotas, suscripciones) no infle la deuda de hoy.

### Added

- feat(auth): un Administrador puede agregar como miembro a alguien que todavía no tiene cuenta — queda como "Pendiente" y se vincula automáticamente en cuanto esa persona se registra con el mismo email.
- feat(services): un gasto se puede registrar en cuotas — se generan N gastos, uno por mes, cada uno por el importe total dividido en partes iguales; el balance solo refleja cada cuota en el mes que le corresponde.
- feat(services): un Administrador puede crear suscripciones mensuales (ej. Netflix, gimnasio) — se genera automáticamente el gasto de cada mes mientras estén activas, sin acción manual; nueva pantalla "Suscripciones" para verlas y cancelarlas.

### Added

- feat(gastos-estado-pago): cada gasto registra si ya está saldado ("Pagado") o pendiente ("A pagar") — un gasto manual nace "Pagado", y una cuota/suscripción/consumo importado nace "A pagar"; se puede cambiar con un clic desde el listado. Puramente informativo, no afecta el Balance.

### Changed

- feat(nav-agrupada): el menú superior (desktop) agrupa las 9 pantallas en 4 elementos de primer nivel — Inicio, Casa (Miembros/Ranking/Actividad), Gastos (Gastos/Balance/Tarjetas/Suscripciones) y Tareas — con menús desplegables para Casa/Gastos; la barra inferior en mobile no cambia.
- feat(gastos-vista-mensual): la pantalla Gastos ahora muestra un selector de mes (mismo componente que Balance, mes actual preseleccionado) que filtra el listado — en vez de una única lista con todo el historial mezclado; el dashboard de Inicio no cambia, sigue mostrando los últimos 10 gastos de toda la casa.

### Added

- feat(prestamos-entre-miembros): nueva pantalla "Préstamos" para registrar deudas explícitas entre dos miembros (quién presta, a quién, importe, moneda, fecha), con estado pendiente/pagado cambiable con un clic — completamente separada de Gastos y Balance, sin afectar ningún cálculo de la casa.

### Changed

- feat(gastos-sin-reparto): un gasto ya no se reparte entre participantes ni genera ninguna deuda individual — pasa a ser simplemente una salida de fondos de la casa. Balance ahora muestra el total gastado de la casa por moneda más, a modo informativo, cuánto aportó cada miembro — sin ninguna cifra de "le correspondía" ni transferencias sugeridas (esa deuda entre personas ahora se registra explícitamente con Préstamos).

### Removed

- feat(gastos-sin-reparto): se elimina `GastoParticipante` y todo el reparto de gastos entre participantes, junto con su historial — el formulario "Nuevo gasto" ya no pide elegir con quién se comparte.

### Changed

- feat(prestamos-confirmacion-mutua): un préstamo recién registrado ya no queda activo al instante — la parte que lo registra queda confirmada automáticamente y la otra debe confirmarlo o rechazarlo; solo confirmado por ambas partes habilita marcarlo pagado/pendiente. Evita cargas de préstamos que no correspondan.

### Added

- feat(mantenimiento-casa): nueva pantalla "Mantenimiento" (agrupada con "Tareas") para cargar cuestiones de mantenimiento de la casa — fecha estimada, periodicidad (semanal a anual), lista de materiales necesarios con cantidad y estado conseguido/pendiente, y una alerta visual en Inicio cuando se acerca la fecha; un ítem recurrente no se puede completar antes de su fecha estimada.

- feat(mantenimiento-autos): nueva pantalla "Mantenimiento Autos" para registrar los autos de la casa y cargarles sus services/mantenimientos, con la misma mecánica (fecha estimada, periodicidad, materiales, alerta) ya construida para mantenimiento de la casa — agrupados por auto y separados de "Mantenimiento".

### Fixed

- fix(services): las cuotas restantes importadas de un resumen ahora muestran el número de cuota en su descripción (ej. "(4/6)"), igual que una serie de cuotas nueva — antes quedaban indistinguibles entre sí en el listado de Gastos.
- fix(mantenimiento): presionar Enter en el campo "Material" (al cargar un ítem de mantenimiento, de la casa o de un auto) ya no envía el formulario completo — antes creaba el ítem sin ningún material, sin ningún error, perdiendo silenciosamente lo que se acababa de tipear.

### Added

- feat(resumen-tarjeta-pago): cada resumen de tarjeta importado queda registrado (tarjeta, fechas, saldos, cantidad de gastos, estado) y vinculado a los gastos que generó; volver a importar el mismo resumen (misma tarjeta y fecha de cierre) se rechaza para evitar gastos duplicados. Nueva acción "Pagar resumen" en la pantalla Tarjetas que marca el resumen y todos sus gastos vinculados como pagados en un solo paso.
- feat(gastos): el historial de gastos ahora pagina de a 50 resultados en vez de mostrar todo el mes de una sola vez.

### Changed

- refactor(frontend): se elimina la duplicación de `parseJsonOrThrow` en los 10 clientes de API del frontend, ahora compartida desde `httpError.ts` — sin cambio de comportamiento (hallazgo de auditoría de código).
- refactor(services): `registrar_gasto`/`registrar_gasto_cuotas_restantes`/`registrar_suscripcion_detectada` agrupan sus atributos opcionales (cuotas, moneda, tarjeta, estado, resumen) en un único objeto `GastoMetadata` en vez de parámetros sueltos — sin cambio de comportamiento (hallazgo de auditoría de código).
