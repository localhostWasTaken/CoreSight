
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Users, 
  CheckSquare, 
  FolderKanban, 
  Activity, 
  TrendingUp, 
  AlertCircle, 
  GitCommit,
  Briefcase,
  Clock,
  ArrowRight,
  UserPlus
} from 'lucide-react';
import AdminLayout from '../components/AdminLayout';
import { userAPI, taskAPI, projectAPI, analyticsAPI, jobAPI, commitAPI } from '../lib/api';

interface DashboardStats {
  totalUsers: number;
  activeTasks: number;
  projects: number;
  pendingJobs: number;
  loading: boolean;
}

interface ActivityItem {
  id: string;
  type: 'commit' | 'task' | 'job';
  title: string;
  subtitle: string;
  date: string;
  icon: any;
  color: string;
}

interface PendingJob {
  _id: string;
  suggested_title: string;
  created_at: string;
}

interface TopContributor {
  user_id: string;
  name: string;
  commit_count: number;
  lines_added: number;
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    totalUsers: 0,
    activeTasks: 0,
    projects: 0,
    pendingJobs: 0,
    loading: true,
  });

  const [recentActivity, setRecentActivity] = useState<ActivityItem[]>([]);
  const [pendingJobs, setPendingJobs] = useState<PendingJob[]>([]);
  const [topContributors, setTopContributors] = useState<TopContributor[]>([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      // Use Promise.allSettled so one failure doesn't block everything
      const [usersRes, tasksRes, projectsRes, jobsRes, commitsRes, contributorsRes] = await Promise.allSettled([
        userAPI.list(),
        taskAPI.list(),
        projectAPI.list(),
        jobAPI.list({ status: 'pending' }),
        commitAPI.list({ limit: 5 }),
        analyticsAPI.topContributors({ limit: 3 })
      ]);

      setStats({
        totalUsers: usersRes.status === 'fulfilled' ? usersRes.value.data.length : 0,
        activeTasks: tasksRes.status === 'fulfilled' ? tasksRes.value.data.filter((t: any) => t.status !== 'done').length : 0,
        projects: projectsRes.status === 'fulfilled' ? projectsRes.value.data.length : 0,
        pendingJobs: jobsRes.status === 'fulfilled' ? jobsRes.value.data.length : 0,
        loading: false,
      });

      if (jobsRes.status === 'fulfilled') {
        setPendingJobs(jobsRes.value.data.slice(0, 3));
      }

      // Process recent activity from commits
      if (commitsRes.status === 'fulfilled') {
        const commitsData = Array.isArray(commitsRes.value.data) ? commitsRes.value.data : [];
        const activities: ActivityItem[] = commitsData.slice(0, 5).map((commit: any, index: number) => ({
          id: commit._id || commit.id || `commit-${index}-${Date.now()}`,
          type: 'commit',
          title: commit.message || commit.commit_message || 'Commit',
          subtitle: `${commit.author_name || 'Unknown'} • ${commit.repository || 'Repo'}`,
          date: commit.committed_at || commit.created_at,
          icon: GitCommit,
          color: 'text-[rgb(var(--color-accent))]',
        }));
        setRecentActivity(activities);
      }
      
     } catch (error) {
      console.error('Failed to load dashboard data:', error);
      setStats(prev => ({ ...prev, loading: false }));
    }
  };

  const formatTimeAgo = (date: string) => {
    const d = new Date(date);
    if (isNaN(d.getTime())) return 'Unknown';
    const now = new Date();
    const diffMs = now.getTime() - d.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  return (
    <AdminLayout>
      <div className="max-w-7xl mx-auto">
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
            <div className="stat-card hover:border-[rgb(var(--color-accent))] transition-colors group">
              <div className="flex items-center justify-between mb-4">
                <Users className="w-8 h-8 text-[rgb(var(--color-text-secondary))] group-hover:text-[rgb(var(--color-accent))] transition-colors" />
                <TrendingUp className="w-4 h-4 text-[rgb(var(--color-success))]" />
              </div>
              <div className="stat-label">Total Users</div>
              <div className="stat-value">{stats.loading ? '—' : stats.totalUsers}</div>
            </div>
          </Link>

          <Link to="/tasks" className="no-underline">
            <div className="stat-card hover:border-[rgb(var(--color-accent))] transition-colors group">
              <div className="flex items-center justify-between mb-4">
                <CheckSquare className="w-8 h-8 text-[rgb(var(--color-text-secondary))] group-hover:text-[rgb(var(--color-accent))] transition-colors" />
                <Activity className="w-4 h-4 text-[rgb(var(--color-info))]" />
              </div>
              <div className="stat-label">Active Tasks</div>
              <div className="stat-value">{stats.loading ? '—' : stats.activeTasks}</div>
            </div>
          </Link>

          <Link to="/projects" className="no-underline">
            <div className="stat-card hover:border-[rgb(var(--color-accent))] transition-colors group">
              <div className="flex items-center justify-between mb-4">
                <FolderKanban className="w-8 h-8 text-[rgb(var(--color-text-secondary))] group-hover:text-[rgb(var(--color-accent))] transition-colors" />
              </div>
              <div className="stat-label">Projects</div>
              <div className="stat-value">{stats.loading ? '—' : stats.projects}</div>
            </div>
          </Link>

          <Link to="/jobs" className="no-underline">
            <div className="stat-card hover:border-[rgb(var(--color-accent))] transition-colors group">
              <div className="flex items-center justify-between mb-4">
                <Briefcase className="w-8 h-8 text-[rgb(var(--color-text-secondary))] group-hover:text-[rgb(var(--color-accent))] transition-colors" />
                {stats.pendingJobs > 0 && <AlertCircle className="w-4 h-4 text-[rgb(var(--color-warning))]" />}
              </div>
              <div className="stat-label">Pending Jobs</div>
              <div className="stat-value">{stats.loading ? '—' : stats.pendingJobs}</div>
            </div>
          </Link>
        </div>

        {/* Dashboard Grid Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Main Content Area (2 cols) */}
          <div className="lg:col-span-2 space-y-8">
            
            {/* Recent Activity */}
            <div className="card">
              <div className="card-header flex items-center justify-between">
                <h3 className="text-lg font-semibold mb-0">Recent Activity</h3>
                <Link to="/activity" className="text-sm flex items-center gap-1 hover:underline">
                  View All <ArrowRight className="w-3 h-3" />
                </Link>
              </div>
              <div className="card-body p-0">
                {stats.loading ? (
                   <div className="p-8 text-center text-[rgb(var(--color-text-secondary))]">Loading...</div>
                ) : recentActivity.length === 0 ? (
                  <div className="p-8 text-center text-[rgb(var(--color-text-secondary))]">
                    No recent activity found.
                  </div>
                ) : (
                  <div className="divide-y divide-[rgb(var(--color-border))]">
                    {recentActivity.map((item) => (
                      <div key={item.id} className="p-4 hover:bg-[rgb(var(--color-surface-secondary))] transition-colors flex items-start gap-4">
                        <div className={`mt-1 p-2 rounded-full bg-[rgb(var(--color-surface))] border border-[rgb(var(--color-border))] ${item.color}`}>
                          <item.icon className="w-4 h-4" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-[rgb(var(--color-text-primary))] truncate">
                            {item.title}
                          </p>
                          <p className="text-xs text-[rgb(var(--color-text-secondary))] mt-0.5">
                            {item.subtitle}
                          </p>
                        </div>
                        <div className="text-xs text-[rgb(var(--color-text-tertiary))] whitespace-nowrap">
                          {formatTimeAgo(item.date)}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Quick Actions */}
             <div className="card">
                <div className="card-header">
                  <h3 className="text-lg font-semibold mb-0">Quick Actions</h3>
                </div>
                <div className="card-body grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <Link to="/users/new" className="btn btn-secondary justify-start h-auto py-3 flex-col items-center text-center gap-2 hover:border-[rgb(var(--color-accent))]">
                    <UserPlus className="w-5 h-5 text-[rgb(var(--color-accent))]" />
                    <span>Add User</span>
                  </Link>
                  <Link to="/projects/new" className="btn btn-secondary justify-start h-auto py-3 flex-col items-center text-center gap-2 hover:border-[rgb(var(--color-accent))]">
                    <FolderKanban className="w-5 h-5 text-[rgb(var(--color-accent))]" />
                    <span>New Project</span>
                  </Link>
                  <Link to="/analytics" className="btn btn-secondary justify-start h-auto py-3 flex-col items-center text-center gap-2 hover:border-[rgb(var(--color-accent))]">
                    <Activity className="w-5 h-5 text-[rgb(var(--color-accent))]" />
                    <span>Analytics</span>
                  </Link>
                </div>
              </div>

          </div>

          {/* Sidebar Area (1 col) */}
          <div className="space-y-8">
            
            {/* Pending Job Requisitions */}
            <div className="card">
              <div className="card-header flex items-center justify-between">
                <h3 className="text-lg font-semibold mb-0">Pending Jobs</h3>
                {stats.pendingJobs > 0 && (
                   <span className="badge badge-warning">{stats.pendingJobs}</span>
                )}
              </div>
              <div className="card-body p-0">
                {stats.loading ? (
                   <div className="p-6 text-center text-xs text-[rgb(var(--color-text-secondary))]">Loading...</div>
                ) : pendingJobs.length === 0 ? (
                  <div className="p-6 text-center">
                    <CheckSquare className="w-8 h-8 mx-auto text-[rgb(var(--color-success))] mb-2 opacity-50" />
                    <p className="text-sm text-[rgb(var(--color-text-secondary))]">All cleared!</p>
                  </div>
                ) : (
                  <div className="divide-y divide-[rgb(var(--color-border))]">
                    {pendingJobs.map((job) => (
                      <div key={job._id} className="p-4 hover:bg-[rgb(var(--color-surface-secondary))] transition-colors">
                        <div className="flex items-start justify-between gap-2 mb-1">
                          <h4 className="text-sm font-medium text-[rgb(var(--color-text-primary))] line-clamp-1">
                            {job.suggested_title}
                          </h4>
                        </div>
                        <div className="flex items-center justify-between mt-2">
                           <span className="text-xs text-[rgb(var(--color-text-tertiary))] flex items-center gap-1">
                             <Clock className="w-3 h-3" />
                             {formatTimeAgo(job.created_at)}
                           </span>
                           <Link to="/jobs" className="text-xs font-medium text-[rgb(var(--color-accent))] hover:underline">
                             Review
                           </Link>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                <div className="p-3 border-t border-[rgb(var(--color-border))] bg-[rgb(var(--color-surface-secondary))]">
                  <Link to="/jobs" className="text-xs w-full flex items-center justify-center gap-1 text-[rgb(var(--color-text-secondary))] hover:text-[rgb(var(--color-text-primary))]">
                    Manage Requisitions <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>
              </div>
            </div>

            {/* System Info */}
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold mb-0">System Status</h3>
              </div>
              <div className="card-body space-y-3">
                <div className="flex justify-between items-center text-sm">
                  <span className="text-[rgb(var(--color-text-secondary))]">Version</span>
                  <span className="font-mono">v1.2.0</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-[rgb(var(--color-text-secondary))]">Status</span>
                  <span className="badge badge-success flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-green-600 animate-pulse"></span>
                    Operational
                  </span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-[rgb(var(--color-text-secondary))]">Environment</span>
                  <span className="badge badge-neutral">Production</span>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </AdminLayout>
  );
}
