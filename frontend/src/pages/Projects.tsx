import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { FolderKanban, Plus, ExternalLink, Calendar, DollarSign } from 'lucide-react';
import AdminLayout from '../components/AdminLayout';
import { projectAPI } from '../lib/api';

interface Project {
  id: string;
  _id?: string;
  name: string;
  repo_url?: string;
  jira_space_id?: string;
  total_budget: number;
  spent_budget?: number;
  created_at: string;
}

export default function Projects() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const response = await projectAPI.list();
      setProjects(response.data);
    } catch (err) {
      console.error('Failed to load projects:', err);
    } finally {
      setLoading(false);
    }
  };

  const getProjectId = (project: Project) => project.id || project._id || '';

  const getSpentPercentage = (project: Project) => {
    const spent = project.spent_budget || 0;
    return project.total_budget > 0 ? (spent / project.total_budget) * 100 : 0;
  };

  return (
    <AdminLayout>
      <div className="max-w-7xl">
        {/* Page Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold tracking-tight mb-2">Projects</h1>
            <p className="text-[rgb(var(--color-text-secondary))]">
              Manage your project portfolio and budgets
            </p>
          </div>
          <button className="btn btn-primary">
            <Plus className="w-4 h-4" />
            New Project
          </button>
        </div>

        {/* Projects Grid */}
        {loading ? (
          <div className="text-center py-12 text-[rgb(var(--color-text-secondary))]">
            Loading projects...
          </div>
        ) : projects.length === 0 ? (
          <div className="card card-body text-center py-12">
            <FolderKanban className="w-12 h-12 mx-auto mb-4 text-[rgb(var(--color-text-tertiary))]" />
            <p className="text-[rgb(var(--color-text-secondary))]">
              No projects found. Create your first project to get started.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <div 
                key={getProjectId(project)} 
                className="card hover:border-[rgb(var(--color-accent))] hover:shadow-lg transition-all cursor-pointer"
                onClick={() => setSelectedProject(selectedProject?.id === getProjectId(project) ? null : project)}
              >
                <div className="card-body">
                  <div className="flex items-start gap-3 mb-4">
                    <FolderKanban className="w-6 h-6 text-[rgb(var(--color-accent))] flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-semibold mb-1">{project.name}</h3>
                      {project.repo_url && (
                        <a 
                          href={project.repo_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-[rgb(var(--color-info))] hover:underline flex items-center gap-1"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <ExternalLink className="w-3 h-3" />
                          View Repository
                        </a>
                      )}
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    {/* Budget Progress */}
                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-xs text-[rgb(var(--color-text-secondary))]">Budget</span>
                        <span className="text-xs font-medium">
                          ${(project.spent_budget || 0).toLocaleString()} / ${project.total_budget.toLocaleString()}
                        </span>
                      </div>
                      <div className="h-2 bg-[rgb(var(--color-surface-secondary))] rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-[rgb(var(--color-accent))] transition-all"
                          style={{ width: `${Math.min(getSpentPercentage(project), 100)}%` }}
                        />
                      </div>
                    </div>

                    <div className="flex justify-between items-center text-sm">
                      <div className="flex items-center gap-1 text-[rgb(var(--color-text-tertiary))]">
                        <Calendar className="w-3 h-3" />
                        <span>{new Date(project.created_at).toLocaleDateString()}</span>
                      </div>
                      {project.jira_space_id && (
                        <span className="badge badge-info text-xs">Jira Connected</span>
                      )}
                    </div>
                  </div>

                  {/* Expanded Details */}
                  {selectedProject && getProjectId(selectedProject) === getProjectId(project) && (
                    <div className="mt-4 pt-4 border-t border-[rgb(var(--color-border))]">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-[rgb(var(--color-text-tertiary))]">Total Budget</span>
                          <p className="font-semibold">${project.total_budget.toLocaleString()}</p>
                        </div>
                        <div>
                          <span className="text-[rgb(var(--color-text-tertiary))]">Spent</span>
                          <p className="font-semibold text-[rgb(var(--color-warning))]">
                            ${(project.spent_budget || 0).toLocaleString()}
                          </p>
                        </div>
                        {project.jira_space_id && (
                          <div className="col-span-2">
                            <span className="text-[rgb(var(--color-text-tertiary))]">Jira Space</span>
                            <p className="font-mono text-xs">{project.jira_space_id}</p>
                          </div>
                        )}
                      </div>
                      <div className="mt-4 flex gap-2">
                        <button className="btn btn-secondary flex-1 text-xs py-2">
                          View Tasks
                        </button>
                        <button className="btn btn-primary flex-1 text-xs py-2">
                          Edit Project
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </AdminLayout>
  );
}
