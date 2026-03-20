# User Stories — TaskFlow (Phase 1)

---

## Epic A: Autenticación

### US-A01: Registro de usuario
**Como** Visitante, **quiero** registrarme con mi email y contraseña **para** crear una cuenta y unirme al equipo.

**Criterios de aceptación:**
```gherkin
Scenario: Registro exitoso
  Given estoy en la página de registro
  When ingreso un email válido "carlos@team.com", nombre "Carlos" y contraseña "Segura123!"
  And la contraseña tiene al menos 8 caracteres
  Then se crea mi cuenta con rol "member"
  And soy redirigido a la página de login con mensaje de confirmación

Scenario: Registro con email duplicado
  Given existe un usuario con email "carlos@team.com"
  When intento registrarme con el mismo email
  Then veo un mensaje de error "El email ya está registrado"
  And no se crea una cuenta duplicada

Scenario: Registro con contraseña débil
  Given estoy en la página de registro
  When ingreso una contraseña con menos de 8 caracteres
  Then veo un mensaje de error indicando los requisitos de contraseña
  And el formulario no se envía

Scenario: Registro con email inválido
  Given estoy en la página de registro
  When ingreso un email con formato inválido (e.g., "carlos@", "carlos.com")
  Then veo un mensaje de error "Formato de email inválido"
  And el formulario no se envía

Scenario: Registro con campos vacíos
  Given estoy en la página de registro
  When intento enviar el formulario con campos obligatorios vacíos
  Then veo mensajes de validación en cada campo requerido
```

**Persona**: Visitante

---

### US-A02: Inicio de sesión
**Como** Visitante, **quiero** iniciar sesión con mi email y contraseña **para** acceder a mis tareas y al equipo.

**Criterios de aceptación:**
```gherkin
Scenario: Login exitoso
  Given tengo una cuenta registrada con email "maria@team.com"
  When ingreso mi email y contraseña correctos
  Then recibo un token JWT válido por 24 horas y un refresh token
  And soy redirigido al Dashboard

Scenario: Login con credenciales incorrectas
  Given tengo una cuenta registrada
  When ingreso una contraseña incorrecta
  Then veo un mensaje de error "Credenciales inválidas"
  And no se genera ningún token

Scenario: Login con email no registrado
  Given no existe una cuenta con email "desconocido@team.com"
  When intento hacer login con ese email
  Then veo un mensaje de error "Credenciales inválidas"
  And el mensaje no revela si el email existe o no

Scenario: Rate limiting en login
  Given he intentado hacer login 5 veces en el último minuto
  When intento un 6to login
  Then recibo un error 429 "Demasiados intentos, intente de nuevo más tarde"

Scenario: Login con cuenta inactiva
  Given mi cuenta está marcada como is_active = false
  When intento hacer login
  Then veo un mensaje de error "Cuenta desactivada"
```

**Persona**: Visitante

---

### US-A03: Ver perfil actual
**Como** Miembro, **quiero** ver mi perfil actual **para** confirmar que estoy autenticado con la cuenta correcta.

**Criterios de aceptación:**
```gherkin
Scenario: Ver perfil autenticado
  Given estoy autenticado como "maria@team.com"
  When accedo a mi perfil (GET /api/v1/auth/me)
  Then veo mi nombre, email, rol y avatar
  And no veo campos sensibles como hash de contraseña

Scenario: Acceso sin autenticación
  Given no tengo un token JWT válido
  When intento acceder a mi perfil
  Then recibo un error 401 "No autenticado"
```

**Persona**: Miembro, Admin

---

### US-A04: Renovación de token JWT
**Como** Miembro, **quiero** que mi sesión se renueve automáticamente **para** no tener que volver a iniciar sesión cada 24 horas si sigo activo.

**Criterios de aceptación:**
```gherkin
Scenario: Refresh token válido
  Given mi token JWT ha expirado
  And tengo un refresh token válido
  When solicito un nuevo token
  Then recibo un nuevo JWT válido por 24 horas

Scenario: Refresh token expirado
  Given mi refresh token ha expirado
  When solicito un nuevo token
  Then recibo un error 401
  And soy redirigido al login
```

**Persona**: Miembro, Admin

---

### US-A05: Cerrar sesión
**Como** Miembro, **quiero** cerrar mi sesión **para** proteger mi cuenta cuando dejo de usar la aplicación.

**Criterios de aceptación:**
```gherkin
Scenario: Logout exitoso
  Given estoy autenticado
  When cierro mi sesión
  Then mi token se invalida en el cliente
  And soy redirigido a la página de login

Scenario: Acceso post-logout
  Given he cerrado sesión
  When intento acceder a una ruta protegida
  Then soy redirigido al login
```

