# Overview: gamificacion-puntos

## Data Model

Migración `0020_gamificacion` (una sola — las dos piezas de esquema de
esta spec son chicas y se shippean juntas):

```python
class LogroObtenido(Base):
    __tablename__ = "logros_obtenidos"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    casa_id = Column(GUID(), ForeignKey("casas.id"), nullable=False)
    miembro_id = Column(GUID(), ForeignKey("miembros.id"), nullable=False)
    # String, no FK a una tabla de catálogo — el catálogo de logros es
    # fijo en código (LOGROS_CATALOGO), no una entidad editable.
    logro_id = Column(String, nullable=False)
    obtenido_en = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
```

`Casa` (migración `0001`, ya existe) gana una columna nullable:

```python
meta_puntos_mensual = Column(Integer, nullable=True)
```

Ambas son seguras a nivel de FK-ordering: `LogroObtenido.casa_id`/
`miembro_id` referencian tablas (`casas`, `miembros`) creadas en la
migración `0001`, muy anterior a `0020` — `ForeignKey()` real a nivel
de modelo es seguro acá (mismo caso que `ResumenTarjeta.tarjeta_id`,
no el caso `Gasto.resumen_id`). `Casa.meta_puntos_mensual` es una
columna nueva en una tabla YA existente — igual que `Gasto.estado` en
su momento, se agrega directo a la clase, `create_all` la crea bien en
una base nueva.

## T1 — Niveles + rachas + ranking por mes (`ranking_service.py`)

Sin tabla nueva — todo se deriva de `HistorialTarea`, que ya tiene
`completada_en`/`puntos_obtenidos`.

```python
NIVELES = [
    (0, "Novato"),
    (50, "Activo"),
    (150, "Comprometido"),
    (300, "Campeón de la casa"),
]

def _nivel_de(puntos_totales: int) -> str:
    nivel = NIVELES[0][1]
    for umbral, nombre in NIVELES:
        if puntos_totales >= umbral:
            nivel = nombre
    return nivel
```

`calcular_racha(casa_id, miembro_id) -> int`: trae los días
calendario distintos (UTC — no hay noción de zona horaria de la casa
en ningún otro lado del proyecto, mismo criterio simple que el resto
de las fechas de la app) con al menos un `HistorialTarea` de ese
miembro, ordenados descendente, y cuenta consecutivos hacia atrás
empezando desde hoy o ayer (si hoy todavía no completó nada, la racha
no se considera rota hasta que termine el día).

`calcular_ranking(casa_id, mes: Optional[str] = None)`: agrega un
filtro opcional de rango de mes sobre `HistorialTarea.completada_en`
(rango `_rango_mes`-style, copia local en este archivo — mismo
criterio de "un servicio por responsabilidad" ya establecido, no se
importa el de `gasto_service.py`). Sin `mes`, el comportamiento es
exactamente el actual — `dashboard_service.armar_dashboard` sigue
llamándolo sin argumento (TC-004, regresión). Cada entrada del
resultado gana `nivel` (sobre el total HISTÓRICO del miembro, nunca
sobre el total filtrado por mes — el nivel es un logro acumulado de
siempre) y `racha`.

## T2 — Logros (`logro_service.py`, nuevo)

```python
LOGROS_CATALOGO = [
    {"id": "primera_tarea", "nombre": "Primera tarea", "tipo": "tareas", "umbral": 1},
    {"id": "diez_tareas", "nombre": "10 tareas completadas", "tipo": "tareas", "umbral": 10},
    {"id": "cincuenta_tareas", "nombre": "50 tareas completadas", "tipo": "tareas", "umbral": 50},
    {"id": "cien_puntos", "nombre": "100 puntos", "tipo": "puntos", "umbral": 100},
    {"id": "quinientos_puntos", "nombre": "500 puntos", "tipo": "puntos", "umbral": 500},
    {"id": "racha_siete", "nombre": "Racha de 7 días", "tipo": "racha", "umbral": 7},
    {"id": "racha_treinta", "nombre": "Racha de 30 días", "tipo": "racha", "umbral": 30},
]
```

