import { Navigate } from "react-router";
import { fetchGithubLoginUrl, fetchGoogleLoginUrl } from "../api/auth.api";
import { useAuth } from "../hooks/use-auth";

export function LoginPage() {
  const { user, isLoading } = useAuth();

  async function handleGoogle() {
    const url = await fetchGoogleLoginUrl();
    window.location.href = url;
  }

  async function handleGithub() {
    const url = await fetchGithubLoginUrl();
    window.location.href = url;
  }

  if (isLoading) return <div>Cargando...</div>;
  if (user) return <Navigate to="/dashboard" replace />;

  return (
    <div>
      <h1>UTN Buddy</h1>
      <button onClick={handleGoogle}>Login con Google</button>
      <button onClick={handleGithub}>Login con GitHub</button>
    </div>
  );
}
