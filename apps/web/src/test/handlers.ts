import { http, HttpResponse } from "msw";
import type {
  Comment,
  DashboardStats,
  PaginatedResponse,
  Task,
  TokenResponse,
  User,
} from "../types";

const API = "/api/v1";

export const mockUser: User = {
  id: "user-1",
  email: "test@example.com",
  name: "Test User",
  avatar_url: null,
  role: "admin",
  created_at: "2026-01-01T00:00:00Z",
  is_active: true,
};

export const mockUser2: User = {
  id: "user-2",
  email: "member@example.com",
  name: "Team Member",
  avatar_url: null,
  role: "member",
  created_at: "2026-01-02T00:00:00Z",
  is_active: true,
};

export const mockTask: Task = {
  id: "task-1",
  title: "Test Task",
  description: "A test task",
  status: "todo",
  priority: "medium",
  due_date: null,
  created_by: "user-1",
  assigned_to: "user-2",
  tags: ["frontend"],
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
  completed_at: null,
  creator: mockUser,
  assignee: mockUser2,
};

export const mockComment: Comment = {
  id: "comment-1",
  task_id: "task-1",
  author_id: "user-1",
  content: "This is a test comment",
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
  author: mockUser,
};

export const mockDashboardStats: DashboardStats = {
  total_tasks: 10,
  tasks_by_status: { todo: 3, in_progress: 4, done: 2, cancelled: 1 },
  tasks_by_user: { "user-1": 5, "user-2": 5 },
  overdue_tasks: 2,
};

export const handlers = [
  http.post(`${API}/auth/login`, () => {
    return HttpResponse.json<TokenResponse>({
      access_token: "mock-access-token",
      refresh_token: "mock-refresh-token",
      token_type: "bearer",
    });
  }),

  http.post(`${API}/auth/register`, () => {
    return new HttpResponse(null, { status: 201 });
  }),

  http.get(`${API}/auth/me`, () => {
    return HttpResponse.json<User>(mockUser);
  }),

  http.get(`${API}/users`, () => {
    return HttpResponse.json<PaginatedResponse<User>>({
      items: [mockUser, mockUser2],
      total: 2,
      page: 1,
      page_size: 50,
      total_pages: 1,
    });
  }),

  http.get(`${API}/users/:id`, ({ params }) => {
    const user = [mockUser, mockUser2].find((u) => u.id === params.id);
    if (!user) return new HttpResponse(null, { status: 404 });
    return HttpResponse.json<User>(user);
  }),

  http.get(`${API}/tasks`, () => {
    return HttpResponse.json<PaginatedResponse<Task>>({
      items: [mockTask],
      total: 1,
      page: 1,
      page_size: 50,
      total_pages: 1,
    });
  }),

  http.post(`${API}/tasks`, async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>;
    return HttpResponse.json<Task>({
      ...mockTask,
      id: "task-new",
      title: (body.title as string) ?? "New Task",
    });
  }),

  http.get(`${API}/tasks/:id`, () => {
    return HttpResponse.json<Task>(mockTask);
  }),

  http.patch(`${API}/tasks/:id`, () => {
    return HttpResponse.json<Task>(mockTask);
  }),

  http.delete(`${API}/tasks/:id`, () => {
    return new HttpResponse(null, { status: 204 });
  }),

  http.patch(`${API}/tasks/:id/status`, () => {
    return HttpResponse.json<Task>(mockTask);
  }),

  http.patch(`${API}/tasks/:id/assign`, () => {
    return HttpResponse.json<Task>(mockTask);
  }),

  http.get(`${API}/tasks/:id/comments`, () => {
    return HttpResponse.json<Comment[]>([mockComment]);
  }),

  http.post(`${API}/tasks/:id/comments`, () => {
    return HttpResponse.json<Comment>(mockComment);
  }),

  http.get(`${API}/dashboard/stats`, () => {
    return HttpResponse.json<DashboardStats>(mockDashboardStats);
  }),
];
