import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import TaskCard from "./TaskCard";
import type { Task } from "../types";

const baseTask: Task = {
  id: "1",
  title: "Test task",
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
};

describe("TaskCard", () => {
  it("renders task title", () => {
    render(<TaskCard task={baseTask} />);
    expect(screen.getByText("Test task")).toBeInTheDocument();
  });

  it("renders priority badge", () => {
    render(<TaskCard task={baseTask} />);
    expect(screen.getByText("medium")).toBeInTheDocument();
  });

  it("shows overdue badge when task is past due and not done", () => {
    const overdueTask: Task = {
      ...baseTask,
      due_date: "2020-01-01",
    };
    render(<TaskCard task={overdueTask} />);
    expect(screen.getByText("Vencida")).toBeInTheDocument();
  });

  it("does not show overdue badge when task is done", () => {
    const doneTask: Task = {
      ...baseTask,
      status: "done",
      due_date: "2020-01-01",
    };
    render(<TaskCard task={doneTask} />);
    expect(screen.queryByText("Vencida")).not.toBeInTheDocument();
  });

  it("renders assignee name and avatar", () => {
    const taskWithAssignee: Task = {
      ...baseTask,
      assignee: {
        id: "user-1",
        name: "María",
        email: "maria@test.com",
        avatar_url: null,
        role: "member",
        is_active: true,
        created_at: "2026-01-01T00:00:00Z",
      },
    };
    render(<TaskCard task={taskWithAssignee} />);
    expect(screen.getByText("María")).toBeInTheDocument();
    expect(screen.getByText("M")).toBeInTheDocument();
  });

  it("calls onClick when clicked", () => {
    const onClick = vi.fn();
    render(<TaskCard task={baseTask} onClick={onClick} />);
    fireEvent.click(screen.getByRole("button"));
    expect(onClick).toHaveBeenCalledWith(baseTask);
  });

  it("renders due date", () => {
    const taskWithDate: Task = {
      ...baseTask,
      due_date: "2026-06-15",
    };
    render(<TaskCard task={taskWithDate} />);
    // The date is rendered via toLocaleDateString, format varies by environment
    const expected = new Date("2026-06-15").toLocaleDateString("es");
    expect(screen.getByText(expected)).toBeInTheDocument();
  });
});
