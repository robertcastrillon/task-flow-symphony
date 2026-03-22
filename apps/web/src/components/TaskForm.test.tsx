import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import TaskForm from "./TaskForm";
import type { Task, User } from "../types";

vi.mock("../hooks/useUsers", () => ({
  useUsers: vi.fn(),
}));

import { useUsers } from "../hooks/useUsers";

const mockedUseUsers = vi.mocked(useUsers);

const sampleUsers: User[] = [
  {
    id: "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    name: "Ana García",
    email: "ana@test.com",
    avatar_url: null,
    role: "admin",
    is_active: true,
    created_at: "2026-01-01T00:00:00Z",
  },
  {
    id: "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22",
    name: "Carlos López",
    email: "carlos@test.com",
    avatar_url: null,
    role: "member",
    is_active: true,
    created_at: "2026-01-01T00:00:00Z",
  },
];

const sampleTask: Task = {
  id: "task-1",
  title: "Existing Task",
  description: "Task description",
  status: "in_progress",
  priority: "high",
  due_date: "2026-06-15",
  created_by: "user-1",
  assigned_to: "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22",
  tags: ["frontend"],
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
  completed_at: null,
};

describe("TaskForm", () => {
  const mockOnSubmit = vi.fn();
  const mockOnCancel = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockedUseUsers.mockReturnValue({
      data: sampleUsers,
    } as ReturnType<typeof useUsers>);
  });

  it("renders all form fields", () => {
    render(<TaskForm onSubmit={mockOnSubmit} />);

    expect(screen.getByLabelText("Título")).toBeInTheDocument();
    expect(screen.getByLabelText("Descripción")).toBeInTheDocument();
    expect(screen.getByLabelText("Prioridad")).toBeInTheDocument();
    expect(screen.getByLabelText("Estado")).toBeInTheDocument();
    expect(screen.getByLabelText("Fecha límite")).toBeInTheDocument();
    expect(screen.getByLabelText("Asignado a")).toBeInTheDocument();
  });

  it("renders create button when no task is provided", () => {
    render(<TaskForm onSubmit={mockOnSubmit} />);
    expect(
      screen.getByRole("button", { name: /Crear tarea/i }),
    ).toBeInTheDocument();
  });

  it("renders save button when task is provided", () => {
    render(<TaskForm task={sampleTask} onSubmit={mockOnSubmit} />);
    expect(
      screen.getByRole("button", { name: /Guardar/i }),
    ).toBeInTheDocument();
  });

  it("renders cancel button when onCancel is provided", () => {
    render(<TaskForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);
    expect(
      screen.getByRole("button", { name: /Cancelar/i }),
    ).toBeInTheDocument();
  });

  it("does not render cancel button when onCancel is not provided", () => {
    render(<TaskForm onSubmit={mockOnSubmit} />);
    expect(
      screen.queryByRole("button", { name: /Cancelar/i }),
    ).not.toBeInTheDocument();
  });

  it("calls onCancel when cancel button is clicked", async () => {
    const user = userEvent.setup();
    render(<TaskForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);

    await user.click(screen.getByRole("button", { name: /Cancelar/i }));
    expect(mockOnCancel).toHaveBeenCalledOnce();
  });

  it("populates form with task data when editing", () => {
    render(<TaskForm task={sampleTask} onSubmit={mockOnSubmit} />);

    expect(screen.getByLabelText("Título")).toHaveValue("Existing Task");
    expect(screen.getByLabelText("Descripción")).toHaveValue(
      "Task description",
    );
    expect(screen.getByLabelText("Prioridad")).toHaveValue("high");
    expect(screen.getByLabelText("Estado")).toHaveValue("in_progress");
  });

  it("has default values for new task", () => {
    render(<TaskForm onSubmit={mockOnSubmit} />);

    expect(screen.getByLabelText("Título")).toHaveValue("");
    expect(screen.getByLabelText("Prioridad")).toHaveValue("medium");
    expect(screen.getByLabelText("Estado")).toHaveValue("todo");
  });

  it("renders user options in assignee select", () => {
    render(<TaskForm onSubmit={mockOnSubmit} />);

    expect(screen.getByText("Sin asignar")).toBeInTheDocument();
    expect(screen.getByText("Ana García")).toBeInTheDocument();
    expect(screen.getByText("Carlos López")).toBeInTheDocument();
  });

  it("renders priority options", () => {
    render(<TaskForm onSubmit={mockOnSubmit} />);

    expect(screen.getByText("Baja")).toBeInTheDocument();
    expect(screen.getByText("Media")).toBeInTheDocument();
    expect(screen.getByText("Alta")).toBeInTheDocument();
    expect(screen.getByText("Urgente")).toBeInTheDocument();
  });

  it("renders status options", () => {
    render(<TaskForm onSubmit={mockOnSubmit} />);

    expect(screen.getByText("Por hacer")).toBeInTheDocument();
    expect(screen.getByText("En progreso")).toBeInTheDocument();
    expect(screen.getByText("Hecho")).toBeInTheDocument();
    expect(screen.getByText("Cancelado")).toBeInTheDocument();
  });

  it("shows validation error when title is empty", async () => {
    const user = userEvent.setup();
    render(<TaskForm onSubmit={mockOnSubmit} />);

    await user.click(screen.getByRole("button", { name: /Crear tarea/i }));

    await waitFor(() => {
      expect(screen.getByText("El título es obligatorio")).toBeInTheDocument();
    });
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it("submits form with valid data", async () => {
    const user = userEvent.setup();
    render(<TaskForm onSubmit={mockOnSubmit} />);

    await user.type(screen.getByLabelText("Título"), "New Task Title");
    await user.selectOptions(
      screen.getByLabelText("Asignado a"),
      "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    );

    await user.click(screen.getByRole("button", { name: /Crear tarea/i }));

    await waitFor(
      () => {
        expect(mockOnSubmit).toHaveBeenCalled();
      },
      { timeout: 3000 },
    );

    const callArg = mockOnSubmit.mock.calls[0][0];
    expect(callArg.title).toBe("New Task Title");
    expect(callArg.priority).toBe("medium");
    expect(callArg.status).toBe("todo");
    expect(callArg.assigned_to).toBe("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11");
  });

  it("disables submit button when isLoading is true", () => {
    render(<TaskForm onSubmit={mockOnSubmit} isLoading={true} />);

    expect(screen.getByRole("button", { name: /Crear tarea/i })).toBeDisabled();
  });

  it("shows loading spinner when isLoading is true", () => {
    render(<TaskForm onSubmit={mockOnSubmit} isLoading={true} />);

    expect(screen.getByText("", { selector: ".loading" })).toBeInTheDocument();
  });
});
