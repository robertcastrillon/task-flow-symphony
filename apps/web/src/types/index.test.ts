import { describe, it, expect } from "vitest";
import {
  loginSchema,
  registerSchema,
  taskFormSchema,
  commentFormSchema,
} from "./index";

describe("loginSchema", () => {
  it("accepts valid login data", () => {
    const result = loginSchema.safeParse({
      email: "user@example.com",
      password: "12345678",
    });
    expect(result.success).toBe(true);
  });

  it("rejects invalid email", () => {
    const result = loginSchema.safeParse({
      email: "not-an-email",
      password: "12345678",
    });
    expect(result.success).toBe(false);
  });

  it("rejects short password", () => {
    const result = loginSchema.safeParse({
      email: "user@example.com",
      password: "short",
    });
    expect(result.success).toBe(false);
  });
});

describe("registerSchema", () => {
  it("accepts valid registration data", () => {
    const result = registerSchema.safeParse({
      email: "user@example.com",
      name: "Test User",
      password: "12345678",
    });
    expect(result.success).toBe(true);
  });

  it("rejects empty name", () => {
    const result = registerSchema.safeParse({
      email: "user@example.com",
      name: "",
      password: "12345678",
    });
    expect(result.success).toBe(false);
  });
});

describe("taskFormSchema", () => {
  it("accepts valid task data", () => {
    const result = taskFormSchema.safeParse({
      title: "Test task",
      priority: "high",
      status: "todo",
    });
    expect(result.success).toBe(true);
  });

  it("sets default priority and status", () => {
    const result = taskFormSchema.safeParse({ title: "Test task" });
    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.priority).toBe("medium");
      expect(result.data.status).toBe("todo");
    }
  });

  it("rejects empty title", () => {
    const result = taskFormSchema.safeParse({ title: "" });
    expect(result.success).toBe(false);
  });

  it("rejects title longer than 255 chars", () => {
    const result = taskFormSchema.safeParse({ title: "a".repeat(256) });
    expect(result.success).toBe(false);
  });

  it("rejects invalid priority", () => {
    const result = taskFormSchema.safeParse({
      title: "Test",
      priority: "invalid",
    });
    expect(result.success).toBe(false);
  });
});

describe("commentFormSchema", () => {
  it("accepts valid comment", () => {
    const result = commentFormSchema.safeParse({ content: "A comment" });
    expect(result.success).toBe(true);
  });

  it("rejects empty comment", () => {
    const result = commentFormSchema.safeParse({ content: "" });
    expect(result.success).toBe(false);
  });
});
