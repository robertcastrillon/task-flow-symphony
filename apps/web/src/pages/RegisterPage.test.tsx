import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MemoryRouter } from "react-router-dom";
import RegisterPage from "./RegisterPage";
import { AxiosError, AxiosHeaders } from "axios";

const mockRegister = vi.fn();
const mockNavigate = vi.fn();

vi.mock("../hooks/useAuth", () => ({
  useAuth: () => ({
    register: mockRegister,
  }),
}));

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

function renderPage() {
  return render(
    <MemoryRouter>
      <RegisterPage />
    </MemoryRouter>,
  );
}

describe("RegisterPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the registration form", () => {
    renderPage();
    expect(screen.getByText("Crear cuenta")).toBeInTheDocument();
    expect(screen.getByLabelText("Nombre")).toBeInTheDocument();
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByLabelText("Contraseña")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /Registrarse/i }),
    ).toBeInTheDocument();
  });

  it("renders link to login page", () => {
    renderPage();
    expect(screen.getByText("Inicia sesión")).toBeInTheDocument();
  });

  it("shows validation errors for empty fields", async () => {
    const user = userEvent.setup();
    renderPage();

    await user.click(screen.getByRole("button", { name: /Registrarse/i }));

    await waitFor(() => {
      expect(screen.getByText("El nombre es obligatorio")).toBeInTheDocument();
    });
  });

  it("shows validation error for invalid email", async () => {
    renderPage();

    fireEvent.change(screen.getByLabelText("Nombre"), {
      target: { value: "Test User" },
    });
    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "notanemail" },
    });
    fireEvent.change(screen.getByLabelText("Contraseña"), {
      target: { value: "password123" },
    });

    const form = screen
      .getByRole("button", { name: /Registrarse/i })
      .closest("form")!;
    fireEvent.submit(form);

    await waitFor(() => {
      expect(screen.getByText("Email inválido")).toBeInTheDocument();
    });
  });

  it("shows validation error for short password", async () => {
    const user = userEvent.setup();
    renderPage();

    await user.type(screen.getByLabelText("Nombre"), "Test User");
    await user.type(screen.getByLabelText("Email"), "test@example.com");
    await user.type(screen.getByLabelText("Contraseña"), "short");
    await user.click(screen.getByRole("button", { name: /Registrarse/i }));

    await waitFor(() => {
      expect(
        screen.getByText("La contraseña debe tener al menos 8 caracteres"),
      ).toBeInTheDocument();
    });
  });

  it("calls register and navigates to login on success", async () => {
    mockRegister.mockResolvedValue(undefined);
    const user = userEvent.setup();
    renderPage();

    await user.type(screen.getByLabelText("Nombre"), "Test User");
    await user.type(screen.getByLabelText("Email"), "test@example.com");
    await user.type(screen.getByLabelText("Contraseña"), "password123");
    await user.click(screen.getByRole("button", { name: /Registrarse/i }));

    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith({
        name: "Test User",
        email: "test@example.com",
        password: "password123",
      });
      expect(mockNavigate).toHaveBeenCalledWith("/login");
    });
  });

  it("displays API error message on registration failure", async () => {
    const axiosError = new AxiosError("error", "ERR", undefined, undefined, {
      status: 400,
      data: { detail: "Email ya registrado", code: "duplicate" },
      statusText: "Bad Request",
      headers: {},
      config: { headers: new AxiosHeaders() },
    });
    mockRegister.mockRejectedValue(axiosError);
    const user = userEvent.setup();
    renderPage();

    await user.type(screen.getByLabelText("Nombre"), "Test User");
    await user.type(screen.getByLabelText("Email"), "test@example.com");
    await user.type(screen.getByLabelText("Contraseña"), "password123");
    await user.click(screen.getByRole("button", { name: /Registrarse/i }));

    await waitFor(() => {
      expect(screen.getByText("Email ya registrado")).toBeInTheDocument();
    });
  });

  it("displays generic error message for non-Axios errors", async () => {
    mockRegister.mockRejectedValue(new Error("Network error"));
    const user = userEvent.setup();
    renderPage();

    await user.type(screen.getByLabelText("Nombre"), "Test User");
    await user.type(screen.getByLabelText("Email"), "test@example.com");
    await user.type(screen.getByLabelText("Contraseña"), "password123");
    await user.click(screen.getByRole("button", { name: /Registrarse/i }));

    await waitFor(() => {
      expect(screen.getByText("Error al registrarse")).toBeInTheDocument();
    });
  });

  it("displays fallback error when AxiosError has no detail", async () => {
    const axiosError = new AxiosError("error", "ERR", undefined, undefined, {
      status: 500,
      data: {},
      statusText: "Internal Server Error",
      headers: {},
      config: { headers: new AxiosHeaders() },
    });
    mockRegister.mockRejectedValue(axiosError);
    const user = userEvent.setup();
    renderPage();

    await user.type(screen.getByLabelText("Nombre"), "Test User");
    await user.type(screen.getByLabelText("Email"), "test@example.com");
    await user.type(screen.getByLabelText("Contraseña"), "password123");
    await user.click(screen.getByRole("button", { name: /Registrarse/i }));

    await waitFor(() => {
      expect(screen.getByText("Error al registrarse")).toBeInTheDocument();
    });
  });
});
