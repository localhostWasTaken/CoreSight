import { useEffect, useState } from 'react';
import { GitCommit, GitBranch, Clock } from 'lucide-react';
import AdminLayout from '../components/AdminLayout';
import { commitAPI } from '../lib/api';

interface Commit {
  id: string;
  sha: string;
  message: string;
  author_name: string;
  committed_at: string;
  lines_added: number;
  lines_deleted: number;
  lines_modified: number;
  files_changed: string[];
}

export default function Activity() {
  const [commits, setCommits] = useState<Commit[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadActivity();
  }, []);

  const loadActivity = async () => {
    try {
      const response = await commitAPI.list();
      setCommits(response.data);
    } catch (err) {
      console.error('Failed to load activity:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatTimeAgo = (date: string) => {
    const now = new Date();
    const past = new Date(date);
    const diffMs = now.getTime() - past.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  return (
    <AdminLayout>
      <div className="max-w-5xl">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight mb-2">Activity Feed</h1>
          <p className="text-[rgb(var(--color-text-secondary))]">
            Real-time commit activity and code changes
          </p>
        </div>

        {/* Activity Timeline */}
        {loading ? (
          <div className="text-center py-12 text-[rgb(var(--color-text-secondary))]">
            Loading activity...
          </div>
        ) : commits.length === 0 ? (
          <div className="card card-body text-center py-12">
            <GitCommit className="w-12 h-12 mx-auto mb-4 text-[rgb(var(--color-text-tertiary))]" />
            <p className="text-[rgb(var(--color-text-secondary))]">
              No recent activity found.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {commits.map((commit) => (
              <div key={commit.id} className="card hover:border-[rgb(var(--color-accent))] transition-colors">
                <div className="card-body">
                  <div className="flex gap-4">
                    <div className="flex-shrink-0 mt-1">
                      <GitBranch className="w-5 h-5 text-[rgb(var(--color-text-secondary))]" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4 mb-2">
                        <div className="flex-1">
                          <p className="font-medium mb-1">{commit.message}</p>
                          <div className="flex items-center gap-3 text-xs text-[rgb(var(--color-text-tertiary))]">
                            <span className="font-medium text-[rgb(var(--color-text-secondary))]">
                              {commit.author_name}
                            </span>
                            <span>•</span>
                            <span>{formatTimeAgo(commit.committed_at)}</span>
                            <span>•</span>
                            <code className="text-xs bg-[rgb(var(--color-surface-secondary))] px-2 py-0.5 font-mono">
                              {commit.sha.slice(0, 7)}
                            </code>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-4 text-xs mt-3">
                        <div className="flex items-center gap-1 text-[rgb(var(--color-success))]">
                          <span>+{commit.lines_added}</span>
                        </div>
                        <div className="flex items-center gap-1 text-[rgb(var(--color-error))]">
                          <span>-{commit.lines_deleted}</span>
                        </div>
                        <div className="flex items-center gap-1 text-[rgb(var(--color-text-tertiary))]">
                          <span>~{commit.lines_modified}</span>
                        </div>
                        {commit.files_changed.length > 0 && (
                          <>
                            <span className="text-[rgb(var(--color-text-tertiary))]">•</span>
                            <span className="text-[rgb(var(--color-text-tertiary))]">
                              {commit.files_changed.length} file{commit.files_changed.length !== 1 ? 's' : ''} changed
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </AdminLayout>
  );
}
