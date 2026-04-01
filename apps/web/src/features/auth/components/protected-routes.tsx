import { useAuth } from "@/features/auth/hooks/use-auth";
import { Navigate } from "react-router";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();

  if (isLoading) return <div>Cargando...</div>;
  if (!user) return <Navigate to="/" replace />;

  return children;
}
