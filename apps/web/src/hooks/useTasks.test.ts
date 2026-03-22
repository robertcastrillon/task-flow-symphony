import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createElement, type ReactNode } from "react";
import {
  useTaskList,
  useTask,
  useCreateTask,
  useUpdateTask,
  useDeleteTask,
  useChangeStatus,
  useAssignTask,
} from "./useTasks";
import type { Task, PaginatedResponse } from "../types";

vi.mock("../services/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}));

import api from "../services/api";

const mockedApi = vi.mocked(api, { deep: true });

const mockTask: Task = {
  id: "task-1",
  title: "Test Task",
  description: "A test task",
  status: "todo",
  priority: "medium",
  due_date: null,
  created_by: "user-1",
  assigned_to: null,
  tags: ["test"],
  created_at: "2025-01-01T00:00:00Z",
  updated_at: "2025-01-01T00:00:00Z",
  completed_at: null,
};

const mockPaginatedResponse: PaginatedResponse<Task> = {
  items: [mockTask],
  total: 1,
  page: 1,
  page_size: 10,
  total_pages: 1,
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

describe("useTasks", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("useTaskList", () => {
    it("fetches tasks with no filters", async () => {
      mockedApi.get.mockResolvedValueOnce({ data: mockPaginatedResponse });

      const { result } = renderHook(() => useTaskList(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockPaginatedResponse);
      expect(mockedApi.get).toHaveBeenCalledWith("/tasks?");
    });

    it("fetches tasks with filters", async () => {
      mockedApi.get.mockResolvedValueOnce({ data: mockPaginatedResponse });

      const { result } = renderHook(
        () =>
          useTaskList({
            status: "todo",
            priority: "high",
            assignee: "user-1",
            tag: "urgent",
            search: "test",
            page: 2,
            page_size: 20,
          }),
        { wrapper: createWrapper() },
      );

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      const calledUrl = (mockedApi.get as ReturnType<typeof vi.fn>).mock
        .calls[0][0] as string;
      expect(calledUrl).toContain("status=todo");
      expect(calledUrl).toContain("priority=high");
      expect(calledUrl).toContain("assignee=user-1");
      expect(calledUrl).toContain("tag=urgent");
      expect(calledUrl).toContain("search=test");
      expect(calledUrl).toContain("page=2");
      expect(calledUrl).toContain("page_size=20");
    });

    it("handles fetch error", async () => {
      mockedApi.get.mockRejectedValueOnce(new Error("Network error"));

      const { result } = renderHook(() => useTaskList(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error).toBeDefined();
    });
  });

  describe("useTask", () => {
    it("fetches a single task by id", async () => {
      mockedApi.get.mockResolvedValueOnce({ data: mockTask });

      const { result } = renderHook(() => useTask("task-1"), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockTask);
      expect(mockedApi.get).toHaveBeenCalledWith("/tasks/task-1");
    });

    it("does not fetch when id is empty", () => {
      const { result } = renderHook(() => useTask(""), {
        wrapper: createWrapper(),
      });

      expect(result.current.fetchStatus).toBe("idle");
      expect(mockedApi.get).not.toHaveBeenCalled();
    });
  });

  describe("useCreateTask", () => {
    it("creates a task and invalidates cache", async () => {
      mockedApi.post.mockResolvedValueOnce({ data: mockTask });

      const { result } = renderHook(() => useCreateTask(), {
        wrapper: createWrapper(),
      });

      await result.current.mutateAsync({
        title: "New Task",
        priority: "medium",
        status: "todo",
        tags: [],
      });

      expect(mockedApi.post).toHaveBeenCalledWith("/tasks", {
        title: "New Task",
        priority: "medium",
        status: "todo",
        tags: [],
      });
    });

    it("handles creation error", async () => {
      mockedApi.post.mockRejectedValueOnce(new Error("Validation error"));

      const { result } = renderHook(() => useCreateTask(), {
        wrapper: createWrapper(),
      });

      await expect(
        result.current.mutateAsync({
          title: "New Task",
          priority: "medium",
          status: "todo",
          tags: [],
        }),
      ).rejects.toThrow("Validation error");
    });
  });

  describe("useUpdateTask", () => {
    it("updates a task", async () => {
      const updatedTask = { ...mockTask, title: "Updated Task" };
      mockedApi.patch.mockResolvedValueOnce({ data: updatedTask });

      const { result } = renderHook(() => useUpdateTask(), {
        wrapper: createWrapper(),
      });

      const data = await result.current.mutateAsync({
        id: "task-1",
        title: "Updated Task",
      });

      expect(mockedApi.patch).toHaveBeenCalledWith("/tasks/task-1", {
        title: "Updated Task",
      });
      expect(data).toEqual(updatedTask);
    });
  });

  describe("useDeleteTask", () => {
    it("deletes a task", async () => {
      mockedApi.delete.mockResolvedValueOnce({});

      const { result } = renderHook(() => useDeleteTask(), {
        wrapper: createWrapper(),
      });

      await result.current.mutateAsync("task-1");

      expect(mockedApi.delete).toHaveBeenCalledWith("/tasks/task-1");
    });

    it("handles deletion error", async () => {
      mockedApi.delete.mockRejectedValueOnce(new Error("Not found"));

      const { result } = renderHook(() => useDeleteTask(), {
        wrapper: createWrapper(),
      });

      await expect(result.current.mutateAsync("nonexistent")).rejects.toThrow(
        "Not found",
      );
    });
  });

  describe("useChangeStatus", () => {
    it("changes task status", async () => {
      const updatedTask = { ...mockTask, status: "done" as const };
      mockedApi.patch.mockResolvedValueOnce({ data: updatedTask });

      const { result } = renderHook(() => useChangeStatus(), {
        wrapper: createWrapper(),
      });

      const data = await result.current.mutateAsync({
        id: "task-1",
        status: "done",
      });

      expect(mockedApi.patch).toHaveBeenCalledWith("/tasks/task-1/status", {
        status: "done",
      });
      expect(data).toEqual(updatedTask);
    });
  });

  describe("useAssignTask", () => {
    it("assigns a task to a user", async () => {
      const updatedTask = { ...mockTask, assigned_to: "user-2" };
      mockedApi.patch.mockResolvedValueOnce({ data: updatedTask });

      const { result } = renderHook(() => useAssignTask(), {
        wrapper: createWrapper(),
      });

      const data = await result.current.mutateAsync({
        id: "task-1",
        assigned_to: "user-2",
      });

      expect(mockedApi.patch).toHaveBeenCalledWith("/tasks/task-1/assign", {
        assigned_to: "user-2",
      });
      expect(data).toEqual(updatedTask);
    });

    it("unassigns a task", async () => {
      const updatedTask = { ...mockTask, assigned_to: null };
      mockedApi.patch.mockResolvedValueOnce({ data: updatedTask });

      const { result } = renderHook(() => useAssignTask(), {
        wrapper: createWrapper(),
      });

      await result.current.mutateAsync({
        id: "task-1",
        assigned_to: null,
      });

      expect(mockedApi.patch).toHaveBeenCalledWith("/tasks/task-1/assign", {
        assigned_to: null,
      });
    });
  });
});
