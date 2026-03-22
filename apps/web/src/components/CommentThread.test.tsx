import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import CommentThread from "./CommentThread";
import type { Comment } from "../types";

const mockMutate = vi.fn();

vi.mock("../hooks/useComments", () => ({
  useComments: vi.fn(),
  useCreateComment: vi.fn(),
}));

import { useComments, useCreateComment } from "../hooks/useComments";

const mockedUseComments = vi.mocked(useComments);
const mockedUseCreateComment = vi.mocked(useCreateComment);

const sampleComments: Comment[] = [
  {
    id: "c1",
    task_id: "task-1",
    author_id: "user-1",
    content: "This is the first comment",
    created_at: "2026-01-01T10:00:00Z",
    updated_at: "2026-01-01T10:00:00Z",
    author: {
      id: "user-1",
      name: "Ana",
      email: "ana@test.com",
      avatar_url: null,
      role: "member",
      is_active: true,
      created_at: "2026-01-01T00:00:00Z",
    },
  },
  {
    id: "c2",
    task_id: "task-1",
    author_id: "user-2",
    content: "Second comment here",
    created_at: "2026-01-02T10:00:00Z",
    updated_at: "2026-01-02T10:00:00Z",
    author: {
      id: "user-2",
      name: "Pedro",
      email: "pedro@test.com",
      avatar_url: null,
      role: "admin",
      is_active: true,
      created_at: "2026-01-01T00:00:00Z",
    },
  },
];

describe("CommentThread", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockedUseCreateComment.mockReturnValue({
      mutate: mockMutate,
      isPending: false,
    } as ReturnType<typeof useCreateComment>);
  });

  it("shows loading spinner while loading", () => {
    mockedUseComments.mockReturnValue({
      data: undefined,
      isLoading: true,
    } as ReturnType<typeof useComments>);

    render(<CommentThread taskId="task-1" />);
    expect(screen.getByText("", { selector: ".loading" })).toBeInTheDocument();
  });

  it("renders comments list", () => {
    mockedUseComments.mockReturnValue({
      data: sampleComments,
      isLoading: false,
    } as ReturnType<typeof useComments>);

    render(<CommentThread taskId="task-1" />);
    expect(screen.getByText("Comentarios")).toBeInTheDocument();
    expect(screen.getByText("This is the first comment")).toBeInTheDocument();
    expect(screen.getByText("Second comment here")).toBeInTheDocument();
    expect(screen.getByText("Ana")).toBeInTheDocument();
    expect(screen.getByText("Pedro")).toBeInTheDocument();
  });

  it("shows author avatar initials", () => {
    mockedUseComments.mockReturnValue({
      data: sampleComments,
      isLoading: false,
    } as ReturnType<typeof useComments>);

    render(<CommentThread taskId="task-1" />);
    expect(screen.getByText("A")).toBeInTheDocument();
    expect(screen.getByText("P")).toBeInTheDocument();
  });

  it("shows empty state when no comments", () => {
    mockedUseComments.mockReturnValue({
      data: [],
      isLoading: false,
    } as ReturnType<typeof useComments>);

    render(<CommentThread taskId="task-1" />);
    expect(screen.getByText("No hay comentarios aún.")).toBeInTheDocument();
  });

  it("renders the comment form", () => {
    mockedUseComments.mockReturnValue({
      data: [],
      isLoading: false,
    } as ReturnType<typeof useComments>);

    render(<CommentThread taskId="task-1" />);
    expect(
      screen.getByPlaceholderText("Escribe un comentario..."),
    ).toBeInTheDocument();
    expect(screen.getByText("Enviar")).toBeInTheDocument();
  });

  it("submits a new comment", async () => {
    mockedUseComments.mockReturnValue({
      data: [],
      isLoading: false,
    } as ReturnType<typeof useComments>);

    const user = userEvent.setup();
    render(<CommentThread taskId="task-1" />);

    await user.type(
      screen.getByPlaceholderText("Escribe un comentario..."),
      "New comment text",
    );
    await user.click(screen.getByText("Enviar"));

    await waitFor(() => {
      expect(mockMutate).toHaveBeenCalledWith(
        { content: "New comment text", taskId: "task-1" },
        expect.objectContaining({ onSuccess: expect.any(Function) }),
      );
    });
  });

  it("disables submit button when creating comment", () => {
    mockedUseComments.mockReturnValue({
      data: [],
      isLoading: false,
    } as ReturnType<typeof useComments>);
    mockedUseCreateComment.mockReturnValue({
      mutate: mockMutate,
      isPending: true,
    } as ReturnType<typeof useCreateComment>);

    render(<CommentThread taskId="task-1" />);
    expect(screen.getByText("Enviar")).toBeDisabled();
  });

  it("shows fallback for comment without author", () => {
    const commentNoAuthor: Comment = {
      id: "c3",
      task_id: "task-1",
      author_id: "user-3",
      content: "Anonymous comment",
      created_at: "2026-01-03T10:00:00Z",
      updated_at: "2026-01-03T10:00:00Z",
    };
    mockedUseComments.mockReturnValue({
      data: [commentNoAuthor],
      isLoading: false,
    } as ReturnType<typeof useComments>);

    render(<CommentThread taskId="task-1" />);
    expect(screen.getByText("Usuario")).toBeInTheDocument();
    expect(screen.getByText("?")).toBeInTheDocument();
  });
});
