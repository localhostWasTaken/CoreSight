import { useEffect, useState } from 'react';
import { Briefcase, MapPin, Mail, Loader2, Building2, Clock } from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000';

interface Job {
    _id: string;
    title: string;
    description: string;
    required_skills: string[];
    location: string;
    workplace_type: string;
    employment_type: string;
}

// Format employment type for display
const formatEmploymentType = (type: string) => {
    const map: Record<string, string> = {
        'FULL_TIME': 'Full Time',
        'PART_TIME': 'Part Time',
        'CONTRACT': 'Contract',
        'INTERNSHIP': 'Internship',
    };
    return map[type] || type;
};

// Format workplace type for display
const formatWorkplaceType = (type: string) => {
    const map: Record<string, string> = {
        'ON_SITE': 'On-site',
        'REMOTE': 'Remote',
        'HYBRID': 'Hybrid',
    };
    return map[type] || type;
};

// Generate mailto link with template
const generateMailtoLink = (jobTitle: string) => {
    const email = 'career@coreinsights.ai';
    const subject = encodeURIComponent(`Application for ${jobTitle}`);
    const body = encodeURIComponent(
        `Hi,

I would like to apply for the ${jobTitle} position.

I feel I would be a good fit for this role because [please describe your relevant experience and why you're interested in this position].

I have attached my CV/Resume for your consideration.

Best regards,
[Your Name]`
    );

    return `mailto:${email}?subject=${subject}&body=${body}`;
};

export default function Careers() {
    const [jobs, setJobs] = useState<Job[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadJobs();
    }, []);

    const loadJobs = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/api/public/careers`);
            setJobs(response.data);
        } catch (err) {
            console.error('Failed to load jobs:', err);
            setError('Failed to load job listings. Please try again later.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex flex-col">
            {/* Header - matching AdminLayout style */}
            <header className="h-16 bg-[rgb(var(--color-surface))] border-b border-[rgb(var(--color-border))] flex items-center px-8">
                <div className="flex items-center gap-3">
                    <h1 className="text-xl font-bold tracking-tight mb-0">CoreSight</h1>
                    <span className="text-[rgb(var(--color-text-tertiary))]">|</span>
                    <span className="text-sm font-medium text-[rgb(var(--color-text-secondary))]">Careers</span>
                </div>
            </header>

            {/* Main content - matching AdminLayout style */}
            <main className="flex-1 p-8 bg-[rgb(var(--color-background))]">
                <div className="max-w-5xl mx-auto">
                    {/* Page header */}
                    <div className="mb-8">
                        <div className="flex items-center gap-3 mb-2">
                            <Briefcase className="w-7 h-7 text-[rgb(var(--color-accent))]" />
                            <h1 className="text-3xl font-bold tracking-tight mb-0">Join Our Team</h1>
                        </div>
                        <p className="text-[rgb(var(--color-text-secondary))]">
                            Be part of our mission to transform enterprise intelligence
                        </p>
                    </div>

                    {loading ? (
                        <div className="text-center py-16">
                            <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-[rgb(var(--color-accent))]" />
                            <p className="text-[rgb(var(--color-text-secondary))]">Loading open positions...</p>
                        </div>
                    ) : error ? (
                        <div className="card card-body text-center py-12">
                            <p className="text-[rgb(var(--color-error))]">{error}</p>
                        </div>
                    ) : jobs.length === 0 ? (
                        <div className="card card-body text-center py-12">
                            <Briefcase className="w-12 h-12 mx-auto mb-4 text-[rgb(var(--color-text-tertiary))]" />
                            <h2 className="text-xl font-semibold mb-2">No Open Positions</h2>
                            <p className="text-[rgb(var(--color-text-secondary))] mb-4">
                                We don't have any open positions at the moment, but check back soon!
                            </p>
                            <p className="text-sm text-[rgb(var(--color-text-tertiary))]">
                                You can also reach out to us at{' '}
                                <a href="mailto:career@coreinsights.ai">career@coreinsights.ai</a>
                            </p>
                        </div>
                    ) : (
                        <div className="space-y-6">
                            <div className="flex items-center justify-between">
                                <h2 className="text-xl font-semibold mb-0">Open Positions</h2>
                                <span className="badge badge-neutral">
                                    {jobs.length} {jobs.length === 1 ? 'opening' : 'openings'}
                                </span>
                            </div>

                            <div className="grid gap-4">
                                {jobs.map((job) => (
                                    <div
                                        key={job._id}
                                        className="card hover:border-[rgb(var(--color-accent))] transition-colors"
                                    >
                                        <div className="card-body">
                                            <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
                                                <div className="flex-1">
                                                    <h3 className="text-xl font-semibold mb-3">{job.title}</h3>

                                                    <div className="flex flex-wrap items-center gap-3 mb-4">
                                                        {job.location && (
                                                            <div className="flex items-center gap-1 text-sm text-[rgb(var(--color-text-secondary))]">
                                                                <MapPin className="w-4 h-4" />
                                                                {job.location}
                                                            </div>
                                                        )}
                                                        <div className="flex items-center gap-1 text-sm text-[rgb(var(--color-text-secondary))]">
                                                            <Building2 className="w-4 h-4" />
                                                            {formatWorkplaceType(job.workplace_type)}
                                                        </div>
                                                        <div className="flex items-center gap-1 text-sm text-[rgb(var(--color-text-secondary))]">
                                                            <Clock className="w-4 h-4" />
                                                            {formatEmploymentType(job.employment_type)}
                                                        </div>
                                                    </div>

                                                    {job.required_skills && job.required_skills.length > 0 && (
                                                        <div className="flex flex-wrap gap-2 mb-4">
                                                            {job.required_skills.map((skill, i) => (
                                                                <span key={i} className="badge badge-neutral text-xs">
                                                                    {skill}
                                                                </span>
                                                            ))}
                                                        </div>
                                                    )}

                                                    {job.description && (
                                                        <div
                                                            className="text-sm text-[rgb(var(--color-text-secondary))] line-clamp-3"
                                                            dangerouslySetInnerHTML={{ __html: job.description }}
                                                        />
                                                    )}
                                                </div>

                                                <div className="lg:ml-6 lg:flex-shrink-0">
                                                    <a
                                                        href={generateMailtoLink(job.title)}
                                                        className="btn btn-primary gap-2 w-full lg:w-auto no-underline"
                                                    >
                                                        <Mail className="w-4 h-4" />
                                                        Apply Now
                                                    </a>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>

                            {/* Application info card */}
                            <div className="card bg-[rgb(var(--color-surface-secondary))]">
                                <div className="card-body">
                                    <h3 className="text-lg font-semibold mb-2">How to Apply</h3>
                                    <p className="text-[rgb(var(--color-text-secondary))] mb-0">
                                        Click "Apply Now" on any position to send an email. Please attach your CV/Resume and tell us why you'd be a great fit.
                                    </p>
                                    <p className="text-sm text-[rgb(var(--color-text-tertiary))] mt-2 mb-0">
                                        All applications go to <strong>career@coreinsights.ai</strong>
                                    </p>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
}
