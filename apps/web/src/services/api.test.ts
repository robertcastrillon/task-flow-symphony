import { describe, it, expect, beforeEach } from "vitest";
import api from "./api";

describe("API client", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("has correct base URL", () => {
    expect(api.defaults.baseURL).toBe("/api/v1");
  });

  it("sets Content-Type header", () => {
    expect(api.defaults.headers["Content-Type"]).toBe("application/json");
  });

  it("adds Authorization header when token exists", () => {
    localStorage.setItem("access_token", "test-token");
    const handlers = api.interceptors.request.handlers as unknown as Array<{
      fulfilled: (config: { headers: Record<string, string> }) => {
        headers: Record<string, string>;
      };
    }>;
    const config = handlers[0].fulfilled({
      headers: {} as Record<string, string>,
    });
    expect(config.headers.Authorization).toBe("Bearer test-token");
  });

  it("does not add Authorization header when no token", () => {
    const handlers = api.interceptors.request.handlers as unknown as Array<{
      fulfilled: (config: { headers: Record<string, string> }) => {
        headers: Record<string, string>;
      };
    }>;
    const config = handlers[0].fulfilled({
      headers: {} as Record<string, string>,
    });
    expect(config.headers.Authorization).toBeUndefined();
  });
});
