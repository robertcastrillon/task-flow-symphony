import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { taskFormSchema, type TaskFormData, type Task } from "../types";
import { useUsers } from "../hooks/useUsers";

interface TaskFormProps {
  task?: Task;
  onSubmit: (data: TaskFormData) => void;
  onCancel?: () => void;
  isLoading?: boolean;
}

export default function TaskForm({
  task,
  onSubmit,
  onCancel,
  isLoading = false,
}: TaskFormProps) {
  const { data: users } = useUsers();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<TaskFormData>({
    resolver: zodResolver(taskFormSchema),
    defaultValues: task
      ? {
          title: task.title,
          description: task.description ?? "",
          priority: task.priority,
          status: task.status,
          due_date: task.due_date ?? "",
          assigned_to: task.assigned_to,
          tags: task.tags,
        }
      : {
          priority: "medium",
          status: "todo",
          tags: [],
        },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="form-control">
        <label className="label" htmlFor="title">
          <span className="label-text">Título</span>
        </label>
        <input
          id="title"
          type="text"
          className={`input input-bordered ${errors.title ? "input-error" : ""}`}
          {...register("title")}
        />
        {errors.title && (
          <label className="label">
            <span className="label-text-alt text-error">
              {errors.title.message}
            </span>
          </label>
        )}
      </div>

      <div className="form-control">
        <label className="label" htmlFor="description">
          <span className="label-text">Descripción</span>
        </label>
        <textarea
          id="description"
          className="textarea textarea-bordered"
          {...register("description")}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="form-control">
          <label className="label" htmlFor="priority">
            <span className="label-text">Prioridad</span>
          </label>
          <select
            id="priority"
            className="select select-bordered"
            {...register("priority")}
          >
            <option value="low">Baja</option>
            <option value="medium">Media</option>
            <option value="high">Alta</option>
            <option value="urgent">Urgente</option>
          </select>
        </div>

        <div className="form-control">
          <label className="label" htmlFor="status">
            <span className="label-text">Estado</span>
          </label>
          <select
            id="status"
            className="select select-bordered"
            {...register("status")}
          >
            <option value="todo">Por hacer</option>
            <option value="in_progress">En progreso</option>
            <option value="done">Hecho</option>
            <option value="cancelled">Cancelado</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="form-control">
          <label className="label" htmlFor="due_date">
            <span className="label-text">Fecha límite</span>
          </label>
          <input
            id="due_date"
            type="date"
            className="input input-bordered"
            {...register("due_date")}
          />
        </div>

        <div className="form-control">
          <label className="label" htmlFor="assigned_to">
            <span className="label-text">Asignado a</span>
          </label>
          <select
            id="assigned_to"
            className="select select-bordered"
            {...register("assigned_to")}
          >
            <option value="">Sin asignar</option>
            {users?.map((user) => (
              <option key={user.id} value={user.id}>
                {user.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="flex justify-end gap-2 pt-2">
        {onCancel && (
          <button type="button" className="btn btn-ghost" onClick={onCancel}>
            Cancelar
          </button>
        )}
        <button type="submit" className="btn btn-primary" disabled={isLoading}>
          {isLoading && <span className="loading loading-spinner loading-sm" />}
          {task ? "Guardar" : "Crear tarea"}
        </button>
      </div>
    </form>
  );
}
