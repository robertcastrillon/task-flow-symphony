import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createElement, type ReactNode } from "react";
import { useDashboardStats } from "./useDashboard";
import type { DashboardStats } from "../types";

vi.mock("../services/api", () => ({
  default: {
    get: vi.fn(),
  },
}));

import api from "../services/api";

const mockedApi = vi.mocked(api);

const mockStats: DashboardStats = {
  total_tasks: 25,
  tasks_by_status: {
    todo: 10,
    in_progress: 8,
    done: 5,
    cancelled: 2,
  },
  tasks_by_user: {
    "user-1": 12,
    "user-2": 13,
  },
  overdue_tasks: 3,
};

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  return function Wrapper({ children }: { children: ReactNode }) {
    return createElement(
      QueryClientProvider,
      { client: queryClient },
      children,
    );
  };
}

describe("useDashboard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("useDashboardStats", () => {
    it("fetches dashboard stats", async () => {
      mockedApi.get.mockResolvedValueOnce({ data: mockStats });

      const { result } = renderHook(() => useDashboardStats(), {
        wrapper: createWrapper(),
      });

      expect(result.current.isLoading).toBe(true);

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockStats);
      expect(mockedApi.get).toHaveBeenCalledWith("/dashboard/stats");
    });

    it("handles fetch error", async () => {
      mockedApi.get.mockRejectedValueOnce(new Error("Server error"));

      const { result } = renderHook(() => useDashboardStats(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error).toBeDefined();
    });

    it("starts in loading state", () => {
      mockedApi.get.mockReturnValue(new Promise(() => {}));

      const { result } = renderHook(() => useDashboardStats(), {
        wrapper: createWrapper(),
      });

      expect(result.current.isLoading).toBe(true);
      expect(result.current.data).toBeUndefined();
    });
  });
});
