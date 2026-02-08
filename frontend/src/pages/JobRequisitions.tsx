import { useEffect, useState, useCallback } from 'react';
import { Briefcase, MapPin, Upload, CheckCircle, AlertCircle, Loader2, Clock } from 'lucide-react';
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
  linkedin_job_id?: string;
}

interface SearchResult {
  id: string;
  name: string;
}

// Debounce hook
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

export default function JobRequisitions() {
  const [pendingReqs, setPendingReqs] = useState<JobRequisition[]>([]);
  const [approvedReqs, setApprovedReqs] = useState<JobRequisition[]>([]);
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
  const [searchingTitles, setSearchingTitles] = useState(false);
  const [searchingLocations, setSearchingLocations] = useState(false);

  // Debounced search queries
  const debouncedTitleQuery = useDebounce(titleQuery, 1500);
  const debouncedLocationQuery = useDebounce(locationQuery,1500);

  useEffect(() => {
    loadRequisitions();
  }, []);

  // Auto-search when debounced query changes
  useEffect(() => {
    if (debouncedTitleQuery && debouncedTitleQuery.length >= 3 && !selectedTitle) {
      searchTitles(debouncedTitleQuery);
    } else if (debouncedTitleQuery.length < 3) {
      setTitleResults([]);
    }
  }, [debouncedTitleQuery]);

  useEffect(() => {
    if (debouncedLocationQuery && debouncedLocationQuery.length >= 3 && !selectedLocation) {
      searchLocations(debouncedLocationQuery);
    } else if (debouncedLocationQuery.length < 3) {
      setLocationResults([]);
    }
  }, [debouncedLocationQuery]);

  const loadRequisitions = async () => {
    try {
      const [pendingRes, approvedRes] = await Promise.all([
        jobAPI.list({ status: 'pending' }),
        jobAPI.list({ status: 'ready,posted' })
      ]);
      setPendingReqs(pendingRes.data);
      setApprovedReqs(approvedRes.data);
    } catch (err) {
      console.error('Failed to load requisitions:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenModal = (req: JobRequisition) => {
    setSelectedReq(req);
    // Use empty string, not suggested title - that becomes placeholder
    setTitleQuery('');
    setLocationQuery('');
    setSelectedTitle(null);
    setSelectedLocation(null);
    setTitleResults([]);
    setLocationResults([]);
    setIsModalOpen(true);
  };

  const searchTitles = async (query: string) => {
    setSearchingTitles(true);
    try {
      const res = await linkedinAPI.searchJobTitles(query);
      setTitleResults(res.data.results);
    } catch (err) {
      console.error(err);
    } finally {
      setSearchingTitles(false);
    }
  };

  const searchLocations = async (query: string) => {
    setSearchingLocations(true);
    try {
      const res = await linkedinAPI.searchLocations(query);
      setLocationResults(res.data.results);
    } catch (err) {
      console.error(err);
    } finally {
      setSearchingLocations(false);
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

  const renderRequisitionCard = (req: JobRequisition, isPending: boolean) => (
    <div key={req._id} className="card hover:border-[rgb(var(--color-accent))] transition-colors">
      <div className="card-body">
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <h3 className="text-xl font-semibold">{req.suggested_title}</h3>
              {!isPending && (
                <span className="badge badge-success text-xs">
                  <CheckCircle className="w-3 h-3 mr-1" />
                  Approved
                </span>
              )}
            </div>
            <div className="flex flex-wrap gap-2 mb-3">
              {req.required_skills?.map((skill, i) => (
                <span key={i} className="badge badge-neutral text-xs">{skill}</span>
              ))}
            </div>
            {req.linkedin_job_title_text && (
              <div className="text-sm text-[rgb(var(--color-text-secondary))] mb-1">
                <Briefcase className="w-3 h-3 inline mr-1" />
                {req.linkedin_job_title_text}
              </div>
            )}
            {req.linkedin_location_text && (
              <div className="text-sm text-[rgb(var(--color-text-secondary))] mb-1">
                <MapPin className="w-3 h-3 inline mr-1" />
                {req.linkedin_location_text}
              </div>
            )}
            <div className="text-sm text-[rgb(var(--color-text-tertiary))] mt-2">
              <Clock className="w-3 h-3 inline mr-1" />
              Created: {new Date(req.created_at).toLocaleDateString()}
            </div>
          </div>
          {isPending && (
            <button 
              onClick={() => handleOpenModal(req)}
              className="btn btn-primary btn-sm gap-2"
            >
              <Upload className="w-4 h-4" />
              Review & Upload
            </button>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <AdminLayout>
      <div className="max-w-7xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight mb-2">Job Requisitions</h1>
          <p className="text-[rgb(var(--color-text-secondary))]">
            Review and manage job requisitions created by the AI system
          </p>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2" />
            <p className="text-[rgb(var(--color-text-secondary))]">Loading requisitions...</p>
          </div>
        ) : (
          <div className="space-y-8">
            {/* Pending Section */}
            <div>
              <div className="flex items-center gap-2 mb-4">
                <AlertCircle className="w-5 h-5 text-[rgb(var(--color-warning))]" />
                <h2 className="text-2xl font-bold">Pending Approval</h2>
                <span className="badge badge-warning">{pendingReqs.length}</span>
              </div>
              
              {pendingReqs.length === 0 ? (
                <div className="card card-body text-center py-8">
                  <p className="text-[rgb(var(--color-text-secondary))]">No pending requisitions</p>
                </div>
              ) : (
                <div className="grid gap-4">
                  {pendingReqs.map((req) => renderRequisitionCard(req, true))}
                </div>
              )}
            </div>

            {/* Approved Section */}
            <div>
              <div className="flex items-center gap-2 mb-4">
                <CheckCircle className="w-5 h-5 text-[rgb(var(--color-success))]" />
                <h2 className="text-2xl font-bold">Approved & Posted</h2>
                <span className="badge badge-success">{approvedReqs.length}</span>
              </div>
              
              {approvedReqs.length === 0 ? (
                <div className="card card-body text-center py-8">
                  <p className="text-[rgb(var(--color-text-secondary))]">No approved requisitions yet</p>
                </div>
              ) : (
                <div className="grid gap-4">
                  {approvedReqs.map((req) => renderRequisitionCard(req, false))}
                </div>
              )}
            </div>
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
                        placeholder={selectedReq.suggested_title}
                        value={titleQuery}
                        onChange={(e) => {
                          setTitleQuery(e.target.value);
                          setSelectedTitle(null);
                        }}
                      />
                      {searchingTitles && (
                        <div className="absolute right-3 top-1/2 -translate-y-1/2">
                          <Loader2 className="w-4 h-4 animate-spin text-[rgb(var(--color-text-tertiary))]" />
                        </div>
                      )}
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
                    {!selectedTitle && titleQuery.length > 0 && titleQuery.length < 3 && (
                      <div className="mt-1 text-xs text-[rgb(var(--color-text-tertiary))]">
                        Type at least 3 characters to search...
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
                        placeholder="e.g., San Francisco, CA"
                        value={locationQuery}
                        onChange={(e) => {
                          setLocationQuery(e.target.value);
                          setSelectedLocation(null);
                        }}
                      />
                      {searchingLocations && (
                        <div className="absolute right-3 top-1/2 -translate-y-1/2">
                          <Loader2 className="w-4 h-4 animate-spin text-[rgb(var(--color-text-tertiary))]" />
                        </div>
                      )}
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
                    {!selectedLocation && locationQuery.length > 0 && locationQuery.length < 3 && (
                      <div className="mt-1 text-xs text-[rgb(var(--color-text-tertiary))]">
                        Type at least 3 characters to search...
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
