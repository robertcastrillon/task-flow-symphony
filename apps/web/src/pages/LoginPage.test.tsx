import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MemoryRouter } from "react-router-dom";
import LoginPage from "./LoginPage";
import { AxiosError, AxiosHeaders } from "axios";

const mockLogin = vi.fn();
const mockNavigate = vi.fn();

vi.mock("../hooks/useAuth", () => ({
  useAuth: () => ({
    login: mockLogin,
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
      <LoginPage />
    </MemoryRouter>,
  );
}

describe("LoginPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the login form", () => {
    renderPage();
    expect(screen.getByText("TaskFlow")).toBeInTheDocument();
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByLabelText("Contraseña")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /Iniciar sesión/i }),
    ).toBeInTheDocument();
  });

  it("renders link to register page", () => {
    renderPage();
    expect(screen.getByText("Regístrate")).toBeInTheDocument();
  });

  it("shows validation error for invalid email", async () => {
    renderPage();

    const emailInput = screen.getByLabelText("Email");
    const passwordInput = screen.getByLabelText("Contraseña");

    // Use fireEvent to set values, bypassing HTML5 email validation
    fireEvent.change(emailInput, { target: { value: "notanemail" } });
    fireEvent.change(passwordInput, { target: { value: "password123" } });

    // Submit the form directly to bypass native browser validation
    const form = screen
      .getByRole("button", { name: /Iniciar sesión/i })
      .closest("form")!;
    fireEvent.submit(form);

    await waitFor(() => {
      expect(screen.getByText("Email inválido")).toBeInTheDocument();
    });
  });

  it("shows validation error for short password", async () => {
    const user = userEvent.setup();
    renderPage();

    await user.type(screen.getByLabelText("Email"), "test@example.com");
    await user.type(screen.getByLabelText("Contraseña"), "short");
    await user.click(screen.getByRole("button", { name: /Iniciar sesión/i }));

    await waitFor(() => {
      expect(
        screen.getByText("La contraseña debe tener al menos 8 caracteres"),
      ).toBeInTheDocument();
    });
  });

  it("calls login and navigates to dashboard on success", async () => {
    mockLogin.mockResolvedValue(undefined);
    const user = userEvent.setup();
    renderPage();

    await user.type(screen.getByLabelText("Email"), "test@example.com");
    await user.type(screen.getByLabelText("Contraseña"), "password123");
    await user.click(screen.getByRole("button", { name: /Iniciar sesión/i }));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        email: "test@example.com",
        password: "password123",
      });
      expect(mockNavigate).toHaveBeenCalledWith("/dashboard");
    });
  });

  it("displays rate limit error for 429 status", async () => {
    const axiosError = new AxiosError("error", "ERR", undefined, undefined, {
      status: 429,
      data: {},
      statusText: "Too Many Requests",
      headers: {},
      config: { headers: new AxiosHeaders() },
    });
    mockLogin.mockRejectedValue(axiosError);
    const user = userEvent.setup();
    renderPage();

    await user.type(screen.getByLabelText("Email"), "test@example.com");
    await user.type(screen.getByLabelText("Contraseña"), "password123");
    await user.click(screen.getByRole("button", { name: /Iniciar sesión/i }));

    await waitFor(() => {
      expect(
        screen.getByText("Demasiados intentos. Intenta de nuevo en un minuto."),
      ).toBeInTheDocument();
    });
  });

  it("displays API error detail on login failure", async () => {
    const axiosError = new AxiosError("error", "ERR", undefined, undefined, {
      status: 401,
      data: { detail: "Contraseña incorrecta", code: "invalid_credentials" },
      statusText: "Unauthorized",
      headers: {},
      config: { headers: new AxiosHeaders() },
    });
    mockLogin.mockRejectedValue(axiosError);
    const user = userEvent.setup();
    renderPage();

    await user.type(screen.getByLabelText("Email"), "test@example.com");
    await user.type(screen.getByLabelText("Contraseña"), "password123");
    await user.click(screen.getByRole("button", { name: /Iniciar sesión/i }));

    await waitFor(() => {
      expect(screen.getByText("Contraseña incorrecta")).toBeInTheDocument();
    });
  });

  it("displays fallback error when AxiosError has no detail", async () => {
    const axiosError = new AxiosError("error", "ERR", undefined, undefined, {
      status: 401,
      data: {},
      statusText: "Unauthorized",
      headers: {},
      config: { headers: new AxiosHeaders() },
    });
    mockLogin.mockRejectedValue(axiosError);
    const user = userEvent.setup();
    renderPage();

    await user.type(screen.getByLabelText("Email"), "test@example.com");
    await user.type(screen.getByLabelText("Contraseña"), "password123");
    await user.click(screen.getByRole("button", { name: /Iniciar sesión/i }));

    await waitFor(() => {
      expect(screen.getByText("Credenciales inválidas")).toBeInTheDocument();
    });
  });

  it("displays generic error for non-Axios errors", async () => {
    mockLogin.mockRejectedValue(new Error("Something went wrong"));
    const user = userEvent.setup();
    renderPage();

    await user.type(screen.getByLabelText("Email"), "test@example.com");
    await user.type(screen.getByLabelText("Contraseña"), "password123");
    await user.click(screen.getByRole("button", { name: /Iniciar sesión/i }));

    await waitFor(() => {
      expect(screen.getByText("Error al iniciar sesión")).toBeInTheDocument();
    });
  });

  it("shows empty form validation errors", async () => {
    const user = userEvent.setup();
    renderPage();

    await user.click(screen.getByRole("button", { name: /Iniciar sesión/i }));

    await waitFor(() => {
      expect(screen.getByText("Email inválido")).toBeInTheDocument();
    });
  });
});
