import { Route, Routes } from "react-router";
import { ProtectedRoute } from "./features/auth/components/protected-routes";
import { LoginPage } from "./features/auth/pages/login-page";
import { DashboardPage } from "./features/dashboard/pages/dashboard-page";

export function App() {
  return (
    <Routes>
      <Route path="/" element={<LoginPage />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}
