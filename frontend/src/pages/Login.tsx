import { useState, FormEvent } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { LogIn } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const from = (location.state as any)?.from?.pathname || '/dashboard';

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err) {
      setError('Invalid credentials. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[rgb(var(--color-background))]">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold tracking-tight mb-2">CoreSight</h1>
          <p className="text-[rgb(var(--color-text-secondary))] text-sm">
            Business Intelligence via Engineering Metrics
          </p>
        </div>

        {/* Login Card */}
        <div className="card">
          <div className="card-body">
            <div className="mb-6">
              <h2 className="text-2xl font-bold tracking-tight mb-1">Admin Login</h2>
              <p className="text-sm text-[rgb(var(--color-text-secondary))]">
                Enter your credentials to access the dashboard
              </p>
            </div>

            {error && (
              <div className="mb-6 p-4 bg-[rgba(205,100,100,0.1)] border border-[rgba(205,100,100,0.3)] text-[rgb(var(--color-error))] rounded-sm text-sm">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor="email" className="label">
                  Email Address
                </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input"
                  placeholder="admin@coresight.com"
                  required
                  autoComplete="email"
                />
              </div>

              <div>
                <label htmlFor="password" className="label">
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input"
                  placeholder="••••••••"
                  required
                  autoComplete="current-password"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="btn btn-primary w-full mt-6"
              >
                <LogIn className="w-4 h-4" />
                {loading ? 'Logging in...' : 'Log In'}
              </button>
            </form>

            <div className="mt-6 pt-6 border-t border-[rgb(var(--color-border))]">
              <p className="text-xs text-[rgb(var(--color-text-tertiary))] text-center">
                Admin: admin@gmail.com / password123
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8">
          <p className="text-xs text-[rgb(var(--color-text-tertiary))]">
            © 2026 CoreSight. Low-level metrics, high-level insights.
          </p>
        </div>
      </div>
    </div>
  );
}
