import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useNavigate } from "react-router-dom";
import { registerSchema, type RegisterFormData } from "../types";
import { useAuth } from "../hooks/useAuth";
import { AxiosError } from "axios";
import type { ApiError } from "../types";

export default function RegisterPage() {
  const { register: registerUser } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  async function onSubmit(data: RegisterFormData) {
    try {
      setError(null);
      await registerUser(data);
      navigate("/login");
    } catch (err) {
      if (err instanceof AxiosError) {
        const apiError = err.response?.data as ApiError | undefined;
        setError(apiError?.detail ?? "Error al registrarse");
      } else {
        setError("Error al registrarse");
      }
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-base-200">
      <div className="card w-96 bg-base-100 shadow-lg">
        <div className="card-body">
          <h1 className="card-title text-2xl justify-center mb-4">
            Crear cuenta
          </h1>
          {error && (
            <div className="alert alert-error text-sm" role="alert">
              {error}
            </div>
          )}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="form-control">
              <label className="label" htmlFor="name">
                <span className="label-text">Nombre</span>
              </label>
              <input
                id="name"
                type="text"
                className={`input input-bordered ${errors.name ? "input-error" : ""}`}
                {...register("name")}
              />
              {errors.name && (
                <label className="label">
                  <span className="label-text-alt text-error">
                    {errors.name.message}
                  </span>
                </label>
              )}
            </div>

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
              Registrarse
            </button>
          </form>

          <p className="text-center text-sm mt-4">
            ¿Ya tienes cuenta?{" "}
            <Link to="/login" className="link link-primary">
              Inicia sesión
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
