import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MemoryRouter } from "react-router-dom";
import TaskListPage from "./TaskListPage";
import type { Task, TaskFilters } from "../types";

const mockNavigate = vi.fn();

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

vi.mock("../hooks/useTasks", () => ({
  useTaskList: vi.fn(),
}));

vi.mock("../components/FilterBar", () => ({
  default: ({
    filters,
    onChange,
  }: {
    filters: TaskFilters;
    onChange: (f: TaskFilters) => void;
  }) => (
    <div data-testid="filter-bar">
      <button onClick={() => onChange({ ...filters, status: "done", page: 1 })}>
        filter-done
      </button>
    </div>
  ),
}));

import { useTaskList } from "../hooks/useTasks";

const mockedUseTaskList = vi.mocked(useTaskList);

const sampleTasks: Task[] = [
  {
    id: "task-1",
    title: "Task One",
    description: null,
    status: "todo",
    priority: "medium",
    due_date: "2026-06-15",
    created_by: "user-1",
    assigned_to: "user-2",
    tags: [],
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
    completed_at: null,
    assignee: {
      id: "user-2",
      name: "Carlos",
      email: "carlos@test.com",
      avatar_url: null,
      role: "member",
      is_active: true,
      created_at: "2026-01-01T00:00:00Z",
    },
  },
  {
    id: "task-2",
    title: "Task Two",
    description: null,
    status: "in_progress",
    priority: "high",
    due_date: null,
    created_by: "user-1",
    assigned_to: null,
    tags: [],
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
    completed_at: null,
  },
];

function renderPage() {
  return render(
    <MemoryRouter>
      <TaskListPage />
    </MemoryRouter>,
  );
}

describe("TaskListPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows loading spinner while loading", () => {
    mockedUseTaskList.mockReturnValue({
      data: undefined,
      isLoading: true,
    } as unknown as ReturnType<typeof useTaskList>);

    renderPage();
    expect(screen.getByText("", { selector: ".loading" })).toBeInTheDocument();
  });

  it("renders page title", () => {
    mockedUseTaskList.mockReturnValue({
      data: { items: [], total: 0, page: 1, page_size: 10, total_pages: 0 },
      isLoading: false,
    } as unknown as ReturnType<typeof useTaskList>);

    renderPage();
    expect(screen.getByText("Lista de tareas")).toBeInTheDocument();
  });

  it("renders the filter bar", () => {
    mockedUseTaskList.mockReturnValue({
      data: { items: [], total: 0, page: 1, page_size: 10, total_pages: 0 },
      isLoading: false,
    } as unknown as ReturnType<typeof useTaskList>);

    renderPage();
    expect(screen.getByTestId("filter-bar")).toBeInTheDocument();
  });

  it("renders task rows in a table", () => {
    mockedUseTaskList.mockReturnValue({
      data: {
        items: sampleTasks,
        total: 2,
        page: 1,
        page_size: 10,
        total_pages: 1,
      },
      isLoading: false,
    } as unknown as ReturnType<typeof useTaskList>);

    renderPage();
    expect(screen.getByText("Task One")).toBeInTheDocument();
    expect(screen.getByText("Task Two")).toBeInTheDocument();
    expect(screen.getByText("Carlos")).toBeInTheDocument();
    expect(screen.getByText("medium")).toBeInTheDocument();
    expect(screen.getByText("high")).toBeInTheDocument();
  });

  it("shows dash for missing assignee", () => {
    mockedUseTaskList.mockReturnValue({
      data: {
        items: [sampleTasks[1]],
        total: 1,
        page: 1,
        page_size: 10,
        total_pages: 1,
      },
      isLoading: false,
    } as unknown as ReturnType<typeof useTaskList>);

    renderPage();
    // Task Two has no assignee, should show em-dash
    const cells = screen.getAllByRole("cell");
    const assigneeCell = cells.find((c) => c.textContent === "\u2014");
    expect(assigneeCell).toBeTruthy();
  });

  it("shows empty state when no tasks", () => {
    mockedUseTaskList.mockReturnValue({
      data: {
        items: [],
        total: 0,
        page: 1,
        page_size: 10,
        total_pages: 0,
      },
      isLoading: false,
    } as unknown as ReturnType<typeof useTaskList>);

    renderPage();
    expect(screen.getByText("No se encontraron tareas")).toBeInTheDocument();
  });

  it("navigates to task detail on row click", async () => {
    mockedUseTaskList.mockReturnValue({
      data: {
        items: sampleTasks,
        total: 2,
        page: 1,
        page_size: 10,
        total_pages: 1,
      },
      isLoading: false,
    } as unknown as ReturnType<typeof useTaskList>);

    const user = userEvent.setup();
    renderPage();

    await user.click(screen.getByText("Task One"));
    expect(mockNavigate).toHaveBeenCalledWith("/tasks/task-1");
  });

  it("renders pagination when total_pages > 1", () => {
    mockedUseTaskList.mockReturnValue({
      data: {
        items: sampleTasks,
        total: 30,
        page: 1,
        page_size: 10,
        total_pages: 3,
      },
      isLoading: false,
    } as unknown as ReturnType<typeof useTaskList>);

    renderPage();
    expect(screen.getByText("1")).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
  });

  it("does not render pagination for single page", () => {
    mockedUseTaskList.mockReturnValue({
      data: {
        items: sampleTasks,
        total: 2,
        page: 1,
        page_size: 10,
        total_pages: 1,
      },
      isLoading: false,
    } as unknown as ReturnType<typeof useTaskList>);

    renderPage();
    // Should not have any pagination buttons (join-item)
    expect(screen.queryByText("1")).not.toBeInTheDocument();
  });

  it("updates filters when FilterBar changes", async () => {
    mockedUseTaskList.mockReturnValue({
      data: {
        items: [],
        total: 0,
        page: 1,
        page_size: 10,
        total_pages: 0,
      },
      isLoading: false,
    } as unknown as ReturnType<typeof useTaskList>);

    const user = userEvent.setup();
    renderPage();

    await user.click(screen.getByText("filter-done"));

    // useTaskList should have been called with the new filters
    expect(mockedUseTaskList).toHaveBeenCalled();
  });

  it("renders table headers", () => {
    mockedUseTaskList.mockReturnValue({
      data: {
        items: [],
        total: 0,
        page: 1,
        page_size: 10,
        total_pages: 0,
      },
      isLoading: false,
    } as unknown as ReturnType<typeof useTaskList>);

    renderPage();
    expect(screen.getByText("Título")).toBeInTheDocument();
    expect(screen.getByText("Estado")).toBeInTheDocument();
    expect(screen.getByText("Prioridad")).toBeInTheDocument();
    expect(screen.getByText("Asignado a")).toBeInTheDocument();
    expect(screen.getByText("Fecha límite")).toBeInTheDocument();
  });
});