**Persona**: Miembro, Admin

---

## Epic B: Gestión de Tareas

### US-B01: Crear tarea
**Como** Miembro, **quiero** crear una nueva tarea **para** registrar trabajo pendiente del equipo.

**Criterios de aceptación:**
```gherkin
Scenario: Crear tarea con campos obligatorios
  Given estoy autenticado como miembro del equipo
  When creo una tarea con título "Diseñar landing page"
  Then la tarea se crea con estado "todo" y prioridad "medium" por defecto
  And mi usuario queda como creador (created_by)
  And la tarea aparece en la columna "Todo" del board

Scenario: Crear tarea con todos los campos
  Given estoy autenticado
  When creo una tarea con título, descripción, prioridad "high", fecha de vencimiento y tags ["diseño", "frontend"]
  Then la tarea se crea con todos los campos especificados
  And la tarea aparece en el board con indicador de prioridad alta

Scenario: Crear tarea sin título
  Given estoy autenticado
  When intento crear una tarea sin título
  Then recibo un error de validación "El título es obligatorio"
  And la tarea no se crea

Scenario: Crear tarea con título excesivamente largo
  Given estoy autenticado
  When intento crear una tarea con título de más de 255 caracteres
  Then recibo un error de validación "El título no puede superar 255 caracteres"
```

**Persona**: Miembro, Admin

---

### US-B02: Ver lista de tareas con filtros
**Como** Miembro, **quiero** ver las tareas en formato tabla con filtros **para** encontrar rápidamente las tareas que me interesan.

**Criterios de aceptación:**
```gherkin
Scenario: Ver lista de tareas paginada
  Given existen 60 tareas en el sistema
  When accedo a la lista de tareas sin filtros
  Then veo las primeras 50 tareas
  And hay indicador de paginación para ver las siguientes

Scenario: Filtrar por estado
  Given existen tareas con diferentes estados
  When filtro por estado "in_progress"
  Then solo veo las tareas con estado "in_progress"

Scenario: Filtrar por prioridad
  Given existen tareas con prioridades variadas
  When filtro por prioridad "urgent"
  Then solo veo las tareas marcadas como urgentes

Scenario: Filtrar por asignado
  Given existen tareas asignadas a diferentes usuarios
  When filtro por assignee "maria@team.com"
  Then solo veo las tareas asignadas a María

Scenario: Filtrar por tag
  Given existen tareas con diferentes tags
  When filtro por tag "frontend"
  Then solo veo las tareas que contienen el tag "frontend"

Scenario: Búsqueda por texto
  Given existen tareas con diferentes títulos
  When busco "landing"
  Then veo las tareas cuyo título contiene "landing"

Scenario: Combinación de filtros
  Given existen tareas variadas
  When filtro por estado "todo" y prioridad "high"
  Then solo veo tareas que cumplen ambos criterios

Scenario: Sin resultados
  Given existen tareas en el sistema
  When aplico filtros que no coinciden con ninguna tarea
  Then veo un mensaje "No se encontraron tareas con los filtros seleccionados"

Scenario: Ordenar tareas
  Given existen múltiples tareas
  When ordeno por fecha de vencimiento ascendente
  Then las tareas se muestran ordenadas por due_date de más próxima a más lejana
```

**Persona**: Miembro, Admin

---

### US-B03: Ver tablero Kanban
**Como** Miembro, **quiero** ver mis tareas en un tablero Kanban **para** tener una vista visual del progreso del equipo.

**Criterios de aceptación:**
```gherkin
Scenario: Ver tablero con columnas
  Given existen tareas con diferentes estados
  When accedo al tablero Kanban
  Then veo tres columnas: "Todo", "In Progress", "Done"
  And cada tarea aparece en su columna correspondiente

Scenario: Visualización de TaskCard
  Given existe una tarea con título, prioridad "high", asignada a María, con fecha de vencimiento
  When veo la tarea en el board
  Then la tarjeta muestra título, indicador de prioridad (color), avatar de María y fecha de vencimiento

Scenario: Tarea vencida en el board
  Given existe una tarea con due_date en el pasado y estado "todo"
  When veo la tarea en el board
  Then la tarjeta muestra un indicador visual de tarea vencida
```

**Persona**: Miembro, Admin

---

### US-B04: Mover tarea en el Kanban (drag & drop)
**Como** Miembro, **quiero** arrastrar tareas entre columnas del Kanban **para** cambiar su estado de forma rápida e intuitiva.

