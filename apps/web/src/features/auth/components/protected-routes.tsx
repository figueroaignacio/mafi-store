import { Navigate } from "react-router";
import { useAuth } from "../hooks/use-auth";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();

  if (isLoading) return <div>Cargando...</div>;
  if (!user) return <Navigate to="/" replace />;

  return children;
}
