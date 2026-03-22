import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

const navItems = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/tasks/board", label: "Tablero" },
  { to: "/tasks/list", label: "Lista" },
  { to: "/team", label: "Equipo" },
];

export default function Layout() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen flex">
      <aside className="w-64 bg-base-200 p-4 flex flex-col">
        <h1 className="text-xl font-bold mb-8 px-2">TaskFlow</h1>
        <nav className="flex-1">
          <ul className="menu gap-1">
            {navItems.map((item) => (
              <li key={item.to}>
                <NavLink
                  to={item.to}
                  className={({ isActive }) =>
                    isActive ? "active font-semibold" : ""
                  }
                >
                  {item.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
        <div className="border-t border-base-300 pt-4">
          <div className="flex items-center gap-2 px-2 mb-2">
            <div className="avatar placeholder">
              <div className="bg-neutral text-neutral-content w-8 rounded-full">
                <span className="text-sm">
                  {user?.name?.charAt(0).toUpperCase() ?? "?"}
                </span>
              </div>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user?.name}</p>
              <p className="text-xs text-base-content/60 truncate">
                {user?.email}
              </p>
            </div>
          </div>
          <button onClick={logout} className="btn btn-ghost btn-sm w-full">
            Cerrar sesión
          </button>
        </div>
      </aside>
      <main className="flex-1 p-6 bg-base-100 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
}
