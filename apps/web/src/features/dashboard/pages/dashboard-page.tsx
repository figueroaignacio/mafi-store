import { logout } from "@/features/auth/api/auth.api";
import { useAuthStore } from "@/features/auth/stores/auth.store";

export function DashboardPage() {
  const { user } = useAuthStore();

  async function handleLogout() {
    await logout();
    window.location.href = "/";
  }

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Bienvenido, {user?.name}</p>
      <p>{user?.email}</p>
      <button onClick={handleLogout}>Cerrar sesión</button>
    </div>
  );
}
