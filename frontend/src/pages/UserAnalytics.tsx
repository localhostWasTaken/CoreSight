import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  GitCommit, 
  TrendingUp, 
  Code2, 
  Trash2, 
  Wrench, 
  User, 
  ArrowLeft,
  Activity
} from 'lucide-react';
import { 
  PieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer, 
  Tooltip, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid,
  BarChart,
  Bar
} from 'recharts';
import AdminLayout from '../components/AdminLayout';
import { analyticsAPI, userAPI } from '../lib/api';

interface ImpactBreakdown {
  user_id: string;
  total_commits: number;
  total_lines_added: number;
  total_lines_deleted: number;
  total_lines_modified: number;
  overall_refactor_ratio: number;
  profile: string;
  category_breakdown: {
    new_feature: { count: number; percentage: number };
    refactoring: { count: number; percentage: number };
    cleanup: { count: number; percentage: number };
  };
  recent_commits: any[];
}

interface CommitActivity {
  date: string;
  commits: number;
  lines_added: number;
  lines_deleted: number;
  by_project: Record<string, number>;
}

export default function UserAnalytics() {
  const { userId } = useParams<{ userId: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<any>(null);
  const [impactData, setImpactData] = useState<ImpactBreakdown | null>(null);
  const [activityData, setActivityData] = useState<CommitActivity[]>([]);
  const [projectBreakdown, setProjectBreakdown] = useState<any[]>([]);

  useEffect(() => {
    if (userId) {
      loadUserAnalytics();
    }
  }, [userId]);

  const loadUserAnalytics = async () => {
    try {
      setLoading(true);
      
      // Fetch user details first
      try {
        const userRes = await userAPI.get(userId!);
        setUser(userRes.data);
      } catch (e) {
        console.error("Failed to load user info", e);
      }

      // Fetch analytics in parallel
      const [impactRes, activityRes] = await Promise.all([
        analyticsAPI.userImpact(userId!),
        analyticsAPI.commitActivity(30, userId)
      ]);

      if (impactRes.data.success) {
        setImpactData(impactRes.data.data);
      }

      if (activityRes.data.success) {
        setActivityData(activityRes.data.data.activity || []);
        
        // Process project breakdown from activity
        const projects: Record<string, number> = {};
        activityRes.data.data.activity.forEach((day: any) => {
          if (day.by_project) {
            Object.entries(day.by_project).forEach(([proj, count]) => {
              projects[proj] = (projects[proj] || 0) + (count as number);
            });
          }
        });
        
        setProjectBreakdown(
          Object.entries(projects)
            .map(([name, value]) => ({ name, value }))
            .sort((a, b) => b.value - a.value)
        );
      }
    } catch (err) {
      console.error('Failed to load user analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  const getProfileColor = (profile: string) => {
    switch (profile) {
      case 'maker': return '#22c55e'; // Green
      case 'mender': return '#3b82f6'; // Blue
      case 'cleaner': return '#f59e0b'; // Amber
      default: return '#8b5cf6'; // Purple
    }
  };

  const getProfileDescription = (profile: string) => {
    switch (profile) {
      case 'maker': return 'Builder / Creator (High new feature output)';
      case 'mender': return 'Maintainer / Refactorer (Balanced changes)';
      case 'cleaner': return 'Tech Debt Resolver (High cleanup/deletion)';
      default: return 'Balanced Contributor';
    }
  };

  // Pie chart data for work breakdown
  const workBreakdownData = (impactData && impactData.category_breakdown) ? [
    { name: 'New Features', value: impactData.category_breakdown.new_feature.count, color: '#22c55e' },
    { name: 'Refactoring', value: impactData.category_breakdown.refactoring.count, color: '#3b82f6' },
    { name: 'Cleanup', value: impactData.category_breakdown.cleanup.count, color: '#f59e0b' },
  ].filter(d => d.value > 0) : [];

  return (
    <AdminLayout>
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <button 
            onClick={() => navigate('/users')}
            className="flex items-center gap-2 text-sm text-[rgb(var(--color-text-secondary))] hover:text-[rgb(var(--color-text-primary))] mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Employees
          </button>
          
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
                {user ? user.name : 'User'} Analytics
                {impactData && (
                  <span 
                    className="text-sm px-3 py-1 rounded-full text-white font-medium capitalize"
                    style={{ backgroundColor: getProfileColor(impactData.profile) }}
                  >
                    {impactData.profile} Profile
                  </span>
                )}
              </h1>
              <p className="text-[rgb(var(--color-text-secondary))] mt-2">
                {impactData ? getProfileDescription(impactData.profile) : 'Loading profile...'}
              </p>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12 text-[rgb(var(--color-text-secondary))]">
            Loading analytics...
          </div>
        ) : !impactData || impactData.total_commits === 0 ? (
          <div className="card card-body text-center py-12">
            <p className="text-[rgb(var(--color-text-secondary))]">
              No commit activity found for this user.
            </p>
          </div>
        ) : (
          <>
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              <div className="stat-card">
                <div className="flex items-center justify-between mb-3">
                  <GitCommit className="w-5 h-5 text-[rgb(var(--color-text-secondary))]" />
                </div>
                <div className="stat-label">Total Commits</div>
                <div className="stat-value">{impactData.total_commits}</div>
              </div>

              <div className="stat-card">
                <div className="flex items-center justify-between mb-3">
                  <Code2 className="w-5 h-5 text-green-600" />
                </div>
                <div className="stat-label">Lines Added</div>
                <div className="stat-value text-green-600">+{impactData.total_lines_added.toLocaleString()}</div>
              </div>

              <div className="stat-card">
                <div className="flex items-center justify-between mb-3">
                  <Trash2 className="w-5 h-5 text-red-600" />
                </div>
                <div className="stat-label">Lines Deleted</div>
                <div className="stat-value text-red-600">-{impactData.total_lines_deleted.toLocaleString()}</div>
              </div>

              <div className="stat-card">
                <div className="flex items-center justify-between mb-3">
                  <Wrench className="w-5 h-5 text-blue-600" />
                </div>
                <div className="stat-label">Refactor Ratio</div>
                <div className="stat-value text-blue-600">{(impactData.overall_refactor_ratio * 100).toFixed(1)}%</div>
              </div>
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              {/* Work Breakdown */}
              <div className="card">
                <div className="card-header">
                  <h3 className="text-lg font-semibold mb-0">Work Pattern Breakdown</h3>
                  <p className="text-xs text-[rgb(var(--color-text-tertiary))] mt-1">
                    Based on code churn analysis
                  </p>
                </div>
                <div className="card-body">
                  <ResponsiveContainer width="100%" height={220}>
                    <PieChart>
                      <Pie
                        data={workBreakdownData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {workBreakdownData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="flex justify-center gap-6 mt-4">
                    {workBreakdownData.map((item) => (
                      <div key={item.name} className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                        <span className="text-sm font-medium">{item.name}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Project Contribution */}
              <div className="card">
                <div className="card-header">
                  <h3 className="text-lg font-semibold mb-0">Project Contributions</h3>
                  <p className="text-xs text-[rgb(var(--color-text-tertiary))] mt-1">
                    Commits by project (last 30 days)
                  </p>
                </div>
                <div className="card-body">
                  {projectBreakdown.length > 0 ? (
                    <ResponsiveContainer width="100%" height={250}>
                      <BarChart data={projectBreakdown} layout="vertical">
                        <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="rgb(228, 228, 231)" />
                        <XAxis type="number" hide />
                        <YAxis 
                          dataKey="name" 
                          type="category" 
                          width={100}
                          tick={{ fill: 'rgb(82, 82, 91)', fontSize: 12 }} 
                        />
                        <Tooltip />
                        <Bar dataKey="value" fill="rgb(24, 24, 27)" radius={[0, 4, 4, 0]} barSize={20} />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="text-center py-12 text-[rgb(var(--color-text-secondary))]">
                      No recent project activity
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Activity Timeline */}
            <div className="card mb-8">
              <div className="card-header">
                <h3 className="text-lg font-semibold mb-0">Commit Activity (Last 30 Days)</h3>
              </div>
              <div className="card-body">
                <ResponsiveContainer width="100%" height={220}>
                  <LineChart data={activityData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgb(228, 228, 231)" />
                    <XAxis 
                      dataKey="date" 
                      tick={{ fill: 'rgb(82, 82, 91)', fontSize: 10 }}
                      tickFormatter={(value) => value.slice(5)}
                    />
                    <YAxis tick={{ fill: 'rgb(82, 82, 91)', fontSize: 12 }} />
                    <Tooltip />
                    <Line 
                      type="monotone" 
                      dataKey="commits" 
                      stroke="rgb(24, 24, 27)" 
                      strokeWidth={2} 
                      dot={{ fill: 'rgb(24, 24, 27)', r: 3 }} 
                      activeDot={{ r: 6 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Recent Commits Table */}
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold mb-0">Recent Commits</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="table w-full">
                  <thead>
                    <tr>
                      <th className="text-left py-3 px-4">Message</th>
                      <th className="text-left py-3 px-4">Category</th>
                      <th className="text-right py-3 px-4">Lines +/-</th>
                      <th className="text-right py-3 px-4">Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {impactData.recent_commits.map((commit, idx) => (
                      <tr key={idx} className="border-b border-zinc-100 hover:bg-zinc-50">
                        <td className="py-3 px-4 font-mono text-sm max-w-md truncate">
                          {commit.commit_message}
                        </td>
                        <td className="py-3 px-4">
                          <span className={`badge text-xs capitalize
                            ${commit.category === 'new_feature' ? 'badge-success' : 
                              commit.category === 'cleanup' ? 'badge-warning' : 'badge-info'}`
                          }>
                            {commit.category.replace('_', ' ')}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-right text-sm">
                          <span className="text-green-600">+{commit.lines_added}</span>
                          {' / '}
                          <span className="text-red-600">-{commit.lines_deleted}</span>
                        </td>
                        <td className="py-3 px-4 text-right text-sm text-[rgb(var(--color-text-tertiary))]">
                          {new Date(commit.timestamp).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>
    </AdminLayout>
  );
}
