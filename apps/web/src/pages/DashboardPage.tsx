import { useDashboardStats } from "../hooks/useDashboard";
import StatCard from "../components/StatCard";

export default function DashboardPage() {
  const { data: stats, isLoading } = useDashboardStats();

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <span className="loading loading-spinner loading-lg"></span>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Total de tareas" count={stats?.total_tasks ?? 0} />
        <StatCard label="Por hacer" count={stats?.tasks_by_status?.todo ?? 0} />
        <StatCard
          label="En progreso"
          count={stats?.tasks_by_status?.in_progress ?? 0}
        />
        <StatCard
          label="Tareas vencidas"
          count={stats?.overdue_tasks ?? 0}
          className={
            (stats?.overdue_tasks ?? 0) > 0 ? "border-error border" : ""
          }
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card bg-base-200">
          <div className="card-body">
            <h2 className="card-title text-lg">Tareas por estado</h2>
            {stats?.tasks_by_status && (
              <div className="space-y-2">
                {Object.entries(stats.tasks_by_status).map(
                  ([status, count]) => (
                    <div
                      key={status}
                      className="flex justify-between items-center"
                    >
                      <span className="text-sm capitalize">
                        {status.replace("_", " ")}
                      </span>
                      <span className="badge">{count}</span>
                    </div>
                  ),
                )}
              </div>
            )}
          </div>
        </div>

        <div className="card bg-base-200">
          <div className="card-body">
            <h2 className="card-title text-lg">Tareas por usuario</h2>
            {stats?.tasks_by_user && (
              <div className="space-y-2">
                {Object.entries(stats.tasks_by_user).map(([userId, count]) => (
                  <div
                    key={userId}
                    className="flex justify-between items-center"
                  >
                    <span className="text-sm">{userId}</span>
                    <span className="badge">{count}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
