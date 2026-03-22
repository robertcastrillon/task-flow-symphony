import { z } from "zod";

// Enums
export const UserRole = {
  ADMIN: "admin",
  MEMBER: "member",
} as const;
export type UserRole = (typeof UserRole)[keyof typeof UserRole];

export const TaskStatus = {
  TODO: "todo",
  IN_PROGRESS: "in_progress",
  DONE: "done",
  CANCELLED: "cancelled",
} as const;
export type TaskStatus = (typeof TaskStatus)[keyof typeof TaskStatus];

export const TaskPriority = {
  LOW: "low",
  MEDIUM: "medium",
  HIGH: "high",
  URGENT: "urgent",
} as const;
export type TaskPriority = (typeof TaskPriority)[keyof typeof TaskPriority];

// Zod schemas
export const loginSchema = z.object({
  email: z.string().email("Email inválido"),
  password: z.string().min(8, "La contraseña debe tener al menos 8 caracteres"),
});
export type LoginFormData = z.infer<typeof loginSchema>;

export const registerSchema = z.object({
  email: z.string().email("Email inválido"),
  name: z.string().min(1, "El nombre es obligatorio"),
  password: z.string().min(8, "La contraseña debe tener al menos 8 caracteres"),
});
export type RegisterFormData = z.infer<typeof registerSchema>;

export const taskFormSchema = z.object({
  title: z
    .string()
    .min(1, "El título es obligatorio")
    .max(255, "El título no puede superar 255 caracteres"),
  description: z.string().optional(),
  priority: z.enum(["low", "medium", "high", "urgent"]).default("medium"),
  status: z.enum(["todo", "in_progress", "done", "cancelled"]).default("todo"),
  due_date: z.string().optional(),
  assigned_to: z.string().uuid().optional().nullable(),
  tags: z.array(z.string()).default([]),
});
export type TaskFormData = z.infer<typeof taskFormSchema>;

export const commentFormSchema = z.object({
  content: z.string().min(1, "El comentario no puede estar vacío"),
});
export type CommentFormData = z.infer<typeof commentFormSchema>;

// Domain types
export interface User {
  id: string;
  email: string;
  name: string;
  avatar_url: string | null;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface Task {
  id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  due_date: string | null;
  created_by: string;
  assigned_to: string | null;
  tags: string[];
  created_at: string;
  updated_at: string;
  completed_at: string | null;
  creator?: User;
  assignee?: User;
}

export interface Comment {
  id: string;
  task_id: string;
  author_id: string;
  content: string;
  created_at: string;
  updated_at: string;
  author?: User;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface DashboardStats {
  total_tasks: number;
  tasks_by_status: Record<string, number>;
  tasks_by_user: Record<string, number>;
  overdue_tasks: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ApiError {
  detail: string;
  code: string;
}

export interface TaskFilters {
  status?: TaskStatus;
  priority?: TaskPriority;
  assignee?: string;
  tag?: string;
  search?: string;
  page?: number;
  page_size?: number;
}
