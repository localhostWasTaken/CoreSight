import { useEffect, useState } from 'react';
import { FolderKanban, Plus } from 'lucide-react';
import AdminLayout from '../components/AdminLayout';
import { projectAPI } from '../lib/api';

interface Project {
  id: string;
  name: string;
  repo_url?: string;
  total_budget: number;
  created_at: string;
}

export default function Projects() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

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
              <div key={project.id} className="card hover:border-[rgb(var(--color-accent))] transition-colors cursor-pointer">
                <div className="card-body">
                  <div className="flex items-start gap-3 mb-4">
                    <FolderKanban className="w-6 h-6 text-[rgb(var(--color-text-secondary))] flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-semibold mb-1">{project.name}</h3>
                      {project.repo_url && (
                        <p className="text-xs text-[rgb(var(--color-text-tertiary))] truncate">
                          {project.repo_url}
                        </p>
                      )}
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-[rgb(var(--color-text-secondary))]">Budget</span>
                      <span className="text-sm font-semibold">${project.total_budget.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-[rgb(var(--color-text-secondary))]">Created</span>
                      <span className="text-sm">{new Date(project.created_at).toLocaleDateString()}</span>
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
