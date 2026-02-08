import type { ReactNode } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Users, 
  CheckSquare, 
  BarChart3, 
  FolderKanban,
  LogOut,
  Activity,
  Briefcase
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

interface LayoutProps {
  children: ReactNode;
}

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Users', href: '/users', icon: Users },
  { name: 'Projects', href: '/projects', icon: FolderKanban },
  { name: 'Jobs', href: '/jobs', icon: Briefcase },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Activity', href: '/activity', icon: Activity },
];

export default function AdminLayout({ children }: LayoutProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-64 bg-[rgb(var(--color-surface))] border-r border-[rgb(var(--color-border))] flex flex-col">
        {/* Logo/Brand */}
        <div className="h-16 flex items-center px-6 border-b border-[rgb(var(--color-border))]">
          <h1 className="text-xl font-bold tracking-tight mb-0">CoreSight</h1>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-6 space-y-1">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`
                  flex items-center gap-3 px-3 py-2.5 text-sm font-medium
                  transition-colors no-underline
                  ${isActive 
                    ? 'bg-[rgb(var(--color-accent))] text-white' 
                    : 'text-[rgb(var(--color-text-secondary))] hover:bg-[rgb(var(--color-surface-secondary))] hover:text-[rgb(var(--color-text-primary))]'
                  }
                `}
              >
                <item.icon className="w-5 h-5" />
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* User info */}
        <div className="border-t border-[rgb(var(--color-border))] p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-[rgb(var(--color-text-primary))] truncate mb-0">
                {user?.name}
              </p>
              <p className="text-xs text-[rgb(var(--color-text-secondary))] truncate mb-0">
                {user?.email}
              </p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="btn btn-ghost w-full justify-start text-sm"
          >
            <LogOut className="w-4 h-4" />
            Logout
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-h-screen">
        {/* Header */}
        <header className="h-16 bg-[rgb(var(--color-surface))] border-b border-[rgb(var(--color-border))] flex items-center px-8">
          <div className="flex-1">
            <h2 className="text-sm font-medium text-[rgb(var(--color-text-secondary))] mb-0">
              Admin Dashboard
            </h2>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-8 bg-[rgb(var(--color-background))]">
          {children}
        </main>
      </div>
    </div>
  );
}
