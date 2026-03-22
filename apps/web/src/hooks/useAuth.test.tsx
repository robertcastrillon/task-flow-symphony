import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act, waitFor } from "@testing-library/react";
import { AuthProvider, useAuth } from "./useAuth";
import type { ReactNode } from "react";

const mockUser = {
  id: "user-1",
  email: "test@example.com",
  name: "Test User",
  avatar_url: null,
  role: "member" as const,
  is_active: true,
  created_at: "2025-01-01T00:00:00Z",
};

const mockTokenResponse = {
  access_token: "access-token-123",
  refresh_token: "refresh-token-456",
  token_type: "bearer",
};

vi.mock("../services/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

import api from "../services/api";

const mockedApi = vi.mocked(api);

function wrapper({ children }: { children: ReactNode }) {
  return <AuthProvider>{children}</AuthProvider>;
}

describe("useAuth", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it("throws error when used outside AuthProvider", () => {
    expect(() => {
      renderHook(() => useAuth());
    }).toThrow("useAuth must be used within an AuthProvider");
  });

  it("initializes with no user and isLoading false when no token in localStorage", async () => {
    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });

  it("fetches current user when token exists in localStorage", async () => {
    localStorage.setItem("access_token", "existing-token");
    mockedApi.get.mockResolvedValueOnce({ data: mockUser });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.user).toEqual(mockUser);
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.token).toBe("existing-token");
    expect(mockedApi.get).toHaveBeenCalledWith("/auth/me");
  });

  it("clears token and user when fetchCurrentUser fails", async () => {
    localStorage.setItem("access_token", "bad-token");
    localStorage.setItem("refresh_token", "bad-refresh");
    mockedApi.get.mockRejectedValueOnce(new Error("Unauthorized"));

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(localStorage.getItem("access_token")).toBeNull();
    expect(localStorage.getItem("refresh_token")).toBeNull();
  });

  it("login stores tokens and fetches user", async () => {
    mockedApi.post.mockResolvedValueOnce({ data: mockTokenResponse });
    // login calls api.get("/auth/me") directly, then the useEffect also
    // calls fetchCurrentUser when token changes, so we need two mocks
    mockedApi.get.mockResolvedValue({ data: mockUser });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    await act(async () => {
      await result.current.login({
        email: "test@example.com",
        password: "password123",
      });
    });

    expect(mockedApi.post).toHaveBeenCalledWith("/auth/login", {
      email: "test@example.com",
      password: "password123",
    });

    await waitFor(() => {
      expect(result.current.user).toEqual(mockUser);
    });

    expect(localStorage.getItem("access_token")).toBe("access-token-123");
    expect(localStorage.getItem("refresh_token")).toBe("refresh-token-456");
    expect(result.current.isAuthenticated).toBe(true);
  });

  it("login propagates API errors", async () => {
    mockedApi.post.mockRejectedValueOnce(new Error("Invalid credentials"));

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    await expect(
      act(async () => {
        await result.current.login({
          email: "bad@example.com",
          password: "wrong",
        });
      }),
    ).rejects.toThrow("Invalid credentials");
  });

  it("register calls API with form data", async () => {
    mockedApi.post.mockResolvedValueOnce({ data: {} });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    await act(async () => {
      await result.current.register({
        email: "new@example.com",
        name: "New User",
        password: "password123",
      });
    });

    expect(mockedApi.post).toHaveBeenCalledWith("/auth/register", {
      email: "new@example.com",
      name: "New User",
      password: "password123",
    });
  });

  it("register propagates API errors", async () => {
    mockedApi.post.mockRejectedValueOnce(new Error("Email already exists"));

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    await expect(
      act(async () => {
        await result.current.register({
          email: "existing@example.com",
          name: "User",
          password: "password123",
        });
      }),
    ).rejects.toThrow("Email already exists");
  });

  it("logout clears tokens and user", async () => {
    localStorage.setItem("access_token", "existing-token");
    mockedApi.get.mockResolvedValueOnce({ data: mockUser });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.isAuthenticated).toBe(true);
    });

    act(() => {
      result.current.logout();
    });

    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(localStorage.getItem("access_token")).toBeNull();
    expect(localStorage.getItem("refresh_token")).toBeNull();
  });
});
