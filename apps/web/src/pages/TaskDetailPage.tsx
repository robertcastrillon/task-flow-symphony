import { useParams, useNavigate } from "react-router-dom";
import { useTask, useUpdateTask, useDeleteTask } from "../hooks/useTasks";
import CommentThread from "../components/CommentThread";
import TaskForm from "../components/TaskForm";
import { useState } from "react";
import type { TaskFormData } from "../types";

export default function TaskDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: task, isLoading } = useTask(id!);
  const updateTask = useUpdateTask();
  const deleteTask = useDeleteTask();
  const [isEditing, setIsEditing] = useState(false);

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <span className="loading loading-spinner loading-lg"></span>
      </div>
    );
  }

  if (!task) {
    return (
      <div className="text-center py-12">
        <p className="text-base-content/60">Tarea no encontrada</p>
      </div>
    );
  }

  function handleUpdate(data: TaskFormData) {
    updateTask.mutate(
      { id: id!, ...data },
      { onSuccess: () => setIsEditing(false) },
    );
  }

  function handleDelete() {
    if (window.confirm("¿Estás seguro de que quieres eliminar esta tarea?")) {
      deleteTask.mutate(id!, {
        onSuccess: () => navigate("/tasks/list"),
      });
    }
  }

  return (
    <div className="max-w-3xl mx-auto">
      <button
        onClick={() => navigate(-1)}
        className="btn btn-ghost btn-sm mb-4"
      >
        ← Volver
      </button>

      {isEditing ? (
        <div className="card bg-base-200">
          <div className="card-body">
            <h2 className="card-title">Editar tarea</h2>
            <TaskForm
              task={task}
              onSubmit={handleUpdate}
              onCancel={() => setIsEditing(false)}
              isLoading={updateTask.isPending}
            />
          </div>
        </div>
      ) : (
        <div className="card bg-base-200">
          <div className="card-body">
            <div className="flex justify-between items-start">
              <h1 className="card-title text-xl">{task.title}</h1>
              <div className="flex gap-2">
                <button
                  className="btn btn-sm btn-ghost"
                  onClick={() => setIsEditing(true)}
                >
                  Editar
                </button>
                <button
                  className="btn btn-sm btn-error btn-ghost"
                  onClick={handleDelete}
                >
                  Eliminar
                </button>
              </div>
            </div>

            {task.description && (
              <p className="text-base-content/80 mt-2">{task.description}</p>
            )}

            <div className="grid grid-cols-2 gap-4 mt-4">
              <div>
                <span className="text-sm text-base-content/60">Estado</span>
                <p className="font-medium capitalize">
                  {task.status.replace("_", " ")}
                </p>
              </div>
              <div>
                <span className="text-sm text-base-content/60">Prioridad</span>
                <p className="font-medium capitalize">{task.priority}</p>
              </div>
              <div>
                <span className="text-sm text-base-content/60">Asignado a</span>
                <p className="font-medium">
                  {task.assignee?.name ?? "Sin asignar"}
                </p>
              </div>
              <div>
                <span className="text-sm text-base-content/60">
                  Fecha límite
                </span>
                <p className="font-medium">
                  {task.due_date
                    ? new Date(task.due_date).toLocaleDateString("es")
                    : "Sin fecha"}
                </p>
              </div>
            </div>

            {task.tags.length > 0 && (
              <div className="mt-4">
                <span className="text-sm text-base-content/60">Tags</span>
                <div className="flex gap-1 mt-1">
                  {task.tags.map((tag) => (
                    <span key={tag} className="badge badge-sm badge-outline">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="mt-6 card bg-base-200">
        <div className="card-body">
          <CommentThread taskId={id!} />
        </div>
      </div>
    </div>
  );
}
