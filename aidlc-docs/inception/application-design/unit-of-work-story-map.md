# Unit of Work — Story Map

## Unit 1: Project Setup & Infrastructure
| Story | Description |
|---|---|
| — | No user stories (infrastructure only) |

**Note**: Unit 1 is foundational infrastructure. No user-facing stories apply.

---

## Unit 2: Backend — Auth Module
| Story | Description |
|---|---|
| US-A01 | Registro de usuario (backend) |
| US-A02 | Inicio de sesión (backend) |
| US-A03 | Ver perfil actual (backend) |
| US-A04 | Renovación de token JWT (backend) |
| US-A05 | Cerrar sesión (backend) |
| US-F01 | Autorización basada en roles (backend — auth infrastructure) |

---

## Unit 3: Backend — Tasks & Users Module
| Story | Description |
|---|---|
| US-B01 | Crear tarea (backend) |
| US-B02 | Ver lista de tareas con filtros (backend) |
| US-B05 | Ver detalle de tarea (backend) |
| US-B06 | Editar tarea (backend) |
| US-B07 | Cambiar estado de tarea via API (backend) |
| US-B08 | Asignar tarea a un usuario (backend) |
| US-B09 | Eliminar tarea — soft delete (backend) |
| US-E01 | Ver miembros del equipo (backend) |
| US-E02 | Ver detalle de un miembro (backend) |
| US-E03 | Actualizar perfil propio (backend) |
| US-F01 | Autorización basada en roles (backend — task/user permissions) |

---

## Unit 4: Backend — Comments & Dashboard Module
| Story | Description |
|---|---|
| US-C01 | Ver comentarios de una tarea (backend) |
| US-C02 | Agregar comentario a una tarea (backend) |
| US-D01 | Ver estadísticas del dashboard (backend) |

---

## Unit 5: Frontend Web
| Story | Description |
|---|---|
| US-A01 | Registro de usuario (frontend) |
| US-A02 | Inicio de sesión (frontend) |
| US-A03 | Ver perfil actual (frontend) |
| US-A05 | Cerrar sesión (frontend) |
| US-B01 | Crear tarea (frontend) |
| US-B02 | Ver lista de tareas con filtros (frontend) |
| US-B03 | Ver tablero Kanban (frontend) |
| US-B04 | Mover tarea en el Kanban — drag & drop (frontend) |
| US-B05 | Ver detalle de tarea (frontend) |
| US-B06 | Editar tarea (frontend) |
| US-B08 | Asignar tarea a un usuario (frontend) |
| US-B09 | Eliminar tarea (frontend) |
| US-C01 | Ver comentarios de una tarea (frontend) |
| US-C02 | Agregar comentario a una tarea (frontend) |
| US-D01 | Ver estadísticas del dashboard (frontend) |
| US-E01 | Ver miembros del equipo (frontend) |
| US-E03 | Actualizar perfil propio (frontend) |
| US-F01 | Autorización basada en roles (frontend — route guards, UI) |

---

## Unit 6: Integration & GCP Deployment
| Story | Description |
|---|---|
| — | No user stories (deployment/infrastructure only) |

---

## Story Coverage Verification

| Story | Unit(s) | Covered |
|---|---|---|
| US-A01 | Unit 2 (BE), Unit 5 (FE) | Yes |
| US-A02 | Unit 2 (BE), Unit 5 (FE) | Yes |
| US-A03 | Unit 2 (BE), Unit 5 (FE) | Yes |
| US-A04 | Unit 2 (BE) | Yes |
| US-A05 | Unit 2 (BE), Unit 5 (FE) | Yes |
| US-B01 | Unit 3 (BE), Unit 5 (FE) | Yes |
| US-B02 | Unit 3 (BE), Unit 5 (FE) | Yes |
| US-B03 | Unit 5 (FE) | Yes |
| US-B04 | Unit 5 (FE) | Yes |
| US-B05 | Unit 3 (BE), Unit 5 (FE) | Yes |
| US-B06 | Unit 3 (BE), Unit 5 (FE) | Yes |
| US-B07 | Unit 3 (BE) | Yes |
| US-B08 | Unit 3 (BE), Unit 5 (FE) | Yes |
| US-B09 | Unit 3 (BE), Unit 5 (FE) | Yes |
| US-C01 | Unit 4 (BE), Unit 5 (FE) | Yes |
| US-C02 | Unit 4 (BE), Unit 5 (FE) | Yes |
| US-D01 | Unit 4 (BE), Unit 5 (FE) | Yes |
| US-E01 | Unit 3 (BE), Unit 5 (FE) | Yes |
| US-E02 | Unit 3 (BE) | Yes |
| US-E03 | Unit 3 (BE), Unit 5 (FE) | Yes |
| US-F01 | Unit 2 (BE), Unit 3 (BE), Unit 5 (FE) | Yes |

**All 21 stories are mapped to at least one unit.**
