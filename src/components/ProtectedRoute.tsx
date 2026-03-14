import { Navigate } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { accessToken, isLoading } = useAuthStore();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (!accessToken) return <Navigate to="/login" replace />;
  return <>{children}</>;
}
