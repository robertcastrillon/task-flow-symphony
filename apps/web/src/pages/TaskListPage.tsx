import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTaskList } from "../hooks/useTasks";
import FilterBar from "../components/FilterBar";
import type { TaskFilters } from "../types";

const priorityColors: Record<string, string> = {
  low: "badge-info",
  medium: "badge-warning",
  high: "badge-error",
  urgent: "badge-error badge-outline",
};

export default function TaskListPage() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState<TaskFilters>({ page: 1 });
  const { data, isLoading } = useTaskList(filters);

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Lista de tareas</h1>
      </div>

      <div className="mb-4">
        <FilterBar filters={filters} onChange={setFilters} />
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <span className="loading loading-spinner loading-lg"></span>
        </div>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>Título</th>
                  <th>Estado</th>
                  <th>Prioridad</th>
                  <th>Asignado a</th>
                  <th>Fecha límite</th>
                </tr>
              </thead>
              <tbody>
                {data?.items.map((task) => (
                  <tr
                    key={task.id}
                    className="hover cursor-pointer"
                    onClick={() => navigate(`/tasks/${task.id}`)}
                  >
                    <td className="font-medium">{task.title}</td>
                    <td>
                      <span className="badge badge-sm">
                        {task.status.replace("_", " ")}
                      </span>
                    </td>
                    <td>
                      <span
                        className={`badge badge-sm ${priorityColors[task.priority]}`}
                      >
                        {task.priority}
                      </span>
                    </td>
                    <td>{task.assignee?.name ?? "—"}</td>
                    <td>
                      {task.due_date
                        ? new Date(task.due_date).toLocaleDateString("es")
                        : "—"}
                    </td>
                  </tr>
                ))}
                {data?.items.length === 0 && (
                  <tr>
                    <td
                      colSpan={5}
                      className="text-center text-base-content/60"
                    >
                      No se encontraron tareas
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {data && data.total_pages > 1 && (
            <div className="flex justify-center mt-4">
              <div className="join">
                {Array.from({ length: data.total_pages }, (_, i) => (
                  <button
                    key={i + 1}
                    className={`join-item btn btn-sm ${
                      filters.page === i + 1 ? "btn-active" : ""
                    }`}
                    onClick={() => setFilters({ ...filters, page: i + 1 })}
                  >
                    {i + 1}
                  </button>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
