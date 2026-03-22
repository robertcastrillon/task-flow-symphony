import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MemoryRouter } from "react-router-dom";
import Layout from "./Layout";

const mockLogout = vi.fn();
const mockUser = {
  id: "user-1",
  name: "Ana García",
  email: "ana@test.com",
  avatar_url: null,
  role: "admin" as const,
  is_active: true,
  created_at: "2026-01-01T00:00:00Z",
};

vi.mock("../hooks/useAuth", () => ({
  useAuth: () => ({
    user: mockUser,
    logout: mockLogout,
  }),
}));

function renderLayout() {
  return render(
    <MemoryRouter>
      <Layout />
    </MemoryRouter>,
  );
}

describe("Layout", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the app title", () => {
    renderLayout();
    expect(screen.getByText("TaskFlow")).toBeInTheDocument();
  });

  it("renders navigation links", () => {
    renderLayout();
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Tablero")).toBeInTheDocument();
    expect(screen.getByText("Lista")).toBeInTheDocument();
    expect(screen.getByText("Equipo")).toBeInTheDocument();
  });

  it("renders user info in sidebar", () => {
    renderLayout();
    expect(screen.getByText("Ana García")).toBeInTheDocument();
    expect(screen.getByText("ana@test.com")).toBeInTheDocument();
  });

  it("renders user avatar initial", () => {
    renderLayout();
    expect(screen.getByText("A")).toBeInTheDocument();
  });

  it("renders logout button", () => {
    renderLayout();
    expect(screen.getByText("Cerrar sesión")).toBeInTheDocument();
  });

  it("calls logout when button is clicked", async () => {
    const user = userEvent.setup();
    renderLayout();

    await user.click(screen.getByText("Cerrar sesión"));
    expect(mockLogout).toHaveBeenCalledOnce();
  });

  it("renders navigation links with correct paths", () => {
    renderLayout();
    const dashboardLink = screen.getByText("Dashboard").closest("a");
    const tableroLink = screen.getByText("Tablero").closest("a");
    const listaLink = screen.getByText("Lista").closest("a");
    const equipoLink = screen.getByText("Equipo").closest("a");

    expect(dashboardLink).toHaveAttribute("href", "/dashboard");
    expect(tableroLink).toHaveAttribute("href", "/tasks/board");
    expect(listaLink).toHaveAttribute("href", "/tasks/list");
    expect(equipoLink).toHaveAttribute("href", "/team");
  });
});
