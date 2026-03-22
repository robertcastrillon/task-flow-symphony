import type { TaskFilters, TaskStatus, TaskPriority } from "../types";
import { useUsers } from "../hooks/useUsers";

interface FilterBarProps {
  filters: TaskFilters;
  onChange: (filters: TaskFilters) => void;
}

export default function FilterBar({ filters, onChange }: FilterBarProps) {
  const { data: users } = useUsers();

  function handleChange(key: keyof TaskFilters, value: string) {
    onChange({ ...filters, [key]: value || undefined, page: 1 });
  }

  return (
    <div className="flex flex-wrap gap-3 items-center" role="search">
      <input
        type="text"
        placeholder="Buscar tareas..."
        className="input input-bordered input-sm w-48"
        value={filters.search ?? ""}
        onChange={(e) => handleChange("search", e.target.value)}
      />

      <select
        className="select select-bordered select-sm"
        value={filters.status ?? ""}
        onChange={(e) => handleChange("status", e.target.value)}
        aria-label="Filtrar por estado"
      >
        <option value="">Todos los estados</option>
        <option value={"todo" satisfies TaskStatus}>Por hacer</option>
        <option value={"in_progress" satisfies TaskStatus}>En progreso</option>
        <option value={"done" satisfies TaskStatus}>Hecho</option>
        <option value={"cancelled" satisfies TaskStatus}>Cancelado</option>
      </select>

      <select
        className="select select-bordered select-sm"
        value={filters.priority ?? ""}
        onChange={(e) => handleChange("priority", e.target.value)}
        aria-label="Filtrar por prioridad"
      >
        <option value="">Todas las prioridades</option>
        <option value={"low" satisfies TaskPriority}>Baja</option>
        <option value={"medium" satisfies TaskPriority}>Media</option>
        <option value={"high" satisfies TaskPriority}>Alta</option>
        <option value={"urgent" satisfies TaskPriority}>Urgente</option>
      </select>

      <select
        className="select select-bordered select-sm"
        value={filters.assignee ?? ""}
        onChange={(e) => handleChange("assignee", e.target.value)}
        aria-label="Filtrar por asignado"
      >
        <option value="">Todos los miembros</option>
        {users?.map((user) => (
          <option key={user.id} value={user.id}>
            {user.name}
          </option>
        ))}
      </select>
    </div>
  );
}
