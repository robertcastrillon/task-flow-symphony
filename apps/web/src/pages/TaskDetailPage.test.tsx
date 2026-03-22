import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import TaskDetailPage from "./TaskDetailPage";
import type { Task, TaskFormData } from "../types";

const mockNavigate = vi.fn();
const mockUpdateMutate = vi.fn();
const mockDeleteMutate = vi.fn();

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useParams: () => ({ id: "task-1" }),
    useNavigate: () => mockNavigate,
  };
});

vi.mock("../hooks/useTasks", () => ({
  useTask: vi.fn(),
  useUpdateTask: vi.fn(),
  useDeleteTask: vi.fn(),
}));

vi.mock("../components/CommentThread", () => ({
  default: ({ taskId }: { taskId: string }) => (
    <div data-testid="comment-thread">Comments for {taskId}</div>
  ),
}));

vi.mock("../components/TaskForm", () => ({
  default: ({
    onSubmit,
    onCancel,
  }: {
    onSubmit: (data: TaskFormData) => void;
    onCancel?: () => void;
  }) => (
    <div data-testid="task-form">
      <button onClick={() => onSubmit({ title: "Updated" } as TaskFormData)}>
        Save
      </button>
      {onCancel && <button onClick={onCancel}>Cancel</button>}
    </div>
  ),
}));

import { useTask, useUpdateTask, useDeleteTask } from "../hooks/useTasks";

const mockedUseTask = vi.mocked(useTask);
const mockedUseUpdateTask = vi.mocked(useUpdateTask);
const mockedUseDeleteTask = vi.mocked(useDeleteTask);

const sampleTask: Task = {
  id: "task-1",
  title: "Test Task",
  description: "A test task description",
  status: "in_progress",
  priority: "high",
  due_date: "2026-06-15",
  created_by: "user-1",
  assigned_to: "user-2",
  tags: ["frontend", "bug"],
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
  completed_at: null,
  assignee: {
    id: "user-2",
    name: "María",
    email: "maria@test.com",
    avatar_url: null,
    role: "member",
    is_active: true,
    created_at: "2026-01-01T00:00:00Z",
  },
};

