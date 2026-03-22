import { useUsers } from "../hooks/useUsers";

const roleBadges: Record<string, string> = {
  admin: "badge-primary",
  member: "badge-ghost",
};

export default function TeamPage() {
  const { data: users, isLoading } = useUsers();

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <span className="loading loading-spinner loading-lg"></span>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Equipo</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {users?.map((user) => (
          <div key={user.id} className="card bg-base-200 shadow-sm">
            <div className="card-body p-4 flex-row items-center gap-4">
              <div className="avatar placeholder">
                <div className="bg-neutral text-neutral-content w-12 rounded-full">
                  <span className="text-lg">
                    {user.name.charAt(0).toUpperCase()}
                  </span>
                </div>
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold truncate">{user.name}</h3>
                <p className="text-sm text-base-content/60 truncate">
                  {user.email}
                </p>
              </div>
              <span className={`badge ${roleBadges[user.role] ?? ""}`}>
                {user.role}
              </span>
            </div>
          </div>
        ))}
        {users?.length === 0 && (
          <p className="text-base-content/60 col-span-full text-center">
            No hay miembros en el equipo.
          </p>
        )}
      </div>
    </div>
  );
}
