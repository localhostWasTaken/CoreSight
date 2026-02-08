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
  Activity,
  DollarSign,
  BrainCircuit,
  Target
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

interface ValueAnalysis {
  hourly_rate: number;
  total_cost: number;
  total_value_score: number;
  roi_ratio: number;
  high_impact_commits: Array<{
    hash: string;
    message: string;
    score: number;
    complexity: string;
    reasoning: string;
  }>;
}

export default function UserAnalytics() {
  const { userId } = useParams<{ userId: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<any>(null);
  const [impactData, setImpactData] = useState<ImpactBreakdown | null>(null);
  const [activityData, setActivityData] = useState<CommitActivity[]>([]);
  const [projectBreakdown, setProjectBreakdown] = useState<any[]>([]);
  const [valueData, setValueData] = useState<ValueAnalysis | null>(null);

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
      const [impactRes, activityRes, valueRes] = await Promise.all([
        analyticsAPI.userImpact(userId!),
        analyticsAPI.commitActivity(30, userId),
        analyticsAPI.developerValue(userId!, 30)
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

      if (valueRes.data.success) {
        setValueData(valueRes.data.data);
      }
    } catch (err) {
      console.error('Failed to load user analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  const CHART_COLORS = {
    success: 'rgb(120, 180, 120)',
    error: 'rgb(205, 100, 100)',
    info: 'rgb(135, 165, 200)',
    accent: 'rgb(198, 115, 89)',
    warning: 'rgb(218, 175, 95)',
    grid: 'rgb(243, 228, 220)',
    tick: 'rgb(115, 100, 93)',
  };

  const getProfileColor = (profile: string) => {
    switch (profile) {
      case 'maker': return CHART_COLORS.success;
      case 'mender': return CHART_COLORS.info;
      case 'cleaner': return CHART_COLORS.warning;
      default: return CHART_COLORS.accent;
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
    { name: 'New Features', value: impactData.category_breakdown.new_feature.count, color: CHART_COLORS.success },
    { name: 'Refactoring', value: impactData.category_breakdown.refactoring.count, color: CHART_COLORS.info },
    { name: 'Cleanup', value: impactData.category_breakdown.cleanup.count, color: CHART_COLORS.warning },
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
                  <Code2 className="w-5 h-5 text-[rgb(var(--color-success))]" />
                </div>
                <div className="stat-label">Lines Added</div>
                <div className="stat-value text-[rgb(var(--color-success))]">+{impactData.total_lines_added.toLocaleString()}</div>
              </div>

              <div className="stat-card">
                <div className="flex items-center justify-between mb-3">
                  <Trash2 className="w-5 h-5 text-[rgb(var(--color-error))]" />
                </div>
                <div className="stat-label">Lines Deleted</div>
                <div className="stat-value text-[rgb(var(--color-error))]">-{impactData.total_lines_deleted.toLocaleString()}</div>
              </div>

              <div className="stat-card">
                <div className="flex items-center justify-between mb-3">
                  <Wrench className="w-5 h-5 text-[rgb(var(--color-info))]" />
                </div>
                <div className="stat-label">Refactor Ratio</div>
                <div className="stat-value text-[rgb(var(--color-info))]">{(impactData.overall_refactor_ratio * 100).toFixed(1)}%</div>
              </div>
            </div>

            {/* Cost & Value Analysis */}
            {valueData && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                {/* Cost Summary Card */}
                <div className="card">
                  <div className="card-body text-center">
                    <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-[rgba(198,115,89,0.12)] flex items-center justify-center">
                      <DollarSign className="w-6 h-6 text-[rgb(var(--color-accent))]" />
                    </div>
                    <div className="stat-label">Estimated Cost (30d)</div>
                    <div className="stat-value">${valueData.total_cost.toLocaleString()}</div>
                    <div className="text-xs text-[rgb(var(--color-text-tertiary))] mt-2">
                      @ ${valueData.hourly_rate}/hr
                    </div>
                  </div>
                </div>

                {/* Value Score Card */}
                <div className="card">
                  <div className="card-body text-center">
                    <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-[rgba(120,180,120,0.12)] flex items-center justify-center">
                      <BrainCircuit className="w-6 h-6 text-[rgb(var(--color-success))]" />
                    </div>
                    <div className="stat-label">Value Score</div>
                    <div className="stat-value">{valueData.total_value_score}</div>
                    <div className="text-xs text-[rgb(var(--color-text-tertiary))] mt-2">
                      AI-assessed impact
                    </div>
                  </div>
                </div>

                {/* ROI Card */}
                <div className="card">
                  <div className="card-body text-center">
                    <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-[rgba(135,165,200,0.12)] flex items-center justify-center">
                      <Target className="w-6 h-6 text-[rgb(var(--color-info))]" />
                    </div>
                    <div className="stat-label">ROI Ratio</div>
                    <div className={`stat-value ${valueData.roi_ratio > 1.5 ? 'text-[rgb(var(--color-success))]' : ''}`}>
                      {valueData.roi_ratio}x
                    </div>
                    <div className="mt-3">
                      <div className="progress">
                        <div 
                          className={`progress-bar ${valueData.roi_ratio > 1.5 ? 'bg-[rgb(var(--color-success))]' : ''}`} 
                          style={{ width: `${Math.min(valueData.roi_ratio * 30, 100)}%` }}
                        />
                      </div>
                      <div className="text-xs text-[rgb(var(--color-text-tertiary))] mt-2">
                        &gt;1.5x = high value delivery
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* High Impact Commits */}
            {valueData && valueData.high_impact_commits.length > 0 && (
              <div className="card mb-8">
                <div className="card-header flex items-center gap-2">
                  <BrainCircuit className="w-5 h-5 text-[rgb(var(--color-accent))]" />
                  <div>
                    <h3 className="text-lg font-semibold mb-0">Top Value Contributions</h3>
                    <p className="text-xs text-[rgb(var(--color-text-tertiary))] mt-1">
                      Highest-impact commits ranked by AI analysis
                    </p>
                  </div>
                </div>
                <div className="card-body p-0">
                  <div className="divide-y divide-[rgb(var(--color-border))]">
                    {valueData.high_impact_commits.map((commit, i) => (
                      <div key={i} className="p-4 hover:bg-[rgb(var(--color-surface-secondary))] transition-colors flex items-start gap-4">
                        <div className="flex-shrink-0 w-10 h-10 rounded-full bg-[rgb(var(--color-surface-secondary))] border border-[rgb(var(--color-border))] flex items-center justify-center">
                          <span className="text-sm font-bold text-[rgb(var(--color-accent))]">{commit.score}</span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-mono text-xs px-1.5 py-0.5 bg-[rgb(var(--color-surface-secondary))] rounded text-[rgb(var(--color-text-secondary))]">
                              {commit.hash}
                            </span>
                            <span className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded
                              ${commit.complexity === 'high' ? 'bg-[rgba(205,100,100,0.15)] text-[rgb(var(--color-error))]' : 
                                commit.complexity === 'medium' ? 'bg-[rgba(218,175,95,0.15)] text-[rgb(var(--color-warning))]' : 
                                'bg-[rgba(120,180,120,0.15)] text-[rgb(var(--color-success))]'}`}>
                              {commit.complexity}
                            </span>
                          </div>
                          <p className="text-sm font-medium text-[rgb(var(--color-text-primary))] truncate">
                            {commit.message}
                          </p>
                          <p className="text-xs text-[rgb(var(--color-text-tertiary))] mt-1 line-clamp-1">
                            {commit.reasoning}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

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
                        <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke={CHART_COLORS.grid} />
                        <XAxis type="number" hide />
                        <YAxis 
                          dataKey="name" 
                          type="category" 
                          width={100}
                          tick={{ fill: CHART_COLORS.tick, fontSize: 12 }} 
                        />
                        <Tooltip />
                        <Bar dataKey="value" fill={CHART_COLORS.accent} radius={[0, 4, 4, 0]} barSize={20} />
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
                    <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} />
                    <XAxis 
                      dataKey="date" 
                      tick={{ fill: CHART_COLORS.tick, fontSize: 10 }}
                      tickFormatter={(value) => value.slice(5)}
                    />
                    <YAxis tick={{ fill: CHART_COLORS.tick, fontSize: 12 }} />
                    <Tooltip />
                    <Line 
                      type="monotone" 
                      dataKey="commits" 
                      stroke={CHART_COLORS.accent} 
                      strokeWidth={2} 
                      dot={{ fill: CHART_COLORS.accent, r: 3 }} 
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
                      <tr key={idx} className="border-b border-[rgb(var(--color-border))] hover:bg-[rgb(var(--color-surface-secondary))]">
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
                          <span className="text-[rgb(var(--color-success))]">+{commit.lines_added}</span>
                          {' / '}
                          <span className="text-[rgb(var(--color-error))]">-{commit.lines_deleted}</span>
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