describe("TaskDetailPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockedUseUpdateTask.mockReturnValue({
      mutate: mockUpdateMutate,
      isPending: false,
    } as ReturnType<typeof useUpdateTask>);
    mockedUseDeleteTask.mockReturnValue({
      mutate: mockDeleteMutate,
    } as ReturnType<typeof useDeleteTask>);
  });

  it("shows loading spinner while loading", () => {
    mockedUseTask.mockReturnValue({
      data: undefined,
      isLoading: true,
    } as ReturnType<typeof useTask>);

    render(<TaskDetailPage />);
    expect(screen.getByText("", { selector: ".loading" })).toBeInTheDocument();
  });

  it("shows not found message when task is null", () => {
    mockedUseTask.mockReturnValue({
      data: undefined,
      isLoading: false,
    } as ReturnType<typeof useTask>);

    render(<TaskDetailPage />);
    expect(screen.getByText("Tarea no encontrada")).toBeInTheDocument();
  });

  it("renders task details", () => {
    mockedUseTask.mockReturnValue({
      data: sampleTask,
      isLoading: false,
    } as ReturnType<typeof useTask>);

    render(<TaskDetailPage />);
    expect(screen.getByText("Test Task")).toBeInTheDocument();
    expect(screen.getByText("A test task description")).toBeInTheDocument();
    expect(screen.getByText("in progress")).toBeInTheDocument();
    expect(screen.getByText("high")).toBeInTheDocument();
    expect(screen.getByText("María")).toBeInTheDocument();
    expect(screen.getByText("frontend")).toBeInTheDocument();
    expect(screen.getByText("bug")).toBeInTheDocument();
  });

  it("renders comment thread", () => {
    mockedUseTask.mockReturnValue({
      data: sampleTask,
      isLoading: false,
    } as ReturnType<typeof useTask>);

    render(<TaskDetailPage />);
    expect(screen.getByTestId("comment-thread")).toBeInTheDocument();
    expect(screen.getByText("Comments for task-1")).toBeInTheDocument();
  });

  it("shows back button that calls navigate(-1)", async () => {
    mockedUseTask.mockReturnValue({
      data: sampleTask,
      isLoading: false,
    } as ReturnType<typeof useTask>);

    const user = userEvent.setup();
    render(<TaskDetailPage />);
    await user.click(screen.getByText(/Volver/));
    expect(mockNavigate).toHaveBeenCalledWith(-1);
  });

  it("switches to edit mode when Editar is clicked", async () => {
    mockedUseTask.mockReturnValue({
      data: sampleTask,
      isLoading: false,
    } as ReturnType<typeof useTask>);

    const user = userEvent.setup();
    render(<TaskDetailPage />);

    await user.click(screen.getByText("Editar"));
    expect(screen.getByTestId("task-form")).toBeInTheDocument();
    expect(screen.getByText("Editar tarea")).toBeInTheDocument();
  });

  it("submits update from edit form", async () => {
    mockUpdateMutate.mockImplementation(
      (_data: Record<string, unknown>, options?: Record<string, unknown>) => {
        const opts = options as { onSuccess?: () => void } | undefined;
        opts?.onSuccess?.();
      },
    );
    mockedUseTask.mockReturnValue({
      data: sampleTask,
      isLoading: false,
    } as ReturnType<typeof useTask>);

    const user = userEvent.setup();
    render(<TaskDetailPage />);

    await user.click(screen.getByText("Editar"));
    await user.click(screen.getByText("Save"));

    expect(mockUpdateMutate).toHaveBeenCalledWith(
      { id: "task-1", title: "Updated" },
      expect.objectContaining({ onSuccess: expect.any(Function) }),
    );
  });

  it("cancels editing and returns to detail view", async () => {
    mockedUseTask.mockReturnValue({
      data: sampleTask,
      isLoading: false,
    } as ReturnType<typeof useTask>);

    const user = userEvent.setup();
    render(<TaskDetailPage />);

    await user.click(screen.getByText("Editar"));
    expect(screen.getByTestId("task-form")).toBeInTheDocument();

    await user.click(screen.getByText("Cancel"));
    expect(screen.queryByTestId("task-form")).not.toBeInTheDocument();
    expect(screen.getByText("Test Task")).toBeInTheDocument();
  });

  it("calls delete with confirmation", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(true);
    mockDeleteMutate.mockImplementation(
      (_id: string, options?: Record<string, unknown>) => {
        const opts = options as { onSuccess?: () => void } | undefined;
        opts?.onSuccess?.();
      },
    );
    mockedUseTask.mockReturnValue({
      data: sampleTask,
      isLoading: false,
    } as ReturnType<typeof useTask>);

    const user = userEvent.setup();
    render(<TaskDetailPage />);

    await user.click(screen.getByText("Eliminar"));

    expect(window.confirm).toHaveBeenCalledWith(
      "¿Estás seguro de que quieres eliminar esta tarea?",
    );
    expect(mockDeleteMutate).toHaveBeenCalledWith(
      "task-1",
      expect.objectContaining({ onSuccess: expect.any(Function) }),
    );
  });

  it("does not delete when confirmation is cancelled", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(false);
    mockedUseTask.mockReturnValue({
      data: sampleTask,
      isLoading: false,
    } as ReturnType<typeof useTask>);

    const user = userEvent.setup();
    render(<TaskDetailPage />);

    await user.click(screen.getByText("Eliminar"));

    expect(mockDeleteMutate).not.toHaveBeenCalled();
  });

  it("shows 'Sin asignar' when task has no assignee", () => {
    const taskNoAssignee: Task = {
      ...sampleTask,
      assignee: undefined,
      assigned_to: null,
    };
    mockedUseTask.mockReturnValue({
      data: taskNoAssignee,
      isLoading: false,
    } as ReturnType<typeof useTask>);

    render(<TaskDetailPage />);
    expect(screen.getByText("Sin asignar")).toBeInTheDocument();
  });

  it("shows 'Sin fecha' when task has no due date", () => {
    const taskNoDate: Task = { ...sampleTask, due_date: null };
    mockedUseTask.mockReturnValue({
      data: taskNoDate,
      isLoading: false,
    } as ReturnType<typeof useTask>);

    render(<TaskDetailPage />);
    expect(screen.getByText("Sin fecha")).toBeInTheDocument();
  });

  it("does not render description when null", () => {
    const taskNoDesc: Task = { ...sampleTask, description: null };
    mockedUseTask.mockReturnValue({
      data: taskNoDesc,
      isLoading: false,
    } as ReturnType<typeof useTask>);

    render(<TaskDetailPage />);
    expect(
      screen.queryByText("A test task description"),
    ).not.toBeInTheDocument();
  });

  it("does not render tags section when tags are empty", () => {
    const taskNoTags: Task = { ...sampleTask, tags: [] };
    mockedUseTask.mockReturnValue({
      data: taskNoTags,
      isLoading: false,
    } as ReturnType<typeof useTask>);

    render(<TaskDetailPage />);
    expect(screen.queryByText("Tags")).not.toBeInTheDocument();
  });
});
