import { useEffect, useState } from 'react';
import { Briefcase, MapPin, Upload, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import AdminLayout from '../components/AdminLayout';
import { jobAPI, linkedinAPI } from '../lib/api';

interface JobRequisition {
  _id: string;
  suggested_title: string;
  description: string;
  required_skills: string[];
  status: string;
  created_at: string;
  linkedin_job_title_text?: string;
  linkedin_location_text?: string;
}

interface SearchResult {
  id: string;
  name: string;
}

export default function JobRequisitions() {
  const [requisitions, setRequisitions] = useState<JobRequisition[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedReq, setSelectedReq] = useState<JobRequisition | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  // Modal state
  const [posting, setPosting] = useState(false);
  const [titleQuery, setTitleQuery] = useState('');
  const [locationQuery, setLocationQuery] = useState('');
  const [titleResults, setTitleResults] = useState<SearchResult[]>([]);
  const [locationResults, setLocationResults] = useState<SearchResult[]>([]);
  const [selectedTitle, setSelectedTitle] = useState<SearchResult | null>(null);
  const [selectedLocation, setSelectedLocation] = useState<SearchResult | null>(null);

  useEffect(() => {
    loadRequisitions();
  }, []);

  const loadRequisitions = async () => {
    try {
      const response = await jobAPI.list({ status: 'pending' });
      setRequisitions(response.data);
    } catch (err) {
      console.error('Failed to load requisitions:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenModal = (req: JobRequisition) => {
    setSelectedReq(req);
    setTitleQuery(req.suggested_title);
    setLocationQuery('');
    setSelectedTitle(null);
    setSelectedLocation(null);
    setTitleResults([]);
    setLocationResults([]);
    setIsModalOpen(true);
  };

  const searchTitles = async (query: string) => {
    setTitleQuery(query);
    if (query.length < 3) return;
    try {
      const res = await linkedinAPI.searchJobTitles(query);
      setTitleResults(res.data.results);
    } catch (err) {
      console.error(err);
    }
  };

  const searchLocations = async (query: string) => {
    setLocationQuery(query);
    if (query.length < 3) return;
    try {
      const res = await linkedinAPI.searchLocations(query);
      setLocationResults(res.data.results);
    } catch (err) {
      console.error(err);
    }
  };

  const handlePost = async () => {
    if (!selectedReq || !selectedTitle || !selectedLocation) return;
    
    setPosting(true);
    try {
      await jobAPI.update(selectedReq._id, {
        linkedin_job_title_id: selectedTitle.id,
        linkedin_job_title_text: selectedTitle.name,
        linkedin_location_id: selectedLocation.id,
        linkedin_location_text: selectedLocation.name,
      });

      await jobAPI.post(selectedReq._id);
      
      setIsModalOpen(false);
      loadRequisitions();
      alert('Job posted successfully!');
    } catch (err) {
      console.error('Failed to post job:', err);
      alert('Failed to post job. Please try again.');
    } finally {
      setPosting(false);
    }
  };

  return (
    <AdminLayout>
      <div className="max-w-7xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight mb-2">Job Requisitions</h1>
          <p className="text-[rgb(var(--color-text-secondary))]">
            Review and upload pending job requisitions to LinkedIn
          </p>
        </div>

        {loading ? (
          <div>Loading...</div>
        ) : requisitions.length === 0 ? (
          <div className="card card-body text-center py-12">
            <Briefcase className="w-12 h-12 mx-auto mb-4 text-[rgb(var(--color-text-tertiary))]" />
            <p>No pending job requisitions found.</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {requisitions.map((req) => (
              <div key={req._id} className="card hover:border-[rgb(var(--color-accent))] transition-colors">
                <div className="card-body">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="text-xl font-semibold mb-2">{req.suggested_title}</h3>
                      <div className="flex flex-wrap gap-2 mb-3">
                        {req.required_skills?.map((skill, i) => (
                          <span key={i} className="badge badge-neutral text-xs">{skill}</span>
                        ))}
                      </div>
                      <div className="text-sm text-[rgb(var(--color-text-tertiary))] mb-2">
                        Created: {new Date(req.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <button 
                      onClick={() => handleOpenModal(req)}
                      className="btn btn-primary btn-sm gap-2"
                    >
                      <Upload className="w-4 h-4" />
                      Review & Upload
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {isModalOpen && selectedReq && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
            <div className="card w-full max-w-2xl bg-[rgb(var(--color-surface))] shadow-xl max-h-[90vh] overflow-y-auto">
              <div className="card-body p-6">
                <h2 className="text-2xl font-bold mb-6">Upload to LinkedIn</h2>
                
                <div className="space-y-6">
                  <div className="form-control">
                    <label className="label">
                      <span className="label-text font-medium">LinkedIn Job Title</span>
                    </label>
                    <div className="relative">
                      <input 
                        type="text"
                        className="input w-full"
                        placeholder="Search job titles..."
                        value={titleQuery}
                        onChange={(e) => searchTitles(e.target.value)}
                      />
                      {titleResults.length > 0 && !selectedTitle && (
                        <ul className="absolute z-10 w-full bg-[rgb(var(--color-surface))] border border-[rgb(var(--color-border))] rounded-md mt-1 max-h-48 overflow-y-auto shadow-lg">
                          {titleResults.map((res) => (
                            <li 
                              key={res.id}
                              className="p-2 hover:bg-[rgb(var(--color-background))] cursor-pointer"
                              onClick={() => {
                                setSelectedTitle(res);
                                setTitleQuery(res.name);
                                setTitleResults([]);
                              }}
                            >
                              {res.name}
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                    {selectedTitle && (
                      <div className="mt-1 text-sm text-[rgb(var(--color-success))] flex items-center gap-1">
                        <CheckCircle className="w-3 h-3" /> Selected: {selectedTitle.name}
                      </div>
                    )}
                  </div>

                  <div className="form-control">
                    <label className="label">
                      <span className="label-text font-medium">Location</span>
                    </label>
                    <div className="relative">
                      <input 
                        type="text"
                        className="input w-full"
                        placeholder="Search locations..."
                        value={locationQuery}
                        onChange={(e) => searchLocations(e.target.value)}
                      />
                      {locationResults.length > 0 && !selectedLocation && (
                        <ul className="absolute z-10 w-full bg-[rgb(var(--color-surface))] border border-[rgb(var(--color-border))] rounded-md mt-1 max-h-48 overflow-y-auto shadow-lg">
                          {locationResults.map((res) => (
                            <li 
                              key={res.id}
                              className="p-2 hover:bg-[rgb(var(--color-background))] cursor-pointer"
                              onClick={() => {
                                setSelectedLocation(res);
                                setLocationQuery(res.name);
                                setLocationResults([]);
                              }}
                            >
                              {res.name}
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                    {selectedLocation && (
                      <div className="mt-1 text-sm text-[rgb(var(--color-success))] flex items-center gap-1">
                        <CheckCircle className="w-3 h-3" /> Selected: {selectedLocation.name}
                      </div>
                    )}
                  </div>
                  
                  <div className="alert alert-info text-sm">
                    <AlertCircle className="w-4 h-4" />
                    <span>This will create a draft job posting on LinkedIn.</span>
                  </div>
                </div>

                <div className="card-actions justify-end mt-8">
                  <button 
                    className="btn btn-ghost" 
                    onClick={() => setIsModalOpen(false)}
                    disabled={posting}
                  >
                    Cancel
                  </button>
                  <button 
                    className="btn btn-primary"
                    onClick={handlePost}
                    disabled={!selectedTitle || !selectedLocation || posting}
                  >
                    {posting ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Upload & Post'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </AdminLayout>
  );
}
