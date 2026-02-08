import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { UserPlus, Mail, Trash2, Edit, TrendingUp } from 'lucide-react';
import AdminLayout from '../components/AdminLayout';
import { userAPI } from '../lib/api';

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  hourly_rate: number;
  skills: string[];
}

function UserSkills({ skills }: { skills: string[] }) {
  const [expanded, setExpanded] = useState(false);
  const LIMIT = 5;

  if (!skills || skills.length === 0) {
    return (
      <span className="text-xs text-[rgb(var(--color-text-tertiary))] italic">
        No skills listed
      </span>
    );
  }

  if (skills.length <= LIMIT) {
    return (
      <div className="flex gap-1 flex-wrap max-w-xs">
        {skills.map((skill, idx) => (
          <span key={idx} className="badge badge-info text-xs px-2 py-0.5">
            {skill}
          </span>
        ))}
      </div>
    );
  }

  const displayedSkills = expanded ? skills : skills.slice(0, LIMIT);

  return (
    <div className="flex flex-col items-start gap-1 max-w-xs">
      <div className="flex gap-1 flex-wrap">
        {displayedSkills.map((skill, idx) => (
          <span key={idx} className="badge badge-info text-xs px-2 py-0.5">
            {skill}
          </span>
        ))}
      </div>
      <button 
        onClick={() => setExpanded(!expanded)}
        className="text-[10px] uppercase font-bold tracking-wider text-[rgb(var(--color-primary))] hover:text-[rgb(var(--color-primary-hover))] mt-1"
      >
        {expanded ? 'Show Less' : `+ ${skills.length - LIMIT} More`}
      </button>
    </div>
  );
}

export default function Users() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const response = await userAPI.list();
      // Filter to show only employees (not admins)
      const employees = response.data.filter((user: User) => user.role === 'employee');
      setUsers(employees);
    } catch (err) {
      setError('Failed to load users');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (userId: string) => {
    if (!confirm('Are you sure you want to delete this employee?')) return;
    
    try {
      await userAPI.delete(userId);
      setUsers(users.filter(u => u.id !== userId));
    } catch (err) {
      alert('Failed to delete employee');
      console.error(err);
    }
  };

  return (
    <AdminLayout>
      <div className="max-w-7xl mx-auto">
        {/* Page Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold tracking-tight mb-2">Employees</h1>
            <p className="text-[rgb(var(--color-text-secondary))]">
              Manage team members and their profiles
            </p>
          </div>
          <Link to="/users/new" className="btn btn-primary">
            <UserPlus className="w-4 h-4" />
            Add Employee
          </Link>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-[rgba(205,100,100,0.1)] border border-[rgba(205,100,100,0.3)] text-[rgb(var(--color-error))] rounded-sm">
            {error}
          </div>
        )}

        {/* Users Table */}
        <div className="card">
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Hourly Rate</th>
                  <th>Skills</th>
                  <th className="text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan={5} className="text-center py-8 text-[rgb(var(--color-text-secondary))]">
                      Loading employees...
                    </td>
                  </tr>
                ) : users.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="text-center py-8 text-[rgb(var(--color-text-secondary))]">
                      No employees found. Add your first employee to get started.
                    </td>
                  </tr>
                ) : (
                  users.map((user) => (
                    <tr key={user.id} className="hover:bg-[rgb(var(--color-surface-secondary))]">
                      <td>
                        <div className="font-medium">{user.name}</div>
                      </td>
                      <td>
                        <div className="flex items-center gap-2 text-sm text-[rgb(var(--color-text-secondary))]">
                          <Mail className="w-3 h-3" />
                          {user.email}
                        </div>
                      </td>
                      <td>
                        <span className="font-mono text-sm">
                          ${user.hourly_rate}/hr
                        </span>
                      </td>
                      <td>
                        <UserSkills skills={user.skills} />
                      </td>
                      <td>
                        <div className="flex gap-2 justify-end">
                          <Link 
                            to={`/users/${user.id}/analytics`}
                            className="btn btn-ghost btn-sm text-[rgb(var(--color-info))] hover:bg-[rgb(var(--color-info))]/10"
                            title="View Analytics"
                          >
                            <TrendingUp className="w-4 h-4" />
                          </Link>
                          <Link 
                            to={`/users/${user.id}/edit`}
                            className="btn btn-ghost btn-sm"
                          >
                            <Edit className="w-4 h-4" />
                          </Link>
                          <button
                            onClick={() => handleDelete(user.id)}
                            className="btn btn-ghost btn-sm text-[rgb(var(--color-error))] hover:bg-[rgb(var(--color-error))]/10"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </AdminLayout>
  );
}
