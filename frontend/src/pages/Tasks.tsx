import { useEffect, useState } from 'react';
import { CheckSquare, Clock, AlertCircle, CheckCircle, Circle } from 'lucide-react';
import AdminLayout from '../components/AdminLayout';
import { taskAPI } from '../lib/api';

interface Task {
  id: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  assignee_id?: string;
  assignee_name?: string;
  project_id?: string;
  estimated_hours?: number;
  created_at: string;
}

export default function Tasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    loadTasks();
  }, [filter]);

  const loadTasks = async () => {
    try {
      const params = filter !== 'all' ? { status: filter } : undefined;
      const response = await taskAPI.list(params);
      setTasks(response.data);
    } catch (err) {
      console.error('Failed to load tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'done':
        return <CheckCircle className="w-4 h-4 text-[rgb(var(--color-success))]" />;
      case 'in_progress':
        return <Clock className="w-4 h-4 text-[rgb(var(--color-info))]" />;
      case 'blocked':
        return <AlertCircle className="w-4 h-4 text-[rgb(var(--color-error))]" />;
      default:
        return <Circle className="w-4 h-4 text-[rgb(var(--color-text-tertiary))]" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const classes: Record<string, string> = {
      done: 'badge-success',
      in_progress: 'badge-info',
      blocked: 'badge-error',
      todo: 'badge-neutral',
    };
    return `badge ${classes[status] || 'badge-neutral'}`;
  };

  const getPriorityBadge = (priority: string) => {
    const classes: Record<string, string> = {
      high: 'badge-error',
      medium: 'badge-warning',
      low: 'badge-info',
    };
    return `badge ${classes[priority] || 'badge-neutral'}`;
  };

  const statusCounts = {
    all: tasks.length,
    todo: tasks.filter(t => t.status === 'todo').length,
    in_progress: tasks.filter(t => t.status === 'in_progress').length,
    done: tasks.filter(t => t.status === 'done').length,
    blocked: tasks.filter(t => t.status === 'blocked').length,
  };

  return (
    <AdminLayout>
      <div className="max-w-7xl">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight mb-2">Tasks</h1>
          <p className="text-[rgb(var(--color-text-secondary))]">
            Track and manage project tasks and assignments
          </p>
        </div>

        {/* Filters */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {[
            { key: 'all', label: 'All Tasks' },
            { key: 'todo', label: 'To Do' },
            { key: 'in_progress', label: 'In Progress' },
            { key: 'done', label: 'Done' },
            { key: 'blocked', label: 'Blocked' },
          ].map(({ key, label }) => (
            <button
              key={key}
              onClick={() => setFilter(key)}
              className={`btn ${filter === key ? 'btn-primary' : 'btn-secondary'} whitespace-nowrap`}
            >
              {label}
              <span className="ml-2 px-2 py-0.5 bg-black/10 rounded text-xs">
                {statusCounts[key as keyof typeof statusCounts]}
              </span>
            </button>
          ))}
        </div>

        {/* Tasks Grid */}
        {loading ? (
          <div className="text-center py-12 text-[rgb(var(--color-text-secondary))]">
            Loading tasks...
          </div>
        ) : tasks.length === 0 ? (
          <div className="card card-body text-center py-12">
            <CheckSquare className="w-12 h-12 mx-auto mb-4 text-[rgb(var(--color-text-tertiary))]" />
            <p className="text-[rgb(var(--color-text-secondary))]">
              No tasks found for the selected filter.
            </p>
          </div>
        ) : (
          <div className="grid gap-4">
            {tasks.map((task) => (
              <div key={task.id} className="card hover:border-[rgb(var(--color-accent))] transition-colors">
                <div className="card-body">
                  <div className="flex items-start gap-4">
                    <div className="mt-1">
                      {getStatusIcon(task.status)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4 mb-2">
                        <h3 className="text-lg font-semibold mb-1">{task.title}</h3>
                        <div className="flex gap-2 flex-shrink-0">
                          <span className={getStatusBadge(task.status)}>
                            {task.status.replace('_', ' ')}
                          </span>
                          {task.priority && (
                            <span className={getPriorityBadge(task.priority)}>
                              {task.priority}
                            </span>
                          )}
                        </div>
                      </div>
                      
                      {task.description && (
                        <p className="text-sm text-[rgb(var(--color-text-secondary))] mb-3 line-clamp-2">
                          {task.description}
                        </p>
                      )}

                      <div className="flex items-center gap-4 text-xs text-[rgb(var(--color-text-tertiary))]">
                        {task.assignee_name && (
                          <div className="flex items-center gap-1">
                            <span>Assigned to:</span>
                            <span className="font-medium text-[rgb(var(--color-text-secondary))]">
                              {task.assignee_name}
                            </span>
                          </div>
                        )}
                        {task.estimated_hours && (
                          <div className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            <span>{task.estimated_hours}h estimated</span>
                          </div>
                        )}
                        <div>
                          Created: {new Date(task.created_at).toLocaleDateString()}
                        </div>
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
