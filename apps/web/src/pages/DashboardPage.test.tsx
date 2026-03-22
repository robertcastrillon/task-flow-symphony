import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import DashboardPage from "./DashboardPage";

vi.mock("../hooks/useDashboard", () => ({
  useDashboardStats: vi.fn(),
}));

import { useDashboardStats } from "../hooks/useDashboard";

const mockedUseDashboardStats = vi.mocked(useDashboardStats);

describe("DashboardPage", () => {
  it("shows loading spinner while loading", () => {
    mockedUseDashboardStats.mockReturnValue({
      data: undefined,
      isLoading: true,
    } as ReturnType<typeof useDashboardStats>);

    render(<DashboardPage />);
    expect(screen.getByText("", { selector: ".loading" })).toBeInTheDocument();
  });

  it("renders dashboard stats", () => {
    mockedUseDashboardStats.mockReturnValue({
      data: {
        total_tasks: 15,
        tasks_by_status: { todo: 5, in_progress: 3, done: 7 },
        tasks_by_user: {},
        overdue_tasks: 2,
      },
      isLoading: false,
    } as ReturnType<typeof useDashboardStats>);

    render(<DashboardPage />);
    expect(screen.getByText("15")).toBeInTheDocument();
    // "5" and "3" appear in both stat cards and status badges, so use getAllByText
    expect(screen.getAllByText("5").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("3").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("2")).toBeInTheDocument();
  });
});
