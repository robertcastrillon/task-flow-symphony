import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import StatCard from "./StatCard";

describe("StatCard", () => {
  it("renders count and label", () => {
    render(<StatCard label="Total de tareas" count={42} />);
    expect(screen.getByText("42")).toBeInTheDocument();
    expect(screen.getByText("Total de tareas")).toBeInTheDocument();
  });

  it("applies custom className", () => {
    const { container } = render(
      <StatCard label="Test" count={0} className="border-error" />,
    );
    expect(container.firstChild).toHaveClass("border-error");
  });
});
