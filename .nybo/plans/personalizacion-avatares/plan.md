# Personalización de avatares - Feature Plan

| | |
| --- | --- |
| Progress | [progress.md](progress.md) |

feature_kind: multi_spec

## Feature Branch

`feat/personalizacion-avatares`

## Sub-Spec DAG

| Spec | Branch | Depends on | Status |
| --- | --- | --- | --- |
| avatares-economia | `feat/personalizacion-avatares--avatares-economia` | — | approved |
| tienda-accesorios | `feat/personalizacion-avatares--tienda-accesorios` | avatares-economia | approved |
| perfil-avatar-ui | `feat/personalizacion-avatares--perfil-avatar-ui` | avatares-economia, tienda-accesorios | approved |

```yaml
spec_dag:
  avatares-economia: []
  tienda-accesorios: [avatares-economia]
  perfil-avatar-ui: [avatares-economia, tienda-accesorios]
```

## Decisiones ya tomadas (fuera de esta spec, confirmadas por el usuario vía AskUserQuestion)

- **Técnica visual**: animaciones Lottie, reproducidas con `lottie-react` (nueva dependencia — ver `avatares-economia`'s Dependencies).
- **Economía**: moneda separada, ganada en paralelo a los puntos (mismo trigger: completar una tarea). Renombrada internamente **"créditos"** en vez de "monedas" — el proyecto ya usa la palabra "moneda" para ARS/USD (`gastos-multi-moneda`); reusar el mismo término para dos conceptos distintos (divisa de gasto vs. divisa de tienda) generaría confusión real en código y specs futuras. La UI en español sigue diciendo "créditos", nunca "monedas".
- **Progresión**: el nivel actual (Novato/Activo/Comprometido/Campeón, ya existente en `ranking_service.NIVELES`) determina qué razas de avatar están desbloqueadas — no una mascota que evoluciona visualmente (los packs Lottie gratuitos dan variedad de animales, no etapas cachorro/adulto del mismo animal).
- **Alcance**: sistema grande/económico completo (rareza, slots de accesorios, ítems de tiempo limitado) sobre un catálogo inicial v1 acotado a lo curable gratis (LottieFiles, licencia Simple License, uso comercial libre).
- **Assets**: overlay simple (ícono/badge) para accesorios, nunca integrados a la animación Lottie del cuerpo — reemplazables por archivo/URL sin tocar código.
- **Navegación**: ninguna pantalla nueva es un ítem de primer nivel del bottom nav (ya al límite de 4, ver fix `nav-mobile-agrupada`) — todo vive dentro del grupo "Casa" existente.

## Split Rationale

- **avatares-economia** (fundación): pasa las tres pruebas — entregable de forma independiente (un miembro ya puede ganar créditos y elegir una raza desbloqueada sin que exista todavía ninguna tienda de accesorios), revisable sin haber visto las otras dos (no depende de su comportamiento para tener sentido), y separa un concern real de fundación (economía de créditos + catálogo de razas + reproductor Lottie compartido) vs. consumo.
- **tienda-accesorios** (depende de avatares-economia): entrega valor real por sí sola (comprar/equipar accesorios) una vez que existen créditos que gastar; revisable sin haber visto la integración visual; concern separado — mecánica de tienda/inventario, no presentación.
- **perfil-avatar-ui** (depende de ambas): concern real y distinto — integración visual en pantallas YA EXISTENTES (Miembros/Ranking) más una pantalla nueva de selección/tienda — no mecánica de negocio nueva, solo consumo y presentación de lo que las otras dos ya construyeron.

## Next steps

`/nybo-build personalizacion-avatares/specs/avatares-economia` primero (bloquea a las otras dos) — luego `tienda-accesorios` y por último `perfil-avatar-ui` (depende de ambas), o vía `/nybo-orchestrate personalizacion-avatares`.
