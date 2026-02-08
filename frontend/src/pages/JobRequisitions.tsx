import { useEffect, useState } from 'react';
import { MapPin, Upload, CheckCircle, AlertCircle, Loader2, Clock } from 'lucide-react';
import AdminLayout from '../components/AdminLayout';
import { jobAPI } from '../lib/api';

interface JobRequisition {
  id: string;
  suggested_title: string;
  description: string;
  required_skills: string[];
  status: string;
  created_at: string;
  location?: string;
}

export default function JobRequisitions() {
  const [pendingReqs, setPendingReqs] = useState<JobRequisition[]>([]);
  const [approvedReqs, setApprovedReqs] = useState<JobRequisition[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedReq, setSelectedReq] = useState<JobRequisition | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  // Modal state — simple text inputs
  const [posting, setPosting] = useState(false);
  const [titleInput, setTitleInput] = useState('');
  const [locationInput, setLocationInput] = useState('');

  useEffect(() => {
    loadRequisitions();
  }, []);

  const loadRequisitions = async () => {
    try {
      const [pendingRes, approvedRes] = await Promise.all([
        jobAPI.list({ status: 'pending' }),
        jobAPI.list({ status: 'approved,ready,posted' })
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
    setTitleInput(req.suggested_title);
    setLocationInput(req.location || '');
    setIsModalOpen(true);
  };

  const handleApprove = async () => {
    if (!selectedReq || !titleInput.trim() || !locationInput.trim()) return;
    
    setPosting(true);
    try {
      await jobAPI.approve(selectedReq.id, {
        title: titleInput.trim(),
        location: locationInput.trim(),
      });
      
      setIsModalOpen(false);
      loadRequisitions();
    } catch (err) {
      console.error('Failed to approve job:', err);
      alert('Failed to approve job. Please try again.');
    } finally {
      setPosting(false);
    }
  };

  const renderRequisitionCard = (req: JobRequisition, isPending: boolean) => (
    <div key={req.id} className="card hover:border-[rgb(var(--color-accent))] transition-colors">
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
            {req.location && (
              <div className="text-sm text-[rgb(var(--color-text-secondary))] mb-1">
                <MapPin className="w-3 h-3 inline mr-1" />
                {req.location}
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
              Review & Approve
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
            <div className="card w-full max-w-lg bg-[rgb(var(--color-surface))] shadow-xl">
              <div className="card-body p-6">
                <h2 className="text-2xl font-bold mb-2">Approve Job Requisition</h2>
                <p className="text-sm text-[rgb(var(--color-text-secondary))] mb-6">
                  Confirm or edit the title and location, then approve.
                </p>
                
                <div className="space-y-5">
                  <div>
                    <label className="label">Job Title</label>
                    <input 
                      type="text"
                      className="input w-full"
                      placeholder="e.g., Senior React Developer"
                      value={titleInput}
                      onChange={(e) => setTitleInput(e.target.value)}
                    />
                  </div>

                  <div>
                    <label className="label">Location</label>
                    <input 
                      type="text"
                      className="input w-full"
                      placeholder="e.g., Remote, San Francisco, CA"
                      value={locationInput}
                      onChange={(e) => setLocationInput(e.target.value)}
                    />
                  </div>

                  {/* Skills preview */}
                  <div>
                    <label className="label">Required Skills</label>
                    <div className="flex flex-wrap gap-2">
                      {selectedReq.required_skills?.map((skill, i) => (
                        <span key={i} className="badge badge-neutral text-xs">{skill}</span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="flex justify-end gap-3 mt-8">
                  <button 
                    className="btn btn-ghost" 
                    onClick={() => setIsModalOpen(false)}
                    disabled={posting}
                  >
                    Cancel
                  </button>
                  <button 
                    className="btn btn-primary gap-2"
                    onClick={handleApprove}
                    disabled={!titleInput.trim() || !locationInput.trim() || posting}
                  >
                    {posting ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <CheckCircle className="w-4 h-4" />
                    )}
                    Approve & Publish
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
