import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import FilterBar from "./FilterBar";
import type { TaskFilters, User } from "../types";

vi.mock("../hooks/useUsers", () => ({
  useUsers: vi.fn(),
}));

import { useUsers } from "../hooks/useUsers";

const mockedUseUsers = vi.mocked(useUsers);

const sampleUsers: User[] = [
  {
    id: "user-1",
    name: "Ana García",
    email: "ana@test.com",
    avatar_url: null,
    role: "admin",
    is_active: true,
    created_at: "2026-01-01T00:00:00Z",
  },
  {
    id: "user-2",
    name: "Carlos López",
    email: "carlos@test.com",
    avatar_url: null,
    role: "member",
    is_active: true,
    created_at: "2026-01-01T00:00:00Z",
  },
];

describe("FilterBar", () => {
  const mockOnChange = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockedUseUsers.mockReturnValue({
      data: sampleUsers,
    } as ReturnType<typeof useUsers>);
  });

  it("renders all filter controls", () => {
    render(<FilterBar filters={{}} onChange={mockOnChange} />);

    expect(screen.getByPlaceholderText("Buscar tareas...")).toBeInTheDocument();
    expect(screen.getByLabelText("Filtrar por estado")).toBeInTheDocument();
    expect(screen.getByLabelText("Filtrar por prioridad")).toBeInTheDocument();
    expect(screen.getByLabelText("Filtrar por asignado")).toBeInTheDocument();
  });

  it("renders user options in assignee filter", () => {
    render(<FilterBar filters={{}} onChange={mockOnChange} />);

    expect(screen.getByText("Ana García")).toBeInTheDocument();
    expect(screen.getByText("Carlos López")).toBeInTheDocument();
  });

  it("renders status options", () => {
    render(<FilterBar filters={{}} onChange={mockOnChange} />);

    const statusSelect = screen.getByLabelText("Filtrar por estado");
    expect(statusSelect).toBeInTheDocument();
    expect(screen.getByText("Todos los estados")).toBeInTheDocument();
    expect(screen.getByText("Por hacer")).toBeInTheDocument();
    expect(screen.getByText("En progreso")).toBeInTheDocument();
    expect(screen.getByText("Hecho")).toBeInTheDocument();
    expect(screen.getByText("Cancelado")).toBeInTheDocument();
  });

  it("renders priority options", () => {
    render(<FilterBar filters={{}} onChange={mockOnChange} />);

    expect(screen.getByText("Todas las prioridades")).toBeInTheDocument();
    expect(screen.getByText("Baja")).toBeInTheDocument();
    expect(screen.getByText("Media")).toBeInTheDocument();
    expect(screen.getByText("Alta")).toBeInTheDocument();
    expect(screen.getByText("Urgente")).toBeInTheDocument();
  });

  it("calls onChange when search input changes", async () => {
    const user = userEvent.setup();
    render(<FilterBar filters={{}} onChange={mockOnChange} />);

    await user.type(screen.getByPlaceholderText("Buscar tareas..."), "t");

    expect(mockOnChange).toHaveBeenCalledWith(
      expect.objectContaining({ search: "t", page: 1 }),
    );
  });

  it("calls onChange when status filter changes", async () => {
    const user = userEvent.setup();
    render(<FilterBar filters={{}} onChange={mockOnChange} />);

    await user.selectOptions(
      screen.getByLabelText("Filtrar por estado"),
      "todo",
    );

    expect(mockOnChange).toHaveBeenCalledWith(
      expect.objectContaining({ status: "todo", page: 1 }),
    );
  });

  it("calls onChange when priority filter changes", async () => {
    const user = userEvent.setup();
    render(<FilterBar filters={{}} onChange={mockOnChange} />);

    await user.selectOptions(
      screen.getByLabelText("Filtrar por prioridad"),
      "high",
    );

    expect(mockOnChange).toHaveBeenCalledWith(
      expect.objectContaining({ priority: "high", page: 1 }),
    );
  });

  it("calls onChange when assignee filter changes", async () => {
    const user = userEvent.setup();
    render(<FilterBar filters={{}} onChange={mockOnChange} />);

    await user.selectOptions(
      screen.getByLabelText("Filtrar por asignado"),
      "user-1",
    );

    expect(mockOnChange).toHaveBeenCalledWith(
      expect.objectContaining({ assignee: "user-1", page: 1 }),
    );
  });

  it("resets page to 1 when any filter changes", async () => {
    const user = userEvent.setup();
    const filters: TaskFilters = { page: 3 };
    render(<FilterBar filters={filters} onChange={mockOnChange} />);

    await user.selectOptions(
      screen.getByLabelText("Filtrar por estado"),
      "done",
    );

    expect(mockOnChange).toHaveBeenCalledWith(
      expect.objectContaining({ page: 1 }),
    );
  });

  it("clears filter when empty option is selected", async () => {
    const user = userEvent.setup();
    const filters: TaskFilters = { status: "todo" };
    render(<FilterBar filters={filters} onChange={mockOnChange} />);

    await user.selectOptions(screen.getByLabelText("Filtrar por estado"), "");

    expect(mockOnChange).toHaveBeenCalledWith(
      expect.objectContaining({ status: undefined, page: 1 }),
    );
  });

  it("displays current filter values", () => {
    const filters: TaskFilters = {
      search: "bug fix",
      status: "in_progress",
      priority: "high",
    };
    render(<FilterBar filters={filters} onChange={mockOnChange} />);

    expect(screen.getByPlaceholderText("Buscar tareas...")).toHaveValue(
      "bug fix",
    );
    expect(screen.getByLabelText("Filtrar por estado")).toHaveValue(
      "in_progress",
    );
    expect(screen.getByLabelText("Filtrar por prioridad")).toHaveValue("high");
  });

  it("has search role on container", () => {
    render(<FilterBar filters={{}} onChange={mockOnChange} />);
    expect(screen.getByRole("search")).toBeInTheDocument();
  });
});
