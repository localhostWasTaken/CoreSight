import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string;
}

export default function ProtectedRoute({ children, requiredRole = 'admin' }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, user } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[rgb(var(--color-background))]">
        <div className="text-center">
          <div className="inline-block w-8 h-8 border-2 border-[rgb(var(--color-accent))] border-t-transparent rounded-full animate-spin mb-4"></div>
          <div className="text-lg font-medium text-[rgb(var(--color-text-secondary))]">
            Loading...
          </div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check for required role (default: admin)
  if (requiredRole && user?.role !== requiredRole) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[rgb(var(--color-background))]">
        <div className="card max-w-md w-full">
          <div className="card-body text-center">
            <div className="text-5xl mb-4">🚫</div>
            <h2 className="text-xl font-semibold mb-2">Access Denied</h2>
            <p className="text-[rgb(var(--color-text-secondary))] mb-4">
              You don't have permission to access this page. Admin access required.
            </p>
            <button
              onClick={() => window.location.href = '/login'}
              className="btn btn-primary"
            >
              Back to Login
            </button>
          </div>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
