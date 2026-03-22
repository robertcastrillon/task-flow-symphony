import { useNavigate } from "react-router-dom";
import { useTaskList, useChangeStatus } from "../hooks/useTasks";
import KanbanBoard from "../components/KanbanBoard";
import type { TaskStatus } from "../types";

export default function TaskBoardPage() {
  const navigate = useNavigate();
  const { data, isLoading } = useTaskList({ page_size: 50 });
  const changeStatus = useChangeStatus();

  function handleStatusChange(taskId: string, status: TaskStatus) {
    changeStatus.mutate({ id: taskId, status });
  }

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <span className="loading loading-spinner loading-lg"></span>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Tablero Kanban</h1>
      </div>
      <div className="flex-1">
        <KanbanBoard
          tasks={data?.items ?? []}
          onStatusChange={handleStatusChange}
          onTaskClick={(task) => navigate(`/tasks/${task.id}`)}
        />
      </div>
    </div>
  );
}
