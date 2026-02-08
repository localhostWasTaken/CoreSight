import { useEffect, useState } from 'react';
import { BarChart3, TrendingUp, TrendingDown, Users as UsersIcon, Activity } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import AdminLayout from '../components/AdminLayout';
import { analyticsAPI, userAPI } from '../lib/api';

interface UserProfile {
  user_id: string;
  profile: string;
  total_commits: number;
  overall_refactor_ratio: number;
}

export default function Analytics() {
  const [loading, setLoading] = useState(true);
  const [userProfiles, setUserProfiles] = useState<UserProfile[]>([]);
  const [selectedMetric, setSelectedMetric] = useState<'impact' | 'focus'>('impact');

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      // Load users first
      const usersRes = await userAPI.list();
      const users = usersRes.data;

      // Try to load impact data for each user
      const profilePromises = users.slice(0, 5).map(async (user: any) => {
        const userId = user.id || user._id;
        try {
          const impactRes = await analyticsAPI.userImpact(userId);
          return {
            user_id: userId,
            user_name: user.name,
            profile: impactRes.data.data.profile || 'balanced',
            total_commits: impactRes.data.data.total_commits || 0,
            overall_refactor_ratio: impactRes.data.data.overall_refactor_ratio || 0,
          };
        } catch {
          return null;
        }
      });

      const profiles = (await Promise.all(profilePromises)).filter(Boolean) as UserProfile[];
      setUserProfiles(profiles);
    } catch (err) {
      console.error('Failed to load analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  // Mock data for visualization
  const profileDistribution = [
    { name: 'Makers', value: userProfiles.filter(u => u.profile === 'maker').length || 3, color: '#22c55e' },
    { name: 'Menders', value: userProfiles.filter(u => u.profile === 'mender').length || 2, color: '#3b82f6' },
    { name: 'Cleaners', value: userProfiles.filter(u => u.profile === 'cleaner').length || 1, color: '#eab308' },
    { name: 'Balanced', value: userProfiles.filter(u => u.profile === 'balanced').length || 4, color: '#6366f1' },
  ];

  const commitData = userProfiles.length > 0 ? userProfiles.map(u => ({
    name: (u as any).user_name || u.user_id.slice(0, 8),
    commits: u.total_commits,
  })) : [
    { name: 'User A', commits: 45 },
    { name: 'User B', commits: 32 },
    { name: 'User C', commits: 28 },
    { name: 'User D', commits: 21 },
  ];

  return (
    <AdminLayout>
      <div className="max-w-7xl">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight mb-2">Analytics & Insights</h1>
          <p className="text-[rgb(var(--color-text-secondary))]">
            Business intelligence derived from low-level engineering metrics
          </p>
        </div>

        {/* Metric Selector */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setSelectedMetric('impact')}
            className={`btn ${selectedMetric === 'impact' ? 'btn-primary' : 'btn-secondary'}`}
          >
            <BarChart3 className="w-4 h-4" />
            Code Impact Analysis
          </button>
          <button
            onClick={() => setSelectedMetric('focus')}
            className={`btn ${selectedMetric === 'focus' ? 'btn-primary' : 'btn-secondary'}`}
          >
            <Activity className="w-4 h-4" />
            Focus Health
          </button>
        </div>

        {loading ? (
          <div className="text-center py-12 text-[rgb(var(--color-text-secondary))]">
            Loading analytics...
          </div>
        ) : (
          <>
            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="stat-card">
                <div className="flex items-center justify-between mb-4">
                  <UsersIcon className="w-6 h-6 text-[rgb(var(--color-text-secondary))]" />
                  <TrendingUp className="w-4 h-4 text-[rgb(var(--color-success))]" />
                </div>
                <div className="stat-label">Total Contributors</div>
                <div className="stat-value">{userProfiles.length || 10}</div>
              </div>

              <div className="stat-card">
                <div className="flex items-center justify-between mb-4">
                  <BarChart3 className="w-6 h-6 text-[rgb(var(--color-text-secondary))]" />
                </div>
                <div className="stat-label">Makers</div>
                <div className="stat-value" style={{ color: 'rgb(34, 197, 94)' }}>
                  {profileDistribution[0].value}
                </div>
                <div className="stat-change text-[rgb(var(--color-text-tertiary))]">
                  Feature builders
                </div>
              </div>

              <div className="stat-card">
                <div className="flex items-center justify-between mb-4">
                  <Activity className="w-6 h-6 text-[rgb(var(--color-text-secondary))]" />
                </div>
                <div className="stat-label">Menders</div>
                <div className="stat-value" style={{ color: 'rgb(59, 130, 246)' }}>
                  {profileDistribution[1].value}
                </div>
                <div className="stat-change text-[rgb(var(--color-text-tertiary))]">
                  Refactorers
                </div>
              </div>

              <div className="stat-card">
                <div className="flex items-center justify-between mb-4">
                  <TrendingDown className="w-6 h-6 text-[rgb(var(--color-text-secondary))]" />
                </div>
                <div className="stat-label">Avg Refactor Ratio</div>
                <div className="stat-value">
                  {userProfiles.length > 0 
                    ? (userProfiles.reduce((acc, u) => acc + u.overall_refactor_ratio, 0) / userProfiles.length).toFixed(2)
                    : '0.42'
                  }
                </div>
              </div>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              {/* Commit Activity */}
              <div className="card">
                <div className="card-header">
                  <h3 className="text-lg font-semibold mb-0">Commit Activity</h3>
                  <p className="text-xs text-[rgb(var(--color-text-tertiary))] mt-1">
                    Top contributors by commit count
                  </p>
                </div>
                <div className="card-body">
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={commitData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgb(228, 228, 231)" />
                      <XAxis 
                        dataKey="name" 
                        tick={{ fill: 'rgb(82, 82, 91)', fontSize: 12 }}
                        axisLine={{ stroke: 'rgb(228, 228, 231)' }}
                      />
                      <YAxis 
                        tick={{ fill: 'rgb(82, 82, 91)', fontSize: 12 }}
                        axisLine={{ stroke: 'rgb(228, 228, 231)' }}
                      />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: 'white',
                          border: '1px solid rgb(228, 228, 231)',
                          borderRadius: 0
                        }}
                      />
                      <Bar dataKey="commits" fill="rgb(24, 24, 27)" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Profile Distribution */}
              <div className="card">
                <div className="card-header">
                  <h3 className="text-lg font-semibold mb-0">Developer Profiles</h3>
                  <p className="text-xs text-[rgb(var(--color-text-tertiary))] mt-1">
                    Maker vs Mender distribution
                  </p>
                </div>
                <div className="card-body">
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={profileDistribution}
                        cx="50%"
                        cy="50%"
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="value"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      >
                        {profileDistribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                  
                  <div className="grid grid-cols-2 gap-4 mt-6">
                    {profileDistribution.map((profile) => (
                      <div key={profile.name} className="flex items-center gap-2">
                        <div 
                          className="w-3 h-3 flex-shrink-0"
                          style={{ backgroundColor: profile.color }}
                        />
                        <span className="text-sm text-[rgb(var(--color-text-secondary))]">
                          {profile.name}: {profile.value}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Profile Insights */}
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold mb-0">Profile Insights</h3>
              </div>
              <div className="card-body">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-semibold mb-3">Makers (Feature Builders)</h4>
                    <ul className="space-y-2 text-sm text-[rgb(var(--color-text-secondary))]">
                      <li>• 50%+ commits are new features</li>
                      <li>• Low refactor ratio (&lt;0.3)</li>
                      <li>• Drive product innovation</li>
                      <li>• High code addition rate</li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-semibold mb-3">Menders (Maintainers)</h4>
                    <ul className="space-y-2 text-sm text-[rgb(var(--color-text-secondary))]">
                      <li>• 40%+ commits are refactoring</li>
                      <li>• Moderate refactor ratio (0.3-0.6)</li>
                      <li>• Improve code quality</li>
                      <li>• Balance additions and modifications</li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-semibold mb-3">Cleaners (Tech Debt)</h4>
                    <ul className="space-y-2 text-sm text-[rgb(var(--color-text-secondary))]">
                      <li>• 40%+ commits are cleanup</li>
                      <li>• High refactor ratio (&gt;0.6)</li>
                      <li>• Remove legacy code</li>
                      <li>• Reduce codebase complexity</li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-semibold mb-3">Balanced (Generalists)</h4>
                    <ul className="space-y-2 text-sm text-[rgb(var(--color-text-secondary))]">
                      <li>• Mix of all work types</li>
                      <li>• Versatile developers</li>
                      <li>• Handle diverse tasks</li>
                      <li>• Adaptable to team needs</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </AdminLayout>
  );
}