**Criterios de aceptación:**
```gherkin
Scenario: Mover tarea de Todo a In Progress
  Given existe la tarea "Diseñar landing page" en la columna "Todo"
  When arrastro la tarea a la columna "In Progress"
  Then el estado de la tarea se actualiza a "in_progress" via API
  And la fecha updated_at se actualiza
  And la tarea aparece visualmente en la nueva columna

Scenario: Mover tarea a Done
  Given existe una tarea en "In Progress"
  When arrastro la tarea a la columna "Done"
  Then el estado cambia a "done"
  And completed_at se establece con la fecha/hora actual

Scenario: Mover tarea de Done a Todo
  Given existe una tarea en "Done"
  When arrastro la tarea de vuelta a "Todo"
  Then el estado cambia a "todo"
  And completed_at se establece como null

Scenario: Error al mover tarea (sin conexión)
  Given estoy viendo el Kanban board
  When arrastro una tarea pero la API falla
  Then la tarea vuelve a su posición original
  And veo un mensaje de error "No se pudo actualizar el estado"
```

**Persona**: Miembro, Admin

---

### US-B05: Ver detalle de tarea
**Como** Miembro, **quiero** ver el detalle completo de una tarea **para** entender su contexto, descripción y actividad.

**Criterios de aceptación:**
```gherkin
Scenario: Ver detalle completo
  Given existe la tarea "Diseñar landing page" con descripción, prioridad, asignado, tags y comentarios
  When abro el detalle de la tarea
  Then veo título, descripción, estado, prioridad, fecha de vencimiento
  And veo el creador, el asignado (con avatar) y los tags
  And veo la lista de comentarios
  And veo las fechas de creación y última actualización

Scenario: Tarea sin descripción
  Given existe una tarea sin descripción
  When abro el detalle
  Then veo un placeholder "Sin descripción" o campo vacío

Scenario: Acceder a tarea inexistente
  Given no existe una tarea con el ID proporcionado
  When intento ver su detalle
  Then veo un error 404 "Tarea no encontrada"
```

**Persona**: Miembro, Admin

---

### US-B06: Editar tarea
**Como** Miembro, **quiero** editar los datos de una tarea **para** actualizar su información a medida que avanza el trabajo.

**Criterios de aceptación:**
```gherkin
Scenario: Editar título y descripción
  Given estoy viendo el detalle de una tarea que creé
  When edito el título a "Diseñar landing page v2" y agrego descripción
  Then los cambios se guardan via PATCH /api/v1/tasks/{id}
  And updated_at se actualiza

Scenario: Cambiar prioridad
  Given existe una tarea con prioridad "medium"
  When cambio la prioridad a "urgent"
  Then la prioridad se actualiza
  And el indicador visual de prioridad cambia en el board y la lista

Scenario: Editar fecha de vencimiento
  Given existe una tarea sin fecha de vencimiento
  When agrego una fecha de vencimiento
  Then la fecha se guarda y se muestra en la tarjeta del board

Scenario: Editar tags
  Given existe una tarea con tags ["diseño"]
  When agrego el tag "urgente" y elimino "diseño"
  Then los tags se actualizan a ["urgente"]
```

**Persona**: Miembro, Admin

---

### US-B07: Cambiar estado de tarea via API
**Como** Miembro, **quiero** cambiar el estado de una tarea directamente **para** actualizarlo sin usar drag & drop.

**Criterios de aceptación:**
```gherkin
Scenario: Cambiar estado válido
  Given existe una tarea con estado "todo"
  When cambio el estado a "in_progress" via PATCH /api/v1/tasks/{id}/status
  Then el estado se actualiza a "in_progress"
  And updated_at se actualiza

Scenario: Marcar como completada
  Given existe una tarea con estado "in_progress"
  When cambio el estado a "done"
  Then completed_at se establece con la fecha/hora actual

Scenario: Cambiar a estado inválido
  Given existe una tarea
  When intento cambiar el estado a un valor no permitido (e.g., "deleted")
  Then recibo un error de validación "Estado inválido"
```

**Persona**: Miembro, Admin

---

### US-B08: Asignar tarea a un usuario
**Como** Miembro, **quiero** asignar una tarea a un miembro del equipo **para** que sepa que tiene trabajo pendiente.

