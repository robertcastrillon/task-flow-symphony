import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import App from "./App";

vi.mock("./hooks/useAuth", () => {
  const AuthProvider = ({ children }: { children: React.ReactNode }) => (
    <>{children}</>
  );
  return {
    AuthProvider,
    useAuth: () => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
    }),
  };
});

describe("App", () => {
  it("renders login page by default when not authenticated", () => {
    render(<App />);
    expect(screen.getByText("TaskFlow")).toBeInTheDocument();
  });
});
