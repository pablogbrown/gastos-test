# Aplicación de Gestión Doméstica

## 1. Objetivo

El objetivo de la aplicación es permitir que las personas que comparten una vivienda puedan organizar de manera simple los **gastos comunes** y las **tareas domésticas**.

La aplicación debe permitir crear una casa, incorporar miembros, registrar gastos realizados por cada persona y distribuir las responsabilidades domésticas.

Además, debe existir un sistema de puntos que incentive la participación de los miembros mediante la asignación de puntos por cada tarea completada.

---

## 2. Concepto principal

La unidad principal de organización será una **Casa**.

Una casa representa un grupo de personas que comparten gastos y responsabilidades domésticas.

Cada casa podrá tener:

- Nombre.
- Miembros.
- Gastos.
- Tareas.
- Historial de actividades.
- Ranking de puntos.

Una persona podrá participar en una o más casas.

---

## 3. Creación de una casa

Un usuario deberá poder crear una nueva casa.

Al crearla deberá indicar como mínimo:

- Nombre de la casa.

Ejemplos:

- Casa Brown.
- Departamento Centro.
- Casa Universitaria.
- Familia Pérez.

La persona que crea la casa será inicialmente miembro de la misma y tendrá permisos para administrarla.

---

## 4. Miembros de la casa

El administrador de una casa deberá poder agregar nuevos miembros.

Cada miembro deberá tener al menos:

- Nombre.
- Identificación dentro de la casa.

Los miembros podrán participar en:

- Gastos.
- Tareas.
- Sistema de puntos.
- Ranking de la casa.

También deberá ser posible eliminar o desactivar miembros que ya no pertenezcan a la casa.

La eliminación de un miembro no deberá borrar el historial de gastos o tareas que haya realizado anteriormente.

---

# 5. Gestión de gastos

Los miembros deberán poder registrar gastos realizados para la casa.

Cada gasto deberá incluir:

- Descripción.
- Importe.
- Fecha.
- Persona que realizó el gasto.
- Categoría.

Ejemplos de categorías:

- Supermercado.
- Servicios.
- Alquiler.
- Limpieza.
- Mantenimiento.
- Mascotas.
- Comida.
- Otros.

Ejemplo:

**Compra supermercado**

Importe: $75.000  
Pagado por: Pablo  
Categoría: Supermercado  
Fecha: 10/09/2026

---

## 6. Participantes de un gasto

Un gasto podrá corresponder a todos los miembros de la casa o solamente a algunos.

Ejemplo:

Si viven cuatro personas en una casa y se registra un gasto de $40.000 correspondiente a todos los miembros, cada persona deberá asumir $10.000.

También deberá poder registrarse un gasto correspondiente solamente a determinados miembros.

Ejemplo:

Una cena de $30.000 correspondiente solamente a Ana y Pablo deberá dividirse entre ellos.

---

## 7. Balance de gastos

La aplicación deberá calcular automáticamente cuánto dinero pagó cada miembro y cuánto debería haber pagado.

De esta manera deberá mostrar un balance entre los miembros.

Ejemplo:

| Miembro | Pagó | Le correspondía | Balance |
|---|---:|---:|---:|
| Pablo | $80.000 | $50.000 | +$30.000 |
| Ana | $20.000 | $50.000 | -$30.000 |

La aplicación deberá permitir identificar fácilmente:

- Quién tiene dinero a favor.
- Quién tiene dinero pendiente.
- Cuánto debería transferir cada persona para equilibrar las cuentas.

---

# 8. Gestión de tareas domésticas

Los miembros deberán poder crear tareas domésticas.

Cada tarea deberá incluir:

- Nombre.
- Descripción opcional.
- Cantidad de puntos.
- Persona responsable, si existe.
- Fecha prevista, si corresponde.
- Estado.

Ejemplos:

| Tarea | Puntos |
|---|---:|
| Lavar los platos | 5 |
| Sacar la basura | 3 |
| Limpiar el baño | 10 |
| Cocinar | 8 |
| Limpiar la cocina | 7 |
| Hacer las compras | 8 |
| Cortar el pasto | 15 |

---

## 9. Estados de una tarea

Una tarea podrá encontrarse al menos en los siguientes estados:

- Pendiente.
- En curso.
- Completada.

Cuando una tarea sea completada deberá quedar registrado:

- Quién la realizó.
- Cuándo la realizó.
- Cuántos puntos obtuvo.

---

# 10. Sistema de puntos

Cada tarea tendrá asociada una determinada cantidad de puntos.

Cuando un miembro complete una tarea recibirá los puntos correspondientes.

Ejemplo:

Pablo realiza:

- Lavar platos: 5 puntos.
- Sacar basura: 3 puntos.
- Limpiar baño: 10 puntos.

Total obtenido:

**18 puntos**

Los puntos deberán quedar acumulados dentro de la casa.

---

## 11. Ranking de miembros

La casa deberá contar con un ranking que muestre los puntos obtenidos por cada miembro.

Ejemplo:

| Posición | Miembro | Puntos |
|---:|---|---:|
| 1 | Ana | 135 |
| 2 | Pablo | 110 |
| 3 | Matías | 95 |
| 4 | Laura | 80 |

El ranking permitirá visualizar quién está participando más activamente en las tareas domésticas.

---

# 12. Historial de tareas

La aplicación deberá mantener un historial de las tareas realizadas.

Cada registro deberá indicar:

- Tarea.
- Persona que la realizó.
- Fecha.
- Puntos obtenidos.

Ejemplo:

| Fecha | Miembro | Tarea | Puntos |
|---|---|---|---:|
| 10/09 | Pablo | Limpiar baño | 10 |
| 10/09 | Ana | Cocinar | 8 |
| 11/09 | Pablo | Sacar basura | 3 |

---

# 13. Tareas recurrentes

Algunas tareas domésticas podrán repetirse periódicamente.

Ejemplos:

- Sacar la basura todos los días.
- Limpiar el baño una vez por semana.
- Hacer las compras una vez por semana.
- Cortar el pasto cada quince días.

La aplicación deberá permitir definir tareas que vuelvan a quedar disponibles después de completarse.

---

# 14. Asignación de tareas

Una tarea podrá:

- Estar asignada a un miembro específico.
- Estar disponible para cualquier miembro.

En el segundo caso, cualquier integrante de la casa podrá realizarla y obtener los puntos correspondientes.

---

# 15. Vista general de la casa

Cada casa deberá tener una pantalla principal donde puedan visualizarse rápidamente:

- Miembros.
- Gastos recientes.
- Balance económico.
- Tareas pendientes.
- Tareas recientemente completadas.
- Ranking de puntos.

El objetivo será permitir conocer rápidamente el estado general de la casa.

---

# 16. Historial de actividad

La aplicación deberá mantener un historial general de las acciones relevantes.

Ejemplos:

- Pablo registró un gasto de $25.000.
- Ana completó "Limpiar cocina".
- Ana obtuvo 7 puntos.
- Pablo creó la tarea "Comprar alimento para el perro".
- Laura fue agregada a la casa.

---

# 17. Roles

Inicialmente existirán dos tipos de participantes.

## Administrador

Podrá:

- Modificar información de la casa.
- Agregar miembros.
- Eliminar o desactivar miembros.
- Crear tareas.
- Modificar tareas.
- Gestionar categorías.
- Consultar todos los gastos.
- Consultar el ranking.

## Miembro

Podrá:

- Consultar la casa.
- Registrar gastos.
- Consultar balances.
- Realizar tareas.
- Marcar tareas como completadas.
- Consultar sus puntos.
- Consultar el ranking.

---

# 18. Reglas funcionales principales

1. Toda persona deberá pertenecer a una casa para registrar gastos o tareas.

2. Todo gasto deberá indicar quién realizó el pago.

3. Todo gasto deberá indicar qué miembros participan del mismo.

4. Una tarea completada deberá quedar asociada a la persona que la realizó.

5. Los puntos solamente deberán otorgarse cuando una tarea sea completada.

6. Una tarea no deberá entregar puntos más de una vez por cada realización.

7. Los puntos obtenidos deberán mantenerse en el historial.

8. La eliminación de un miembro no deberá eliminar su actividad histórica.

9. Los gastos históricos no deberán modificarse automáticamente cuando se agreguen nuevos miembros a la casa.

10. Cada casa deberá mantener su información independiente de otras casas.

---

# 19. Ejemplo de uso

Pablo crea una casa llamada:

**Casa Brown**

Luego agrega a:

- Ana.
- Juan.
- Laura.

Durante la semana se registran los siguientes gastos:

Pablo paga supermercado por $80.000.

Ana paga internet por $25.000.

Juan paga productos de limpieza por $15.000.

La aplicación muestra automáticamente cuánto pagó cada persona y cuál es el balance entre ellos.

Al mismo tiempo existen las siguientes tareas:

- Lavar platos — 5 puntos.
- Limpiar baño — 10 puntos.
- Sacar basura — 3 puntos.
- Cocinar — 8 puntos.

Durante el día:

Ana cocina y obtiene 8 puntos.

Pablo limpia el baño y obtiene 10 puntos.

Juan saca la basura y obtiene 3 puntos.

El ranking queda:

1. Pablo — 10 puntos.
2. Ana — 8 puntos.
3. Juan — 3 puntos.
4. Laura — 0 puntos.

A medida que los miembros realizan tareas, el ranking se actualiza.

---

# 20. Alcance inicial

Para una primera versión de la aplicación se considera suficiente disponer de:

- Creación de casas.
- Gestión de miembros.
- Registro de gastos.
- División de gastos entre miembros.
- Balance económico.
- Creación de tareas.
- Asignación de tareas.
- Finalización de tareas.
- Sistema de puntos.
- Ranking.
- Historial de gastos.
- Historial de tareas.

---

# 21. Funcionalidades futuras posibles

Fuera del alcance inicial podrían incorporarse posteriormente:

- Premios asociados a puntos.
- Penalizaciones.
- Objetivos semanales.
- Notificaciones.
- Recordatorios de tareas.
- Presupuestos mensuales.
- Límites de gastos.
- Estadísticas de gastos.
- Estadísticas de participación.
- Fotos o comprobantes de gastos.
- Calendario doméstico.
- Listas de compras.
- Votaciones entre los miembros.
- División configurable de gastos.
- Puntos extra por determinadas tareas.
- Desafíos semanales entre miembros.

---

# 22. Resultado esperado

La aplicación deberá ofrecer una forma sencilla de responder cuatro preguntas principales dentro de una casa:

**¿Qué gastos tuvimos?**

**¿Quién pagó cada gasto y quién debe dinero?**

**¿Qué tareas hay pendientes y quién las realizó?**

**¿Cómo se está distribuyendo el trabajo doméstico entre los miembros?**

El sistema de puntos deberá complementar estas funciones permitiendo visualizar y reconocer la participación de cada integrante en las tareas de la casa.