**Criterios de aceptación:**
```gherkin
Scenario: Asignar tarea a otro miembro
  Given soy Admin y existe la tarea "Diseñar landing page" sin asignar
  When asigno la tarea a "maria@team.com"
  Then la tarea muestra el avatar de María
  And María puede ver la tarea al filtrar por "mis tareas"

Scenario: Reasignar tarea
  Given la tarea está asignada a María
  When la reasigno a "carlos@team.com"
  Then la tarea ahora muestra el avatar de Carlos

Scenario: Desasignar tarea
  Given la tarea está asignada a María
  When quito la asignación (assigned_to = null)
  Then la tarea aparece sin asignado

Scenario: Asignar a usuario inexistente
  Given intento asignar la tarea a un ID de usuario que no existe
  When envío la solicitud
  Then recibo un error 404 "Usuario no encontrado"

Scenario: Miembro asigna tarea a sí mismo
  Given soy Miembro y existe una tarea sin asignar
  When me asigno la tarea a mí mismo
  Then la tarea se asigna correctamente a mi usuario
```

**Persona**: Miembro (auto-asignación), Admin (asignar a cualquiera)

---

### US-B09: Eliminar tarea (soft delete)
**Como** Admin, **quiero** eliminar una tarea **para** limpiar tareas obsoletas o creadas por error.

**Criterios de aceptación:**
```gherkin
Scenario: Soft delete exitoso
  Given soy Admin y existe la tarea "Tarea obsoleta"
  When elimino la tarea via DELETE /api/v1/tasks/{id}
  Then la tarea ya no aparece en el board ni en la lista
  And la tarea sigue existiendo en la base de datos (soft delete)

Scenario: Eliminar tarea inexistente
  Given no existe una tarea con el ID proporcionado
  When intento eliminarla
  Then recibo un error 404 "Tarea no encontrada"

Scenario: Miembro elimina su propia tarea
  Given soy Miembro y creé la tarea "Mi tarea"
  When intento eliminar mi tarea
  Then la tarea se elimina correctamente (soft delete)

Scenario: Miembro intenta eliminar tarea de otro
  Given soy Miembro y la tarea fue creada por otro usuario
  When intento eliminarla
  Then recibo un error 403 "No tienes permisos para eliminar esta tarea"
```

**Persona**: Admin, Miembro (solo propias)

---

## Epic C: Comentarios

### US-C01: Ver comentarios de una tarea
**Como** Miembro, **quiero** ver los comentarios de una tarea **para** entender las discusiones y decisiones del equipo.

**Criterios de aceptación:**
```gherkin
Scenario: Ver lista de comentarios
  Given la tarea "Diseñar landing page" tiene 3 comentarios
  When abro el detalle de la tarea
  Then veo los 3 comentarios ordenados cronológicamente
  And cada comentario muestra autor (nombre + avatar), contenido, fecha

Scenario: Tarea sin comentarios
  Given la tarea no tiene comentarios
  When abro el detalle
  Then veo un mensaje "No hay comentarios aún"
  And veo el formulario para agregar uno
```

**Persona**: Miembro, Admin

---

### US-C02: Agregar comentario a una tarea
**Como** Miembro, **quiero** agregar un comentario a una tarea **para** comunicar actualizaciones o hacer preguntas al equipo.

**Criterios de aceptación:**
```gherkin
Scenario: Agregar comentario exitoso
  Given estoy viendo el detalle de la tarea "Diseñar landing page"
  When escribo "¿Usamos los colores de la marca?" y envío
  Then el comentario aparece en la lista con mi nombre, avatar y fecha actual
  And el formulario se limpia

Scenario: Comentario vacío
  Given estoy en el formulario de comentario
  When intento enviar un comentario vacío
  Then veo un error de validación "El comentario no puede estar vacío"
  And el comentario no se envía

Scenario: Comentar en tarea inexistente
  Given intento comentar en una tarea con ID que no existe
  When envío el comentario
  Then recibo un error 404 "Tarea no encontrada"
```

**Persona**: Miembro, Admin

---

## Epic D: Dashboard

### US-D01: Ver estadísticas del dashboard
**Como** Miembro, **quiero** ver un resumen visual de las tareas **para** entender el estado general del trabajo del equipo.

**Criterios de aceptación:**
```gherkin
Scenario: Dashboard muestra métricas correctas
  Given existen 10 tareas: 3 todo, 5 in_progress, 2 done
  When accedo al dashboard
  Then veo StatCards con: Total (10), Todo (3), In Progress (5), Done (2)

Scenario: Dashboard muestra tareas vencidas
  Given existen 2 tareas con due_date en el pasado y estado != "done"
  When accedo al dashboard
  Then veo un indicador de "2 tareas vencidas" resaltado visualmente

Scenario: Dashboard muestra tareas por usuario
  Given existen tareas asignadas a diferentes usuarios
  When accedo al dashboard
  Then veo un resumen de tareas por usuario/asignado

Scenario: Dashboard sin tareas
  Given no existen tareas en el sistema
  When accedo al dashboard
  Then veo todas las métricas en 0
  And veo un mensaje sugerente "No hay tareas. ¡Crea la primera!"
```

