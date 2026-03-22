import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createElement, type ReactNode } from "react";
import { useComments, useCreateComment } from "./useComments";
import type { Comment } from "../types";

vi.mock("../services/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

import api from "../services/api";

const mockedApi = vi.mocked(api);

const mockComments: Comment[] = [
  {
    id: "comment-1",
    task_id: "task-1",
    author_id: "user-1",
    content: "First comment",
    created_at: "2025-01-01T00:00:00Z",
    updated_at: "2025-01-01T00:00:00Z",
  },
  {
    id: "comment-2",
    task_id: "task-1",
    author_id: "user-2",
    content: "Second comment",
    created_at: "2025-01-02T00:00:00Z",
    updated_at: "2025-01-02T00:00:00Z",
  },
];

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

describe("useComments", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("useComments", () => {
    it("fetches comments for a task", async () => {
      mockedApi.get.mockResolvedValueOnce({ data: mockComments });

      const { result } = renderHook(() => useComments("task-1"), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockComments);
      expect(mockedApi.get).toHaveBeenCalledWith("/tasks/task-1/comments");
    });

    it("does not fetch when taskId is empty", () => {
      const { result } = renderHook(() => useComments(""), {
        wrapper: createWrapper(),
      });

      expect(result.current.fetchStatus).toBe("idle");
      expect(mockedApi.get).not.toHaveBeenCalled();
    });

    it("handles fetch error", async () => {
      mockedApi.get.mockRejectedValueOnce(new Error("Not found"));

      const { result } = renderHook(() => useComments("task-1"), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error).toBeDefined();
    });
  });

  describe("useCreateComment", () => {
    it("creates a comment for a task", async () => {
      const newComment: Comment = {
        id: "comment-3",
        task_id: "task-1",
        author_id: "user-1",
        content: "New comment",
        created_at: "2025-01-03T00:00:00Z",
        updated_at: "2025-01-03T00:00:00Z",
      };
      mockedApi.post.mockResolvedValueOnce({ data: newComment });

      const { result } = renderHook(() => useCreateComment(), {
        wrapper: createWrapper(),
      });

      const data = await result.current.mutateAsync({
        taskId: "task-1",
        content: "New comment",
      });

      expect(mockedApi.post).toHaveBeenCalledWith("/tasks/task-1/comments", {
        content: "New comment",
      });
      expect(data).toEqual(newComment);
    });

    it("handles creation error", async () => {
      mockedApi.post.mockRejectedValueOnce(new Error("Validation error"));

      const { result } = renderHook(() => useCreateComment(), {
        wrapper: createWrapper(),
      });

      await expect(
        result.current.mutateAsync({
          taskId: "task-1",
          content: "",
        }),
      ).rejects.toThrow("Validation error");
    });
  });
});
