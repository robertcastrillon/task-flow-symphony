import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import KanbanBoard from "./KanbanBoard";
import type { Task } from "../types";

// Mock dnd-kit to avoid complex drag-and-drop setup in tests
vi.mock("@dnd-kit/core", () => ({
  DndContext: ({ children }: { children: React.ReactNode }) => (
    <div>{children}</div>
  ),
  DragOverlay: ({ children }: { children: React.ReactNode }) => (
    <div>{children}</div>
  ),
  closestCorners: vi.fn(),
}));

vi.mock("@dnd-kit/sortable", () => ({
  SortableContext: ({ children }: { children: React.ReactNode }) => (
    <div>{children}</div>
  ),
  verticalListSortingStrategy: {},
  useSortable: () => ({
    attributes: {},
    listeners: {},
    setNodeRef: vi.fn(),
    transform: null,
    transition: null,
  }),
}));

vi.mock("@dnd-kit/utilities", () => ({
  CSS: {
    Transform: {
      toString: () => undefined,
    },
  },
}));

const sampleTasks: Task[] = [
  {
    id: "t1",
    title: "Todo task",
    description: null,
    status: "todo",
    priority: "low",
    due_date: null,
    created_by: "u1",
    assigned_to: null,
    tags: [],
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
    completed_at: null,
  },
  {
    id: "t2",
    title: "In progress task",
    description: null,
    status: "in_progress",
    priority: "medium",
    due_date: null,
    created_by: "u1",
    assigned_to: null,
    tags: [],
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
    completed_at: null,
  },
  {
    id: "t3",
    title: "Done task",
    description: null,
    status: "done",
    priority: "high",
    due_date: null,
    created_by: "u1",
    assigned_to: null,
    tags: [],
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
    completed_at: null,
  },
];

describe("KanbanBoard", () => {
  const mockOnStatusChange = vi.fn();
  const mockOnTaskClick = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders three columns with labels", () => {
    render(<KanbanBoard tasks={[]} onStatusChange={mockOnStatusChange} />);

    expect(screen.getByText("Por hacer")).toBeInTheDocument();
    expect(screen.getByText("En progreso")).toBeInTheDocument();
    expect(screen.getByText("Hecho")).toBeInTheDocument();
  });

  it("renders tasks in correct columns", () => {
    render(
      <KanbanBoard
        tasks={sampleTasks}
        onStatusChange={mockOnStatusChange}
        onTaskClick={mockOnTaskClick}
      />,
    );

    expect(screen.getByText("Todo task")).toBeInTheDocument();
    expect(screen.getByText("In progress task")).toBeInTheDocument();
    expect(screen.getByText("Done task")).toBeInTheDocument();
  });

  it("shows task count badges for each column", () => {
    render(
      <KanbanBoard tasks={sampleTasks} onStatusChange={mockOnStatusChange} />,
    );

    // Each column should show the count of tasks
    const badges = screen.getAllByText("1");
    expect(badges.length).toBe(3); // 1 task in each column
  });

  it("shows correct count for multiple tasks in same column", () => {
    const tasksWithMultipleTodo: Task[] = [
      ...sampleTasks,
      {
        ...sampleTasks[0],
        id: "t4",
        title: "Another todo",
      },
    ];

    render(
      <KanbanBoard
        tasks={tasksWithMultipleTodo}
        onStatusChange={mockOnStatusChange}
      />,
    );

    expect(screen.getByText("2")).toBeInTheDocument(); // todo column
  });

  it("renders empty columns with 0 count", () => {
    render(<KanbanBoard tasks={[]} onStatusChange={mockOnStatusChange} />);

    const zeroBadges = screen.getAllByText("0");
    expect(zeroBadges.length).toBe(3);
  });

  it("renders column test IDs", () => {
    render(<KanbanBoard tasks={[]} onStatusChange={mockOnStatusChange} />);

    expect(screen.getByTestId("column-todo")).toBeInTheDocument();
    expect(screen.getByTestId("column-in_progress")).toBeInTheDocument();
    expect(screen.getByTestId("column-done")).toBeInTheDocument();
  });

  it("does not show cancelled column", () => {
    render(<KanbanBoard tasks={[]} onStatusChange={mockOnStatusChange} />);

    expect(screen.queryByTestId("column-cancelled")).not.toBeInTheDocument();
  });

  it("filters out cancelled tasks from visible columns", () => {
    const cancelledTask: Task = {
      ...sampleTasks[0],
      id: "t5",
      title: "Cancelled task",
      status: "cancelled",
    };

    render(
      <KanbanBoard
        tasks={[...sampleTasks, cancelledTask]}
        onStatusChange={mockOnStatusChange}
      />,
    );

    // Cancelled tasks are not in any column
    expect(screen.queryByText("Cancelled task")).not.toBeInTheDocument();
  });
});
