import { useEffect, useState } from 'react';
import { CheckSquare, Clock, AlertCircle, CheckCircle, Circle } from 'lucide-react';
import AdminLayout from '../components/AdminLayout';
import { taskAPI } from '../lib/api';

interface Task {
  id: string;
  _id?: string;
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
  const [updatingId, setUpdatingId] = useState<string | null>(null);

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

  const handleStatusChange = async (taskId: string, newStatus: string) => {
    setUpdatingId(taskId);
    try {
      // Call backend API to update status
      await taskAPI.update(taskId, { status: newStatus });
      
      // Update locally for instant feedback
      setTasks(tasks.map(t => 
        (t.id === taskId || t._id === taskId) ? { ...t, status: newStatus } : t
      ));
    } catch (err) {
      console.error('Failed to update task:', err);
      alert('Failed to update task status');
      // Reload to get correct state
      loadTasks();
    } finally {
      setUpdatingId(null);
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

  const getTaskId = (task: Task) => task.id || task._id || '';

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
              <span className="ml-2 px-2 py-0.5 bg-[rgba(var(--color-text-primary),0.1)] rounded text-xs">
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
              <div key={getTaskId(task)} className="card hover:border-[rgb(var(--color-accent))] transition-colors">
                <div className="card-body">
                  <div className="flex items-start gap-4">
                    <div className="mt-1">
                      {getStatusIcon(task.status)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4 mb-2">
                        <h3 className="text-lg font-semibold mb-1">{task.title}</h3>
                        <div className="flex gap-2 flex-shrink-0 items-center">
                          {/* Status Dropdown */}
                          <select
                            value={task.status}
                            onChange={(e) => handleStatusChange(getTaskId(task), e.target.value)}
                            disabled={updatingId === getTaskId(task)}
                            className="input text-sm py-1 px-2 min-w-[120px]"
                          >
                            <option value="todo">To Do</option>
                            <option value="in_progress">In Progress</option>
                            <option value="done">Done</option>
                            <option value="blocked">Blocked</option>
                          </select>
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
                          <div className="flex items-center gap-1.5 px-2 py-1 bg-[rgb(var(--color-surface-secondary))] rounded-full border border-[rgb(var(--color-border))]">
                            <span className="text-[10px] uppercase font-semibold tracking-wider opacity-70">Assigned:</span>
                            <span className="font-medium text-[rgb(var(--color-text-primary))]">
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
