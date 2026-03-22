import { useQuery } from "@tanstack/react-query";
import api from "../services/api";
import type { DashboardStats } from "../types";

export function useDashboardStats() {
  return useQuery({
    queryKey: ["dashboard-stats"],
    queryFn: async () => {
      const { data } = await api.get<DashboardStats>("/dashboard/stats");
      return data;
    },
  });
}
