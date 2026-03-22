import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import TeamPage from "./TeamPage";

vi.mock("../hooks/useUsers", () => ({
  useUsers: vi.fn(),
}));

import { useUsers } from "../hooks/useUsers";

const mockedUseUsers = vi.mocked(useUsers);

describe("TeamPage", () => {
  it("shows loading spinner while loading", () => {
    mockedUseUsers.mockReturnValue({
      data: undefined,
      isLoading: true,
    } as unknown as ReturnType<typeof useUsers>);

    render(<TeamPage />);
    expect(screen.getByText("", { selector: ".loading" })).toBeInTheDocument();
  });

  it("renders team members", () => {
    mockedUseUsers.mockReturnValue({
      data: [
        {
          id: "1",
          name: "María García",
          email: "maria@test.com",
          avatar_url: null,
          role: "member",
          is_active: true,
          created_at: "2026-01-01T00:00:00Z",
        },
        {
          id: "2",
          name: "Luis Admin",
          email: "luis@test.com",
          avatar_url: null,
          role: "admin",
          is_active: true,
          created_at: "2026-01-01T00:00:00Z",
        },
      ],
      isLoading: false,
    } as unknown as ReturnType<typeof useUsers>);

    render(<TeamPage />);
    expect(screen.getByText("María García")).toBeInTheDocument();
    expect(screen.getByText("Luis Admin")).toBeInTheDocument();
    expect(screen.getByText("member")).toBeInTheDocument();
    expect(screen.getByText("admin")).toBeInTheDocument();
  });

  it("shows empty message when no users", () => {
    mockedUseUsers.mockReturnValue({
      data: [],
      isLoading: false,
    } as unknown as ReturnType<typeof useUsers>);

    render(<TeamPage />);
    expect(
      screen.getByText("No hay miembros en el equipo."),
    ).toBeInTheDocument();
  });
});
