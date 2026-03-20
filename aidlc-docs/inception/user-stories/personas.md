# Personas — TaskFlow

## Persona 1: Visitante (Unauthenticated Visitor)

- **Nombre**: Carlos — Visitante
- **Rol**: Usuario no autenticado que accede a la aplicación por primera vez o sin sesión activa
- **Objetivos**:
  - Registrarse para crear una cuenta en el equipo
  - Iniciar sesión para acceder a sus tareas y equipo
- **Motivaciones**: Incorporarse rápidamente al equipo y comenzar a gestionar tareas
- **Frustraciones**: Formularios confusos, mensajes de error poco claros, procesos de registro lentos
- **Contexto de uso**: Accede desde navegador web, puede ser invitado por un miembro existente del equipo

---

## Persona 2: Miembro (Team Member)

- **Nombre**: María — Miembro del equipo
- **Rol**: `member` — Miembro activo del equipo que gestiona sus tareas diarias
- **Objetivos**:
  - Crear y organizar sus tareas
  - Mover tareas entre estados (Todo, In Progress, Done)
  - Ver tareas asignadas y filtrar por prioridad, estado, tags
  - Comentar en tareas para colaborar con el equipo
  - Ver el dashboard con resumen de actividad
  - Actualizar su perfil
- **Motivaciones**: Productividad personal, visibilidad del progreso, colaboración efectiva con el equipo
- **Frustraciones**: Perder de vista tareas urgentes, no saber qué está pendiente, falta de contexto en tareas
- **Contexto de uso**: Uso diario desde navegador, gestiona entre 5-20 tareas activas, interactúa frecuentemente con el board Kanban

---

## Persona 3: Administrador (Admin)

- **Nombre**: Luis — Administrador del equipo
- **Rol**: `admin` — Administrador con permisos extendidos sobre el equipo
- **Objetivos**:
  - Todo lo que puede hacer un Miembro
  - Gestionar miembros del equipo (ver roles, gestionar acceso)
  - Asignar tareas a cualquier miembro del equipo
  - Supervisar el progreso general del equipo desde el dashboard
  - Acceder a estadísticas globales (tareas por usuario, tareas vencidas)
- **Motivaciones**: Visibilidad completa del equipo, distribución eficiente del trabajo, detección temprana de bloqueos
- **Frustraciones**: No tener visibilidad del estado de tareas del equipo, dificultad para reasignar trabajo, tareas vencidas sin detectar
- **Contexto de uso**: Revisa el dashboard frecuentemente, asigna y reasigna tareas, supervisa el board Kanban del equipo

---

## Matriz Persona-Funcionalidad

| Funcionalidad | Visitante | Miembro | Admin |
|---|---|---|---|
| Registro | x | | |
| Login | x | | |
| Ver Dashboard | | x | x |
| Crear Tareas | | x | x |
| Ver/Filtrar Tareas | | x | x |
| Kanban Board (drag & drop) | | x | x |
| Detalle de Tarea | | x | x |
| Asignar Tarea a sí mismo | | x | x |
| Asignar Tarea a otros | | | x |
| Eliminar Tarea (propia) | | x | x |
| Eliminar Tarea (de otros) | | | x |
| Comentar en Tareas | | x | x |
| Ver Equipo | | x | x |
| Gestionar Equipo (roles) | | | x |
| Actualizar Perfil Propio | | x | x |
