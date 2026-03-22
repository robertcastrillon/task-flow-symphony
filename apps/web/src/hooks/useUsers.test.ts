import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createElement, type ReactNode } from "react";
import { useUsers, useUser, useUpdateProfile } from "./useUsers";
import type { User } from "../types";

vi.mock("../services/api", () => ({
  default: {
    get: vi.fn(),
    patch: vi.fn(),
  },
}));

import api from "../services/api";

const mockedApi = vi.mocked(api, { deep: true });

const mockUser: User = {
  id: "user-1",
  email: "test@example.com",
  name: "Test User",
  avatar_url: null,
  role: "member",
  is_active: true,
  created_at: "2025-01-01T00:00:00Z",
};

const mockUsers: User[] = [
  mockUser,
  {
    id: "user-2",
    email: "admin@example.com",
    name: "Admin User",
    avatar_url: "https://example.com/avatar.png",
    role: "admin",
    is_active: true,
    created_at: "2025-01-01T00:00:00Z",
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

describe("useUsers", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("useUsers", () => {
    it("fetches list of users", async () => {
      mockedApi.get.mockResolvedValueOnce({ data: mockUsers });

      const { result } = renderHook(() => useUsers(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockUsers);
      expect(mockedApi.get).toHaveBeenCalledWith("/users");
    });

    it("handles fetch error", async () => {
      mockedApi.get.mockRejectedValueOnce(new Error("Server error"));

      const { result } = renderHook(() => useUsers(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error).toBeDefined();
    });
  });

  describe("useUser", () => {
    it("fetches a single user by id", async () => {
      mockedApi.get.mockResolvedValueOnce({ data: mockUser });

      const { result } = renderHook(() => useUser("user-1"), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockUser);
      expect(mockedApi.get).toHaveBeenCalledWith("/users/user-1");
    });

    it("does not fetch when id is empty", () => {
      const { result } = renderHook(() => useUser(""), {
        wrapper: createWrapper(),
      });

      expect(result.current.fetchStatus).toBe("idle");
      expect(mockedApi.get).not.toHaveBeenCalled();
    });
  });

  describe("useUpdateProfile", () => {
    it("updates user profile with name", async () => {
      const updatedUser = { ...mockUser, name: "Updated Name" };
      mockedApi.patch.mockResolvedValueOnce({ data: updatedUser });

      const { result } = renderHook(() => useUpdateProfile(), {
        wrapper: createWrapper(),
      });

      const data = await result.current.mutateAsync({
        id: "user-1",
        name: "Updated Name",
      });

      expect(mockedApi.patch).toHaveBeenCalledWith("/users/user-1", {
        name: "Updated Name",
      });
      expect(data).toEqual(updatedUser);
    });

    it("updates user profile with avatar_url", async () => {
      const updatedUser = {
        ...mockUser,
        avatar_url: "https://example.com/new-avatar.png",
      };
      mockedApi.patch.mockResolvedValueOnce({ data: updatedUser });

      const { result } = renderHook(() => useUpdateProfile(), {
        wrapper: createWrapper(),
      });

      const data = await result.current.mutateAsync({
        id: "user-1",
        avatar_url: "https://example.com/new-avatar.png",
      });

      expect(mockedApi.patch).toHaveBeenCalledWith("/users/user-1", {
        avatar_url: "https://example.com/new-avatar.png",
      });
      expect(data).toEqual(updatedUser);
    });

    it("clears avatar_url by setting to null", async () => {
      const updatedUser = { ...mockUser, avatar_url: null };
      mockedApi.patch.mockResolvedValueOnce({ data: updatedUser });

      const { result } = renderHook(() => useUpdateProfile(), {
        wrapper: createWrapper(),
      });

      await result.current.mutateAsync({
        id: "user-1",
        avatar_url: null,
      });

      expect(mockedApi.patch).toHaveBeenCalledWith("/users/user-1", {
        avatar_url: null,
      });
    });

    it("handles update error", async () => {
      mockedApi.patch.mockRejectedValueOnce(new Error("Forbidden"));

      const { result } = renderHook(() => useUpdateProfile(), {
        wrapper: createWrapper(),
      });

      await expect(
        result.current.mutateAsync({ id: "user-1", name: "New Name" }),
      ).rejects.toThrow("Forbidden");
    });
  });
});
