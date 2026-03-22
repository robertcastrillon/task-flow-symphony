import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import App from "./App";

describe("App", () => {
  it("renders the app title", () => {
    render(<App />);
    expect(screen.getByText("TaskFlow")).toBeInTheDocument();
  });

  it("renders the subtitle", () => {
    render(<App />);
    expect(
      screen.getByText("Task management for teams"),
    ).toBeInTheDocument();
  });
});
