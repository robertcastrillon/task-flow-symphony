import type { Task } from "../types";

const priorityColors: Record<string, string> = {
  low: "badge-info",
  medium: "badge-warning",
  high: "badge-error",
  urgent: "badge-error badge-outline",
};

interface TaskCardProps {
  task: Task;
  onClick?: (task: Task) => void;
}

export default function TaskCard({ task, onClick }: TaskCardProps) {
  const isOverdue =
    task.due_date &&
    new Date(task.due_date) < new Date() &&
    task.status !== "done";

  return (
    <div
      className={`card bg-base-100 shadow-sm border cursor-pointer hover:shadow-md transition-shadow ${
        isOverdue ? "border-error" : "border-base-300"
      }`}
      onClick={() => onClick?.(task)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") onClick?.(task);
      }}
    >
      <div className="card-body p-3 gap-2">
        <h3 className="card-title text-sm">{task.title}</h3>
        <div className="flex items-center gap-2 flex-wrap">
          <span className={`badge badge-sm ${priorityColors[task.priority]}`}>
            {task.priority}
          </span>
          {isOverdue && (
            <span className="badge badge-sm badge-error">Vencida</span>
          )}
        </div>
        <div className="flex items-center justify-between mt-1">
          {task.assignee && (
            <div className="flex items-center gap-1">
              <div className="avatar placeholder">
                <div className="bg-neutral text-neutral-content w-6 rounded-full">
                  <span className="text-xs">
                    {task.assignee.name.charAt(0).toUpperCase()}
                  </span>
                </div>
              </div>
              <span className="text-xs text-base-content/60">
                {task.assignee.name}
              </span>
            </div>
          )}
          {task.due_date && (
            <span className="text-xs text-base-content/60">
              {new Date(task.due_date).toLocaleDateString("es")}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
