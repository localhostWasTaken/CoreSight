import { useState, useEffect, FormEvent } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Save } from 'lucide-react';
import AdminLayout from '../components/AdminLayout';
import { userAPI } from '../lib/api';

export default function UserForm() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const isEditMode = Boolean(id);
  
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(isEditMode);
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    role: 'employee',
    hourly_rate: 50,
    skills: '',
    github_username: '',
    jira_account_id: '',
  });

  // Fetch user data if editing
  useEffect(() => {
    if (isEditMode && id) {
      fetchUser();
    }
  }, [id]);

  const fetchUser = async () => {
    try {
      const response = await userAPI.get(id!);
      const user = response.data;
      setFormData({
        name: user.name || '',
        email: user.email || '',
        role: user.role || 'employee',
        hourly_rate: user.hourly_rate || 50,
        skills: (user.skills || []).join(', '),
        github_username: user.github_username || '',
        jira_account_id: user.jira_account_id || '',
      });
    } catch (err) {
      setError('Failed to load user');
      console.error(err);
    } finally {
      setFetching(false);
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const payload = {
        ...formData,
        skills: formData.skills.split(',').map(s => s.trim()).filter(Boolean),
        github_username: formData.github_username || undefined,
        jira_account_id: formData.jira_account_id || undefined,
      };

      if (isEditMode) {
        await userAPI.update(id!, payload);
      } else {
        await userAPI.create(payload);
      }
      navigate('/users');
    } catch (err: any) {
      setError(err.response?.data?.detail || `Failed to ${isEditMode ? 'update' : 'create'} user`);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (fetching) {
    return (
      <AdminLayout>
        <div className="max-w-3xl">
          <div className="text-center py-12 text-[rgb(var(--color-text-secondary))]">
            Loading user...
          </div>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <div className="max-w-3xl">
        {/* Page Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/users')}
            className="btn btn-ghost mb-4 px-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Users
          </button>
          <h1 className="text-3xl font-bold tracking-tight mb-2">
            {isEditMode ? 'Edit User' : 'Add New User'}
          </h1>
          <p className="text-[rgb(var(--color-text-secondary))]">
            {isEditMode 
              ? 'Update team member profile and work information'
              : 'Create a new team member profile with skills and work information'
            }
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700">
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit}>
          <div className="card">
            <div className="card-body space-y-6">
              {/* Basic Info */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Basic Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="name" className="label">
                      Full Name *
                    </label>
                    <input
                      id="name"
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="input"
                      required
                    />
                  </div>
                  <div>
                    <label htmlFor="email" className="label">
                      Email Address *
                    </label>
                    <input
                      id="email"
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className="input"
                      required
                    />
                  </div>
                </div>
              </div>

              {/* Role & Rate */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Work Details</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="role" className="label">
                      Role *
                    </label>
                    <select
                      id="role"
                      value={formData.role}
                      onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                      className="input"
                      required
                    >
                      <option value="employee">Employee</option>
                      <option value="contractor">Contractor</option>
                      <option value="manager">Manager</option>
                      <option value="admin">Admin</option>
                    </select>
                  </div>
                  <div>
                    <label htmlFor="hourly_rate" className="label">
                      Hourly Rate ($)
                    </label>
                    <input
                      id="hourly_rate"
                      type="number"
                      min="0"
                      step="0.01"
                      value={formData.hourly_rate}
                      onChange={(e) => setFormData({ ...formData, hourly_rate: parseFloat(e.target.value) })}
                      className="input"
                    />
                  </div>
                </div>
              </div>

              {/* Skills */}
              <div>
                <label htmlFor="skills" className="label">
                  Skills (comma-separated)
                </label>
                <input
                  id="skills"
                  type="text"
                  value={formData.skills}
                  onChange={(e) => setFormData({ ...formData, skills: e.target.value })}
                  className="input"
                  placeholder="Python, React, AWS, Docker"
                />
                <p className="text-xs text-[rgb(var(--color-text-tertiary))] mt-1">
                  Enter skills separated by commas
                </p>
              </div>

              {/* Integrations */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Integration Accounts</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="github_username" className="label">
                      GitHub Username
                    </label>
                    <input
                      id="github_username"
                      type="text"
                      value={formData.github_username}
                      onChange={(e) => setFormData({ ...formData, github_username: e.target.value })}
                      className="input"
                      placeholder="octocat"
                    />
                  </div>
                  <div>
                    <label htmlFor="jira_account_id" className="label">
                      Jira Account ID
                    </label>
                    <input
                      id="jira_account_id"
                      type="text"
                      value={formData.jira_account_id}
                      onChange={(e) => setFormData({ ...formData, jira_account_id: e.target.value })}
                      className="input"
                      placeholder="5b10ac8d82e05b22cc7d4ef5"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="card-body border-t border-[rgb(var(--color-border))] flex flex-row gap-3 justify-end">
              <button
                type="button"
                onClick={() => navigate('/users')}
                className="btn btn-secondary"
                disabled={loading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading}
              >
                <Save className="w-4 h-4" />
                {loading ? (isEditMode ? 'Saving...' : 'Creating...') : (isEditMode ? 'Save Changes' : 'Create User')}
              </button>
            </div>
          </div>
        </form>
      </div>
    </AdminLayout>
  );
}
