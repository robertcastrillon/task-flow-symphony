import { render, screen } from "@testing-library/react";
<<<<<<< HEAD
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
    expect(screen.getByText("Iniciar sesión")).toBeInTheDocument();
=======
import { describe, it, expect } from "vitest";
import App from "./App";

describe("App", () => {
  it("renders the app title", () => {
    render(<App />);
    expect(screen.getByText("TaskFlow")).toBeInTheDocument();
  });

  it("renders the subtitle", () => {
    render(<App />);
    expect(
      screen.getByText("Task management for teams"),
    ).toBeInTheDocument();
>>>>>>> origin/eng-88
  });
});
