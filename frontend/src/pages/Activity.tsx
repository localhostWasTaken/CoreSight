import { useEffect, useState } from 'react';
import { GitCommit, GitBranch, Clock, Code, FileCode } from 'lucide-react';
import AdminLayout from '../components/AdminLayout';
import { commitAPI } from '../lib/api';

interface Commit {
  id: string;
  _id?: string;
  commit_hash?: string;
  sha?: string;
  commit_message?: string;
  message?: string;
  author_name: string;
  author_email?: string;
  committed_at?: string;
  created_at?: string;
  repository?: string;
  branch?: string;
  lines_added?: number;
  lines_deleted?: number;
  lines_modified?: number;
  files_changed?: string[] | number;
  extracted_skills?: string[];
  summary?: string;
  diff_content?: string;
}

export default function Activity() {
  const [commits, setCommits] = useState<Commit[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);

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

  const getCommitId = (c: Commit) => c.id || c._id || c.commit_hash || '';
  const getCommitHash = (c: Commit) => c.commit_hash || c.sha || c.id || c._id || 'unknown';
  const getCommitMessage = (c: Commit) => c.commit_message || c.message || 'No message';
  const getCommitDate = (c: Commit) => c.created_at || c.committed_at;

  const formatTimeAgo = (date: string | undefined) => {
    if (!date) return 'Unknown';
    
    const now = new Date();
    const past = new Date(date);
    
    // Check if date is valid
    if (isNaN(past.getTime())) {
      return 'Unknown';
    }
    
    const diffMs = now.getTime() - past.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 30) return `${diffDays}d ago`;
    return past.toLocaleDateString();
  };

  const getFilesCount = (c: Commit): number => {
    if (Array.isArray(c.files_changed)) return c.files_changed.length;
    if (typeof c.files_changed === 'number') return c.files_changed;
    return 0;
  };

  return (
    <AdminLayout>
      <div className="max-w-5xl">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight mb-2">Activity Feed</h1>
          <p className="text-[rgb(var(--color-text-secondary))]">
            Real-time commit activity and code changes from GitHub webhooks
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
            <p className="text-[rgb(var(--color-text-secondary))] mb-2">
              No recent activity found.
            </p>
            <p className="text-xs text-[rgb(var(--color-text-tertiary))]">
              Configure a GitHub webhook to see commits here.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {commits.map((commit) => (
              <div 
                key={getCommitId(commit)} 
                className="card hover:border-[rgb(var(--color-accent))] transition-colors cursor-pointer"
                onClick={() => setExpandedId(expandedId === getCommitId(commit) ? null : getCommitId(commit))}
              >
                <div className="card-body">
                  <div className="flex gap-4">
                    <div className="flex-shrink-0 mt-1">
                      <GitBranch className="w-5 h-5 text-[rgb(var(--color-accent))]" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4 mb-2">
                        <div className="flex-1">
                          <p className="font-medium mb-1">{getCommitMessage(commit)}</p>
                          <div className="flex items-center gap-3 text-xs text-[rgb(var(--color-text-tertiary))]">
                            <span className="font-medium text-[rgb(var(--color-text-secondary))]">
                              {commit.author_name}
                            </span>
                            <span>•</span>
                            <span className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {formatTimeAgo(getCommitDate(commit))}
                            </span>
                            <span>•</span>
                            <code className="text-xs bg-[rgb(var(--color-surface-secondary))] px-2 py-0.5 font-mono">
                              {getCommitHash(commit).slice(0, 7)}
                            </code>
                          </div>
                        </div>
                      </div>

                      {/* Stats Row */}
                      <div className="flex items-center gap-4 text-xs mt-3">
                        <div className="flex items-center gap-1 text-[rgb(var(--color-success))]">
                          <span>+{commit.lines_added || 0}</span>
                        </div>
                        <div className="flex items-center gap-1 text-[rgb(var(--color-error))]">
                          <span>-{commit.lines_deleted || 0}</span>
                        </div>
                        {getFilesCount(commit) > 0 && (
                          <>
                            <span className="text-[rgb(var(--color-text-tertiary))]">•</span>
                            <span className="flex items-center gap-1 text-[rgb(var(--color-text-tertiary))]">
                              <FileCode className="w-3 h-3" />
                              {getFilesCount(commit)} file{getFilesCount(commit) !== 1 ? 's' : ''}
                            </span>
                          </>
                        )}
                        {commit.repository && (
                          <>
                            <span className="text-[rgb(var(--color-text-tertiary))]">•</span>
                            <span className="text-[rgb(var(--color-text-tertiary))]">
                              {commit.repository}
                            </span>
                          </>
                        )}
                        {commit.branch && (
                          <span className="badge badge-neutral text-xs">{commit.branch}</span>
                        )}
                      </div>

                      {/* Extracted Skills */}
                      {commit.extracted_skills && commit.extracted_skills.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-3">
                          {commit.extracted_skills.map((skill, idx) => (
                            <span key={idx} className="badge badge-info text-xs">
                              {skill}
                            </span>
                          ))}
                        </div>
                      )}

                      {/* Expanded Details */}
                      {expandedId === getCommitId(commit) && (
                        <div className="mt-4 pt-4 border-t border-[rgb(var(--color-border))]">
                          {commit.summary && (
                            <div className="mb-3">
                              <h4 className="text-xs font-semibold text-[rgb(var(--color-text-secondary))] mb-1">
                                AI Summary
                              </h4>
                              <p className="text-sm text-[rgb(var(--color-text-secondary))]">
                                {commit.summary}
                              </p>
                            </div>
                          )}
                          
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <span className="text-xs text-[rgb(var(--color-text-tertiary))]">Author</span>
                              <p className="font-medium">{commit.author_name}</p>
                              {commit.author_email && (
                                <p className="text-xs text-[rgb(var(--color-text-tertiary))]">{commit.author_email}</p>
                              )}
                            </div>
                            <div>
                              <span className="text-xs text-[rgb(var(--color-text-tertiary))]">Committed</span>
                              <p className="font-medium">
                                {getCommitDate(commit) 
                                  ? new Date(getCommitDate(commit)!).toLocaleString()
                                  : 'Unknown'
                                }
                              </p>
                            </div>
                          </div>

                          <div className="mt-3">
                            <span className="text-xs text-[rgb(var(--color-text-tertiary))]">Full Commit Hash</span>
                            <p className="font-mono text-xs bg-[rgb(var(--color-surface-secondary))] px-2 py-1 mt-1">
                              {getCommitHash(commit)}
                            </p>
                          </div>
                        </div>
                      )}
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
