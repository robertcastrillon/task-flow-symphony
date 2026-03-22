import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import TaskBoardPage from "./TaskBoardPage";
import type { Task, PaginatedResponse } from "../types";

const mockNavigate = vi.fn();
const mockMutate = vi.fn();

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

vi.mock("../hooks/useTasks", () => ({
  useTaskList: vi.fn(),
  useChangeStatus: vi.fn(),
}));

// Mock KanbanBoard to avoid dnd-kit complexity
vi.mock("../components/KanbanBoard", () => ({
  default: ({
    tasks,
    onTaskClick,
    onStatusChange,
  }: {
    tasks: Task[];
    onTaskClick?: (task: Task) => void;
    onStatusChange: (taskId: string, status: string) => void;
  }) => (
    <div data-testid="kanban-board">
      {tasks.map((t) => (
        <div key={t.id} data-testid={`task-${t.id}`}>
          <span>{t.title}</span>
          <button onClick={() => onTaskClick?.(t)}>click-{t.id}</button>
          <button onClick={() => onStatusChange(t.id, "done")}>
            change-status-{t.id}
          </button>
        </div>
      ))}
    </div>
  ),
}));

import { useTaskList, useChangeStatus } from "../hooks/useTasks";

const mockedUseTaskList = vi.mocked(useTaskList);
const mockedUseChangeStatus = vi.mocked(useChangeStatus);

const sampleTasks: Task[] = [
  {
    id: "task-1",
    title: "Task One",
    description: null,
    status: "todo",
    priority: "medium",
    due_date: null,
    created_by: "user-1",
    assigned_to: null,
    tags: [],
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
    completed_at: null,
  },
];

describe("TaskBoardPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockedUseChangeStatus.mockReturnValue({
      mutate: mockMutate,
    } as ReturnType<typeof useChangeStatus>);
  });

  it("shows loading spinner while loading", () => {
    mockedUseTaskList.mockReturnValue({
      data: undefined,
      isLoading: true,
    } as ReturnType<typeof useTaskList>);

    render(<TaskBoardPage />);
    expect(screen.getByText("", { selector: ".loading" })).toBeInTheDocument();
  });

  it("renders the kanban board with tasks", () => {
    mockedUseTaskList.mockReturnValue({
      data: { items: sampleTasks } as PaginatedResponse<Task>,
      isLoading: false,
    } as ReturnType<typeof useTaskList>);

    render(<TaskBoardPage />);
    expect(screen.getByText("Tablero Kanban")).toBeInTheDocument();
    expect(screen.getByTestId("kanban-board")).toBeInTheDocument();
    expect(screen.getByText("Task One")).toBeInTheDocument();
  });

  it("renders empty board when no tasks", () => {
    mockedUseTaskList.mockReturnValue({
      data: { items: [] } as unknown as PaginatedResponse<Task>,
      isLoading: false,
    } as ReturnType<typeof useTaskList>);

    render(<TaskBoardPage />);
    expect(screen.getByTestId("kanban-board")).toBeInTheDocument();
  });

  it("navigates to task detail on task click", async () => {
    mockedUseTaskList.mockReturnValue({
      data: { items: sampleTasks } as PaginatedResponse<Task>,
      isLoading: false,
    } as ReturnType<typeof useTaskList>);

    render(<TaskBoardPage />);
    const clickBtn = screen.getByText("click-task-1");
    clickBtn.click();

    expect(mockNavigate).toHaveBeenCalledWith("/tasks/task-1");
  });

  it("calls changeStatus.mutate on status change", () => {
    mockedUseTaskList.mockReturnValue({
      data: { items: sampleTasks } as PaginatedResponse<Task>,
      isLoading: false,
    } as ReturnType<typeof useTaskList>);

    render(<TaskBoardPage />);
    screen.getByText("change-status-task-1").click();

    expect(mockMutate).toHaveBeenCalledWith({
      id: "task-1",
      status: "done",
    });
  });

  it("handles undefined data gracefully", () => {
    mockedUseTaskList.mockReturnValue({
      data: undefined,
      isLoading: false,
    } as ReturnType<typeof useTaskList>);

    render(<TaskBoardPage />);
    expect(screen.getByTestId("kanban-board")).toBeInTheDocument();
  });
});