`evaluar_logros(casa_id, miembro_id)`: cuenta tareas completadas y
puntos totales del miembro (`HistorialTarea`), calcula su racha
(reusa `ranking_service.calcular_racha`), y por cada entrada del
catálogo cuyo umbral ya se cruzó, inserta un `LogroObtenido` **si
todavía no existe uno para ese `(casa_id, miembro_id, logro_id)`** —
chequeo en el service layer antes del insert, nunca un constraint de
base de datos (mismo criterio ya establecido, `[SERV-01]`). Se llama
desde `tarea_service.completar_tarea`, después del commit y junto a
los hooks de `registrar_actividad` ya existentes (`[SERV-02]`: nunca
antes de confirmar la acción disparadora).

`listar_logros_obtenidos(casa_id) -> List[LogroObtenido]`: todos los
logros desbloqueados de la casa, para que el frontend arme "estos son
los logros de cada miembro" sin tener que pedir uno por uno.

## T3 — Meta de la casa (`casa_service.py`)

`actualizar_meta_puntos(casa_id, meta: Optional[int], actor)`:
requiere Administrador (`_validar_actor_admin`, mismo guard que otras
acciones de casa); `meta=None` desactiva la meta (vuelve a no
mostrarse en Inicio).

`calcular_progreso_meta(casa_id, mes: str) -> Optional[dict]`: `None`
si `Casa.meta_puntos_mensual` no está seteada; si lo está, suma los
puntos de **todos** los miembros ese mes (reusa `calcular_ranking`
con `mes`, sumando sus entradas) y devuelve
`{puntos_acumulados, meta, porcentaje}`.

`dashboard_service.DashboardCasa` gana un campo `meta_casa:
Optional[dict]` (mismo patrón que `balance`/`tarjetas_con_alerta`) —
alias camelCase `metaCasa` en el schema de la API (`[API-01]`, solo el
campo contenedor, no sus claves internas).

## T4 — Frontend

- **Ranking.tsx**: selector de mes (mismo componente que Balance/
  Gastos, mes actual preseleccionado — pasado a `obtenerRanking`);
  chip de nivel y "🔥 N días" de racha por fila; nueva sub-sección
  "Logros" listando, por miembro, los logros ya desbloqueados (mismo
  patrón visual que "Historial de tareas" dentro de `Tareas.tsx`).
- **Miembros.tsx**: campo "Meta de puntos mensual" + botón guardar,
  visible solo si `puedeGestionarMiembros(rolUsuarioActual)` (mismo
  guard ya usado ahí para agregar/desactivar miembros).
- **InicioCasa.tsx**: card "Meta de la casa" con barra de progreso
  (`LinearProgress` de MUI), renderizada solo cuando
  `dashboard.metaCasa` no es `null`.

## Tradeoffs

- **Racha en UTC, no zona horaria local de la casa**: el proyecto no
  tiene ningún concepto de zona horaria configurable hoy (todas las
  fechas de gastos/tareas ya son ingenuas); introducir uno solo para
  la racha sería una inconsistencia nueva, no una corrección.
- **Nivel sobre el total histórico, ranking sobre el mes**: son dos
  ejes distintos a propósito — el nivel es un logro de largo plazo
  (nunca baja), el ranking mensual es la competencia del momento
  (se resetea). Mezclarlos confundiría cuál de los dos es cuál.
- **Catálogo de logros fijo en código, no una tabla editable**: dado
  el alcance (7 logros, ninguno pensado para cambiar seguido), una
  tabla de catálogo sería una abstracción prematura — se puede migrar
  a una si algún día se necesita editar logros sin deploy.
- **Meta de la casa, no por miembro**: pedido explícito del usuario —
  fomenta cooperación en vez de competencia adicional (ya cubierta por
  el ranking).
