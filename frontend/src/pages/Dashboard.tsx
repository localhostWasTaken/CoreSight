import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Users, CheckSquare, FolderKanban, Activity, TrendingUp, AlertCircle } from 'lucide-react';
import AdminLayout from '../components/AdminLayout';
import { userAPI, taskAPI, projectAPI, analyticsAPI } from '../lib/api';

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalUsers: 0,
    activeTasks: 0,
    projects: 0,
    loading: true,
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [usersRes, tasksRes, projectsRes] = await Promise.all([
        userAPI.list(),
        taskAPI.list(),
        projectAPI.list(),
      ]);

      setStats({
        totalUsers: usersRes.data.length,
        activeTasks: tasksRes.data.filter((t: any) => t.status !== 'done').length,
        projects: projectsRes.data.length,
        loading: false,
      });
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      setStats(prev => ({ ...prev, loading: false }));
    }
  };

  return (
    <AdminLayout>
      <div className="max-w-7xl">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight mb-2">Dashboard</h1>
          <p className="text-[rgb(var(--color-text-secondary))]">
            Overview of your business intelligence metrics
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Link to="/users" className="no-underline">
            <div className="stat-card hover:border-[rgb(var(--color-accent))] transition-colors">
              <div className="flex items-center justify-between mb-4">
                <Users className="w-8 h-8 text-[rgb(var(--color-text-secondary))]" />
                <TrendingUp className="w-4 h-4 text-[rgb(var(--color-success))]" />
              </div>
              <div className="stat-label">Total Users</div>
              <div className="stat-value">{stats.loading ? '—' : stats.totalUsers}</div>
            </div>
          </Link>

          <Link to="/tasks" className="no-underline">
            <div className="stat-card hover:border-[rgb(var(--color-accent))] transition-colors">
              <div className="flex items-center justify-between mb-4">
                <CheckSquare className="w-8 h-8 text-[rgb(var(--color-text-secondary))]" />
                <Activity className="w-4 h-4 text-[rgb(var(--color-info))]" />
              </div>
              <div className="stat-label">Active Tasks</div>
              <div className="stat-value">{stats.loading ? '—' : stats.activeTasks}</div>
            </div>
          </Link>

          <Link to="/projects" className="no-underline">
            <div className="stat-card hover:border-[rgb(var(--color-accent))] transition-colors">
              <div className="flex items-center justify-between mb-4">
                <FolderKanban className="w-8 h-8 text-[rgb(var(--color-text-secondary))]" />
              </div>
              <div className="stat-label">Projects</div>
              <div className="stat-value">{stats.loading ? '—' : stats.projects}</div>
            </div>
          </Link>

          <Link to="/analytics" className="no-underline">
            <div className="stat-card hover:border-[rgb(var(--color-accent))] transition-colors">
              <div className="flex items-center justify-between mb-4">
                <Activity className="w-8 h-8 text-[rgb(var(--color-text-secondary))]" />
                <AlertCircle className="w-4 h-4 text-[rgb(var(--color-warning))]" />
              </div>
              <div className="stat-label">Insights</div>
              <div className="stat-value">View</div>
            </div>
          </Link>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold mb-0">Quick Actions</h3>
            </div>
            <div className="card-body space-y-3">
              <Link to="/users/new" className="btn btn-secondary w-full justify-start">
                <Users className="w-4 h-4" />
                Add New User
              </Link>
              <Link to="/projects/new" className="btn btn-secondary w-full justify-start">
                <FolderKanban className="w-4 h-4" />
                Create Project
              </Link>
              <Link to="/analytics" className="btn btn-secondary w-full justify-start">
                <Activity className="w-4 h-4" />
                View Analytics
              </Link>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold mb-0">System Info</h3>
            </div>
            <div className="card-body space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-[rgb(var(--color-text-secondary))]">Version</span>
                <span className="text-sm font-medium">1.0.0</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-[rgb(var(--color-text-secondary))]">Status</span>
                <span className="badge badge-success">Operational</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-[rgb(var(--color-text-secondary))]">Last Updated</span>
                <span className="text-sm font-medium">Feb 8, 2026</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AdminLayout>
  );
}
