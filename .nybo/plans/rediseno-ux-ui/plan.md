# Rediseño UX/UI de taskia - Feature Plan

| | |
| --- | --- |
| Progress | [progress.md](progress.md) |

feature_kind: multi_spec

## Feature Branch

`feat/rediseno-ux-ui`

## Sub-Spec DAG

| Spec | Branch | Depends on | Status |
| --- | --- | --- | --- |
| sistema-visual | `feat/rediseno-ux-ui--sistema-visual` | — | approved |
| pantallas-financieras | `feat/rediseno-ux-ui--pantallas-financieras` | sistema-visual | approved |
| pantallas-casa | `feat/rediseno-ux-ui--pantallas-casa` | sistema-visual | approved |
| auth-onboarding | `feat/rediseno-ux-ui--auth-onboarding` | sistema-visual | approved |

```yaml
spec_dag:
  sistema-visual: []
  pantallas-financieras: [sistema-visual]
  pantallas-casa: [sistema-visual]
  auth-onboarding: [sistema-visual]
```

## Split Rationale

El pedido — "rediseñar todo el frontend, las vistas y la experiencia de uso" — cubre 16 pantallas y una identidad visual completamente nueva. Se evaluó contra las tres pruebas de spec atómica (independent deliverable / independent review / concern separation):

- **sistema-visual** (fundación): pasa las tres — es entregable de forma independiente (el nuevo tema + la pantalla Inicio como bandera ya demuestran y validan la nueva identidad visual antes de tocar el resto), revisable de forma independiente (un humano puede aprobar el sistema de diseño sin haber visto todavía cómo se aplica a cada pantalla), y separa un concern real: fundación (tokens + componentes compartidos) vs. consumo (aplicar esos tokens pantalla por pantalla) — el mismo patrón fundación-vs-consumidor citado como split válido en la guía de la skill.
- **pantallas-financieras**, **pantallas-casa**, **auth-onboarding**: cada una pasa las tres una vez que sistema-visual existe — cada grupo de pantallas es usable y entrega valor real de forma independiente de que los otros grupos ya estén rediseñados (un usuario ya se beneficia de ver Gastos/Balance/Tarjetas rediseñados aunque Miembros/Ranking sigan con el diseño viejo); cada spec es revisable sin haber visto las otras (no hay referencias cruzadas de comportamiento entre ellas); y el eje de separación es real y ya existe en la propia navegación de la app — pantallas financieras (Gastos/Balance/Tarjetas/Suscripciones/Préstamos/Mantenimiento) comparten patrones de lista+monto+chip+FAB, pantallas de casa/social (Miembros/Ranking/Tareas/Actividad) comparten patrones de perfil+progreso+feed, y auth/onboarding (Login/Registro/Selector de casas/Crear casa) es un contexto de actor distinto (usuario no autenticado) con patrones de formulario centrado, no de lista.

Ninguna de las cuatro specs individualmente excede el cap de 4 tasks, así que el split no fue necesario "para aliviar el cap" — pasó las tres pruebas independientemente de eso.

## Next steps

`/nybo-build rediseno-ux-ui/specs/sistema-visual` primero (bloquea a las otras tres) — luego `pantallas-financieras`, `pantallas-casa` y `auth-onboarding` en cualquier orden, o vía `/nybo-orchestrate rediseno-ux-ui` para las cuatro coordinadas.