**Persona**: Miembro, Admin

---

## Epic E: Gestión de Equipo

### US-E01: Ver miembros del equipo
**Como** Miembro, **quiero** ver la lista de miembros del equipo **para** saber quiénes forman parte y sus roles.

**Criterios de aceptación:**
```gherkin
Scenario: Ver lista de miembros
  Given existen 5 usuarios activos en el sistema
  When accedo a la página de Equipo
  Then veo los 5 miembros con nombre, email, avatar y rol

Scenario: Distinguir roles
  Given existen usuarios con roles "admin" y "member"
  When veo la lista del equipo
  Then los roles están visualmente diferenciados (badge/etiqueta)

Scenario: Usuarios inactivos
  Given existe un usuario con is_active = false
  When veo la lista del equipo
  Then el usuario inactivo no aparece en la lista (o aparece diferenciado)
```

**Persona**: Miembro, Admin

---

### US-E02: Ver detalle de un miembro
**Como** Miembro, **quiero** ver el perfil de un compañero **para** conocer su información y tareas asignadas.

**Criterios de aceptación:**
```gherkin
Scenario: Ver perfil de miembro
  Given existe el usuario "Maria" con rol "member"
  When accedo a su perfil via GET /api/v1/users/{id}
  Then veo su nombre, email, avatar, rol y fecha de registro

Scenario: Perfil de usuario inexistente
  Given no existe un usuario con el ID proporcionado
  When intento ver su perfil
  Then recibo un error 404 "Usuario no encontrado"
```

**Persona**: Miembro, Admin

---

### US-E03: Actualizar perfil propio
**Como** Miembro, **quiero** actualizar mi nombre y avatar **para** mantener mi perfil actualizado.

**Criterios de aceptación:**
```gherkin
Scenario: Actualizar nombre
  Given estoy autenticado como "maria@team.com"
  When actualizo mi nombre a "María García"
  Then mi nombre se actualiza en el sistema
  And mi nombre actualizado aparece en mis comentarios y tarjetas

Scenario: Actualizar avatar
  Given estoy autenticado
  When actualizo mi avatar_url
  Then el nuevo avatar aparece en mi perfil y en las TaskCards

Scenario: Intentar cambiar email
  Given estoy autenticado
  When intento cambiar mi email
  Then el campo email no es editable / recibo un error

Scenario: Intentar cambiar rol propio
  Given soy Miembro
  When intento cambiar mi rol a "admin"
  Then recibo un error 403 "No tienes permisos para cambiar roles"
```

**Persona**: Miembro, Admin

---

## Epic F: Autorización y Control de Acceso

### US-F01: Autorización basada en roles
**Como** Admin, **quiero** que el sistema aplique permisos según el rol **para** proteger operaciones sensibles.

**Criterios de aceptación:**
```gherkin
Scenario: Admin accede a operaciones de gestión
  Given estoy autenticado como Admin
  When accedo a gestión de equipo, asignación libre de tareas, eliminación de cualquier tarea
  Then todas las operaciones se ejecutan correctamente

Scenario: Miembro intenta operación de Admin
  Given estoy autenticado como Miembro
  When intento asignar una tarea a otro usuario (que no soy yo)
  Then recibo un error 403 "Permisos insuficientes"

Scenario: Token expirado en cualquier endpoint
  Given mi token JWT ha expirado
  When intento acceder a cualquier endpoint protegido
  Then recibo un error 401 "Token expirado"
  And soy redirigido al login

Scenario: Token manipulado
  Given envío un token JWT con firma inválida
  When intento acceder a un endpoint protegido
  Then recibo un error 401 "Token inválido"

Scenario: Autorización a nivel de objeto (IDOR prevention)
  Given soy Miembro y existe una tarea creada por otro usuario
  When intento eliminar esa tarea via API directamente
  Then recibo un error 403
  And la tarea no se elimina
```

**Persona**: Admin, Miembro

---

## Resumen de Stories

| Epic | Stories | Persona Principal |
|---|---|---|
| A: Autenticación | US-A01 a US-A05 (5 stories) | Visitante, Miembro |
| B: Gestión de Tareas | US-B01 a US-B09 (9 stories) | Miembro, Admin |
| C: Comentarios | US-C01 a US-C02 (2 stories) | Miembro |
| D: Dashboard | US-D01 (1 story) | Miembro, Admin |
| E: Gestión de Equipo | US-E01 a US-E03 (3 stories) | Miembro, Admin |
| F: Autorización | US-F01 (1 story) | Admin, Miembro |
| **Total** | **21 stories** | |
