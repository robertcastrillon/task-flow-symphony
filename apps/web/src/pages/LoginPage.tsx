import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useNavigate } from "react-router-dom";
import { loginSchema, type LoginFormData } from "../types";
import { useAuth } from "../hooks/useAuth";
import { AxiosError } from "axios";
import type { ApiError } from "../types";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  async function onSubmit(data: LoginFormData) {
    try {
      setError(null);
      await login(data);
      navigate("/dashboard");
    } catch (err) {
      if (err instanceof AxiosError && err.response?.status === 429) {
        setError("Demasiados intentos. Intenta de nuevo en un minuto.");
      } else if (err instanceof AxiosError) {
        const apiError = err.response?.data as ApiError | undefined;
        setError(apiError?.detail ?? "Credenciales inválidas");
      } else {
        setError("Error al iniciar sesión");
      }
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-base-200">
      <div className="card w-96 bg-base-100 shadow-lg">
        <div className="card-body">
          <h1 className="card-title text-2xl justify-center mb-4">TaskFlow</h1>
          {error && (
            <div className="alert alert-error text-sm" role="alert">
              {error}
            </div>
          )}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="form-control">
              <label className="label" htmlFor="email">
                <span className="label-text">Email</span>
              </label>
              <input
                id="email"
                type="email"
                className={`input input-bordered ${errors.email ? "input-error" : ""}`}
                {...register("email")}
              />
              {errors.email && (
                <label className="label">
                  <span className="label-text-alt text-error">
                    {errors.email.message}
                  </span>
                </label>
              )}
            </div>

            <div className="form-control">
              <label className="label" htmlFor="password">
                <span className="label-text">Contraseña</span>
              </label>
              <input
                id="password"
                type="password"
                className={`input input-bordered ${errors.password ? "input-error" : ""}`}
                {...register("password")}
              />
              {errors.password && (
                <label className="label">
                  <span className="label-text-alt text-error">
                    {errors.password.message}
                  </span>
                </label>
              )}
            </div>

            <button
              type="submit"
              className="btn btn-primary w-full"
              disabled={isSubmitting}
            >
              {isSubmitting && (
                <span className="loading loading-spinner loading-sm" />
              )}
              Iniciar sesión
            </button>
          </form>

          <p className="text-center text-sm mt-4">
            ¿No tienes cuenta?{" "}
            <Link to="/register" className="link link-primary">
              Regístrate
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
