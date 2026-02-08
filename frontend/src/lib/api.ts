import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// API endpoints
export const userAPI = {
  list: () => api.get('/api/users'),
  get: (id: string) => api.get(`/api/users/${id}`),
  create: (data: any) => api.post('/api/users', data),
  update: (id: string, data: any) => api.put(`/api/users/${id}`, data),
  delete: (id: string) => api.delete(`/api/users/${id}`),
};

export const taskAPI = {
  list: (params?: any) => api.get('/api/tasks', { params }),
  get: (id: string) => api.get(`/api/tasks/${id}`),
  assign: (taskId: string, userId: string) => 
    api.post(`/api/tasks/${taskId}/assign/${userId}`),
};

export const projectAPI = {
  list: () => api.get('/api/projects'),
  get: (id: string) => api.get(`/api/projects/${id}`),
  create: (data: any) => api.post('/api/projects', data),
  update: (id: string, data: any) => api.put(`/api/projects/${id}`, data),
  delete: (id: string) => api.delete(`/api/projects/${id}`),
};

export const analyticsAPI = {
  userImpact: (userId: string) => 
    api.get(`/api/analytics/user/${userId}/impact_breakdown`),
  taskCost: (taskId: string) => 
    api.get(`/api/analytics/task/${taskId}/cost_breakdown`),
  focusHealth: (params?: any) => 
    api.get('/api/analytics/team/focus_health', { params }),
  topContributors: (params?: any) => 
    api.get('/api/analytics/team/top_contributors', { params }),
};

export const commitAPI = {
  list: (params?: any) => api.get('/api/commits', { params }),
  byUser: (userId: string) => api.get(`/api/commits/user/${userId}`),
};

export const issueAPI = {
  list: (params?: any) => api.get('/api/issues', { params }),
  get: (id: string) => api.get(`/api/issues/${id}`),
};

export const jobAPI = {
  list: (params?: any) => api.get('/api/jobs/requisitions', { params }),
  get: (id: string) => api.get(`/api/jobs/requisitions/${id}`),
  update: (id: string, data: any) => api.patch(`/api/jobs/requisitions/${id}`, data),
  post: (id: string) => api.post(`/api/jobs/requisitions/${id}/post`),
  approve: (id: string) => api.post(`/api/jobs/requisitions/${id}/approve`),
  delete: (id: string) => api.delete(`/api/jobs/requisitions/${id}`),
};

export const linkedinAPI = {
  searchLocations: (query: string) => api.get('/api/linkedin/search/locations', { params: { query } }),
  searchJobTitles: (query: string) => api.get('/api/linkedin/search/job-titles', { params: { query } }),
};
