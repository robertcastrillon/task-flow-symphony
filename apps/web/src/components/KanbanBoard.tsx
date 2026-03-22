import {
  DndContext,
  DragOverlay,
  closestCorners,
  type DragStartEvent,
  type DragEndEvent,
} from "@dnd-kit/core";
import {
  SortableContext,
  verticalListSortingStrategy,
  useSortable,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { useState } from "react";
import type { Task, TaskStatus } from "../types";
import TaskCard from "./TaskCard";

const columns: { id: TaskStatus; label: string }[] = [
  { id: "todo", label: "Por hacer" },
  { id: "in_progress", label: "En progreso" },
  { id: "done", label: "Hecho" },
];

interface KanbanBoardProps {
  tasks: Task[];
  onStatusChange: (taskId: string, status: TaskStatus) => void;
  onTaskClick?: (task: Task) => void;
}

function SortableTaskCard({
  task,
  onClick,
}: {
  task: Task;
  onClick?: (task: Task) => void;
}) {
  const { attributes, listeners, setNodeRef, transform, transition } =
    useSortable({ id: task.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      <TaskCard task={task} onClick={onClick} />
    </div>
  );
}

export default function KanbanBoard({
  tasks,
  onStatusChange,
  onTaskClick,
}: KanbanBoardProps) {
  const [activeTask, setActiveTask] = useState<Task | null>(null);

  const tasksByStatus = columns.reduce(
    (acc, col) => {
      acc[col.id] = tasks.filter((t) => t.status === col.id);
      return acc;
    },
    {} as Record<TaskStatus, Task[]>,
  );

  function handleDragStart(event: DragStartEvent) {
    const task = tasks.find((t) => t.id === event.active.id);
    if (task) setActiveTask(task);
  }

  function handleDragEnd(event: DragEndEvent) {
    setActiveTask(null);
    const { active, over } = event;
    if (!over) return;

    const taskId = active.id as string;
    const overColumn = columns.find((c) => c.id === over.id);
    if (overColumn) {
      const task = tasks.find((t) => t.id === taskId);
      if (task && task.status !== overColumn.id) {
        onStatusChange(taskId, overColumn.id);
      }
    }
  }

  return (
    <DndContext
      collisionDetection={closestCorners}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div className="grid grid-cols-3 gap-4 h-full">
        {columns.map((col) => (
          <div key={col.id} className="bg-base-200 rounded-lg p-3">
            <h2 className="font-semibold mb-3 text-sm uppercase tracking-wide">
              {col.label}{" "}
              <span className="badge badge-sm">
                {tasksByStatus[col.id].length}
              </span>
            </h2>
            <SortableContext
              id={col.id}
              items={tasksByStatus[col.id].map((t) => t.id)}
              strategy={verticalListSortingStrategy}
            >
              <div
                className="space-y-2 min-h-[100px]"
                data-testid={`column-${col.id}`}
              >
                {tasksByStatus[col.id].map((task) => (
                  <SortableTaskCard
                    key={task.id}
                    task={task}
                    onClick={onTaskClick}
                  />
                ))}
              </div>
            </SortableContext>
          </div>
        ))}
      </div>
      <DragOverlay>{activeTask && <TaskCard task={activeTask} />}</DragOverlay>
    </DndContext>
  );
}
