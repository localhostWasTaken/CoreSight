import { useEffect, useState } from 'react';
import { BarChart3, TrendingUp, TrendingDown, Users as UsersIcon, Activity, FolderGit2, GitCommit, Bug, Zap, Wrench } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import AdminLayout from '../components/AdminLayout';
import { analyticsAPI, userAPI, projectAPI } from '../lib/api';

interface OverviewStats {
  total_commits: number;
  total_projects: number;
  total_users: number;
  active_contributors: number;
  total_lines_added: number;
  total_lines_deleted: number;
  net_lines: number;
  total_tasks: number;
  task_types: Record<string, number>;
  work_breakdown: {
    new_feature: number;
    refactor: number;
    maintenance: number;
    other: number;
  };
}

interface ProjectStat {
  project_id: string;
  project_name: string;
  repo_url: string;
  total_commits: number;
  lines_added: number;
  lines_deleted: number;
  net_lines: number;
  contributor_count: number;
  contributors: string[];
  task_breakdown: {
    features: number;
    bugs: number;
    tasks: number;
  };
  total_tasks: number;
}

interface CommitActivity {
  date: string;
  commits: number;
  lines_added: number;
  lines_deleted: number;
  by_project: Record<string, number>;
}

export default function Analytics() {
  const [loading, setLoading] = useState(true);
  const [overview, setOverview] = useState<OverviewStats | null>(null);
  const [projectStats, setProjectStats] = useState<ProjectStat[]>([]);
  const [commitActivity, setCommitActivity] = useState<CommitActivity[]>([]);
  const [projectByCommits, setProjectByCommits] = useState<Record<string, number>>({});
  const [selectedProject, setSelectedProject] = useState<string>('all');
  const [projects, setProjects] = useState<{id: string, name: string}[]>([]);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      // Load all analytics data in parallel
      const [overviewRes, projectsRes, activityRes, projectListRes] = await Promise.all([
        analyticsAPI.overview(),
        analyticsAPI.projects(),
        analyticsAPI.commitActivity(30),
        projectAPI.list()
      ]);

      if (overviewRes.data.success) {
        setOverview(overviewRes.data.data);
      }

      if (projectsRes.data.success) {
        setProjectStats(projectsRes.data.data.projects || []);
      }

      if (activityRes.data.success) {
        setCommitActivity(activityRes.data.data.activity || []);
        setProjectByCommits(activityRes.data.data.by_project || {});
      }

      // Get project list for filter
      const projList = projectListRes.data || [];
      setProjects(projList.map((p: any) => ({ id: p.id || p._id, name: p.name })));
    } catch (err) {
      console.error('Failed to load analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  // Work breakdown pie chart data
  const workBreakdownData = overview ? [
    { name: 'New Features', value: overview.work_breakdown.new_feature, color: '#22c55e' },
    { name: 'Bug Fixes (Refactor)', value: overview.work_breakdown.refactor, color: '#ef4444' },
    { name: 'Maintenance', value: overview.work_breakdown.maintenance, color: '#3b82f6' },
    { name: 'Other', value: overview.work_breakdown.other, color: '#6b7280' },
  ].filter(d => d.value > 0) : [];

  // Project commit data for bar chart
  const projectCommitData = projectStats.slice(0, 6).map(p => ({
    name: p.project_name.length > 12 ? p.project_name.slice(0, 12) + '...' : p.project_name,
    commits: p.total_commits,
    features: p.task_breakdown?.features || 0,
    bugs: p.task_breakdown?.bugs || 0,
  }));

  // Recent commit activity for line chart (last 14 days)
  const recentActivity = commitActivity.slice(-14);

  // Filter commit activity by project
  const filteredActivity = selectedProject === 'all' 
    ? recentActivity 
    : recentActivity.map(day => ({
        ...day,
        commits: day.by_project?.[selectedProject] || 0
      }));

  return (
    <AdminLayout>
      <div className="max-w-7xl">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight mb-2">Analytics & Insights</h1>
          <p className="text-[rgb(var(--color-text-secondary))]">
            Live data from GitHub commits and Jira tasks
          </p>
        </div>

        {loading ? (
          <div className="text-center py-12 text-[rgb(var(--color-text-secondary))]">
            Loading live analytics...
          </div>
        ) : (
          <>
            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
              <div className="stat-card">
                <div className="flex items-center justify-between mb-3">
                  <GitCommit className="w-5 h-5 text-[rgb(var(--color-text-secondary))]" />
                </div>
                <div className="stat-label">Commits</div>
                <div className="stat-value">{overview?.total_commits || 0}</div>
              </div>

              <div className="stat-card">
                <div className="flex items-center justify-between mb-3">
                  <FolderGit2 className="w-5 h-5 text-[rgb(var(--color-text-secondary))]" />
                </div>
                <div className="stat-label">Projects</div>
                <div className="stat-value">{overview?.total_projects || 0}</div>
              </div>

              <div className="stat-card">
                <div className="flex items-center justify-between mb-3">
                  <Zap className="w-5 h-5 text-green-600" />
                </div>
                <div className="stat-label">Features</div>
                <div className="stat-value text-green-600">{overview?.work_breakdown?.new_feature || 0}</div>
              </div>

              <div className="stat-card">
                <div className="flex items-center justify-between mb-3">
                  <Bug className="w-5 h-5 text-red-600" />
                </div>
                <div className="stat-label">Bug Fixes</div>
                <div className="stat-value text-red-600">{overview?.work_breakdown?.refactor || 0}</div>
              </div>

              <div className="stat-card">
                <div className="flex items-center justify-between mb-3">
                  <Activity className="w-5 h-5 text-[rgb(var(--color-text-secondary))]" />
                </div>
                <div className="stat-label">Net Lines</div>
                <div className="stat-value">
                  {(overview?.net_lines || 0) > 0 ? '+' : ''}{overview?.net_lines?.toLocaleString() || 0}
                </div>
              </div>
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              {/* Work Type Breakdown */}
              <div className="card">
                <div className="card-header">
                  <h3 className="text-lg font-semibold mb-0">Work Type Breakdown</h3>
                  <p className="text-xs text-[rgb(var(--color-text-tertiary))] mt-1">
                    From Jira: Bug = Refactor, Feature = New Development
                  </p>
                </div>
                <div className="card-body">
                  {workBreakdownData.length > 0 ? (
                    <>
                      <ResponsiveContainer width="100%" height={220}>
                        <PieChart>
                          <Pie
                            data={workBreakdownData}
                            cx="50%"
                            cy="50%"
                            outerRadius={75}
                            fill="#8884d8"
                            dataKey="value"
                            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                          >
                            {workBreakdownData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Pie>
                          <Tooltip />
                        </PieChart>
                      </ResponsiveContainer>
                      
                      <div className="grid grid-cols-2 gap-3 mt-4">
                        {workBreakdownData.map((item) => (
                          <div key={item.name} className="flex items-center gap-2">
                            <div 
                              className="w-3 h-3 flex-shrink-0"
                              style={{ backgroundColor: item.color }}
                            />
                            <span className="text-sm text-[rgb(var(--color-text-secondary))]">
                              {item.name}: {item.value}
                            </span>
                          </div>
                        ))}
                      </div>
                    </>
                  ) : (
                    <div className="text-center py-8 text-[rgb(var(--color-text-secondary))]">
                      No task data from Jira
                    </div>
                  )}
                </div>
              </div>

              {/* Commits by Project */}
              <div className="card">
                <div className="card-header">
                  <h3 className="text-lg font-semibold mb-0">Commits by Project</h3>
                  <p className="text-xs text-[rgb(var(--color-text-tertiary))] mt-1">
                    GitHub commit distribution
                  </p>
                </div>
                <div className="card-body">
                  {projectCommitData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={280}>
                      <BarChart data={projectCommitData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgb(228, 228, 231)" />
                        <XAxis 
                          dataKey="name" 
                          tick={{ fill: 'rgb(82, 82, 91)', fontSize: 11 }}
                          axisLine={{ stroke: 'rgb(228, 228, 231)' }}
                        />
                        <YAxis 
                          tick={{ fill: 'rgb(82, 82, 91)', fontSize: 12 }}
                          axisLine={{ stroke: 'rgb(228, 228, 231)' }}
                        />
                        <Tooltip />
                        <Bar dataKey="commits" fill="rgb(24, 24, 27)" name="Commits" />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="text-center py-8 text-[rgb(var(--color-text-secondary))]">
                      No project commit data
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Commit Activity Timeline */}
            <div className="card mb-8">
              <div className="card-header flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold mb-0">Commit Activity (Last 14 Days)</h3>
                  <p className="text-xs text-[rgb(var(--color-text-tertiary))] mt-1">
                    Daily commits from GitHub
                  </p>
                </div>
                <select 
                  value={selectedProject} 
                  onChange={(e) => setSelectedProject(e.target.value)}
                  className="input w-48"
                >
                  <option value="all">All Projects</option>
                  {Object.keys(projectByCommits).map(proj => (
                    <option key={proj} value={proj}>{proj}</option>
                  ))}
                </select>
              </div>
              <div className="card-body">
                {filteredActivity.length > 0 ? (
                  <ResponsiveContainer width="100%" height={220}>
                    <LineChart data={filteredActivity}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgb(228, 228, 231)" />
                      <XAxis 
                        dataKey="date" 
                        tick={{ fill: 'rgb(82, 82, 91)', fontSize: 10 }}
                        tickFormatter={(value) => value.slice(5)}
                      />
                      <YAxis tick={{ fill: 'rgb(82, 82, 91)', fontSize: 12 }} />
                      <Tooltip />
                      <Line type="monotone" dataKey="commits" stroke="rgb(24, 24, 27)" strokeWidth={2} dot={{ fill: 'rgb(24, 24, 27)', r: 3 }} />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="text-center py-8 text-[rgb(var(--color-text-secondary))]">
                    No commit activity data
                  </div>
                )}
              </div>
            </div>

            {/* Project Details Table */}
            {projectStats.length > 0 && (
              <div className="card">
                <div className="card-header">
                  <h3 className="text-lg font-semibold mb-0">Project Details</h3>
                  <p className="text-xs text-[rgb(var(--color-text-tertiary))] mt-1">
                    Combined GitHub + Jira metrics
                  </p>
                </div>
                <div className="card-body overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-zinc-200">
                        <th className="text-left py-3 px-4 font-medium">Project</th>
                        <th className="text-right py-3 px-4 font-medium">Commits</th>
                        <th className="text-right py-3 px-4 font-medium">Features</th>
                        <th className="text-right py-3 px-4 font-medium">Bugs</th>
                        <th className="text-right py-3 px-4 font-medium">Lines +/-</th>
                        <th className="text-right py-3 px-4 font-medium">Contributors</th>
                      </tr>
                    </thead>
                    <tbody>
                      {projectStats.map((project) => (
                        <tr key={project.project_id} className="border-b border-zinc-100 hover:bg-zinc-50">
                          <td className="py-3 px-4">
                            <div className="font-medium">{project.project_name}</div>
                          </td>
                          <td className="text-right py-3 px-4 font-mono">{project.total_commits}</td>
                          <td className="text-right py-3 px-4">
                            <span className="text-green-600">{project.task_breakdown?.features || 0}</span>
                          </td>
                          <td className="text-right py-3 px-4">
                            <span className="text-red-600">{project.task_breakdown?.bugs || 0}</span>
                          </td>
                          <td className="text-right py-3 px-4">
                            <span className="text-green-600">+{project.lines_added.toLocaleString()}</span>
                            {' / '}
                            <span className="text-red-600">-{project.lines_deleted.toLocaleString()}</span>
                          </td>
                          <td className="text-right py-3 px-4">{project.contributor_count}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </AdminLayout>
  );
}
