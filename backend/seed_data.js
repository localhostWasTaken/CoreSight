// CoreSight Mock Data Seed Script
// Run with: mongosh "your-connection-string" < seed_data.js

// Switch to your database
use('coresight');

// NOTE: Delete commands commented out to preserve existing data
// Uncomment these lines ONLY if you want to start fresh
// db.users.deleteMany({});
// db.projects.deleteMany({});
// db.tasks.deleteMany({});
// db.commits.deleteMany({});
// db.sprints.deleteMany({});
// db.job_requisitions.deleteMany({});

print("Creating mock users...");

// Create Users
const users = [
  {
    _id: ObjectId(),
    name: "Alice Johnson",
    email: "alice@coresight.com",
    role: "employee",
    hourly_rate: 75.0,
    skills: ["Python", "FastAPI", "MongoDB", "React", "Machine Learning"],
    work_profile_embeddings: Array(1536).fill(0).map(() => Math.random()),
    github_username: "alice-dev",
    jira_account_id: "alice123",
    project_metrics: {}
  },
  {
    _id: ObjectId(),
    name: "Bob Smith",
    email: "bob@coresight.com",
    role: "employee",
    hourly_rate: 80.0,
    skills: ["JavaScript", "TypeScript", "React", "Node.js", "AWS"],
    work_profile_embeddings: Array(1536).fill(0).map(() => Math.random()),
    github_username: "bob-codes",
    jira_account_id: "bob456",
    project_metrics: {}
  },
  {
    _id: ObjectId(),
    name: "Carol Martinez",
    email: "carol@coresight.com",
    role: "employee",
    hourly_rate: 85.0,
    skills: ["DevOps", "Docker", "Kubernetes", "CI/CD", "Python"],
    work_profile_embeddings: Array(1536).fill(0).map(() => Math.random()),
    github_username: "carol-devops",
    jira_account_id: "carol789",
    project_metrics: {}
  },
  {
    _id: ObjectId(),
    name: "David Chen",
    email: "david@coresight.com",
    role: "employee",
    hourly_rate: 70.0,
    skills: ["Java", "Spring Boot", "PostgreSQL", "Microservices"],
    work_profile_embeddings: Array(1536).fill(0).map(() => Math.random()),
    github_username: "david-java",
    jira_account_id: "david101",
    project_metrics: {}
  },
  {
    _id: ObjectId(),
    name: "Emma Wilson",
    email: "emma@coresight.com",
    role: "employee",
    hourly_rate: 90.0,
    skills: ["UI/UX Design", "Figma", "React", "CSS", "Accessibility"],
    work_profile_embeddings: Array(1536).fill(0).map(() => Math.random()),
    github_username: "emma-design",
    jira_account_id: "emma202",
    project_metrics: {}
  }
];

db.users.insertMany(users);
print(`Created ${users.length} users`);

// Create Projects
print("Creating mock projects...");

const projects = [
  {
    _id: ObjectId(),
    name: "CoreSight-Platform",
    repo_url: "https://github.com/company/coresight-platform",
    jira_space_id: "CS",
    total_budget: 50000.0,
    contributors: [users[0]._id, users[1]._id, users[2]._id],
    created_at: new Date("2025-12-01"),
    updated_at: new Date()
  },
  {
    _id: ObjectId(),
    name: "Analytics-Dashboard",
    repo_url: "https://github.com/company/analytics-dashboard",
    jira_space_id: "AD",
    total_budget: 30000.0,
    contributors: [users[1]._id, users[4]._id],
    created_at: new Date("2026-01-15"),
    updated_at: new Date()
  },
  {
    _id: ObjectId(),
    name: "Mobile-App",
    repo_url: "https://github.com/company/mobile-app",
    jira_space_id: "MA",
    total_budget: 40000.0,
    contributors: [users[3]._id],
    created_at: new Date("2026-01-20"),
    updated_at: new Date()
  }
];

db.projects.insertMany(projects);
print(`Created ${projects.length} projects`);

// Create Sprints
print("Creating mock sprints...");

const sprints = [
  {
    _id: ObjectId(),
    project_id: projects[0]._id,
    name: "Sprint 1 - Foundation",
    start_date: new Date("2026-01-01"),
    end_date: new Date("2026-01-14"),
    goal: "Set up core infrastructure and authentication",
    is_active: false
  },
  {
    _id: ObjectId(),
    project_id: projects[0]._id,
    name: "Sprint 2 - Features",
    start_date: new Date("2026-01-15"),
    end_date: new Date("2026-01-28"),
    goal: "Implement task management and user profiles",
    is_active: false
  },
  {
    _id: ObjectId(),
    project_id: projects[0]._id,
    name: "Sprint 3 - AI Integration",
    start_date: new Date("2026-01-29"),
    end_date: new Date("2026-02-11"),
    goal: "Add AI-powered skill matching and job requisitions",
    is_active: true
  },
  {
    _id: ObjectId(),
    project_id: projects[1]._id,
    name: "Dashboard Sprint 1",
    start_date: new Date("2026-02-01"),
    end_date: new Date("2026-02-14"),
    goal: "Build analytics visualization components",
    is_active: true
  }
];

db.sprints.insertMany(sprints);
print(`Created ${sprints.length} sprints`);

// Create Tasks
print("Creating mock tasks...");

const tasks = [
  {
    _id: ObjectId(),
    external_id: "CS-101",
    title: "Implement user authentication system",
    description: "Build JWT-based authentication with role-based access control",
    description_embeddings: Array(1536).fill(0).map(() => Math.random()),
    type: "feature",
    status: "done",
    priority: "high",
    project_id: projects[0]._id,
    sprint_id: sprints[0]._id,
    current_assignee_ids: [users[0]._id],
    sprint_history: [sprints[0]._id],
    rollover_count: 0,
    total_time_spent_minutes: 480,
    total_cost: 600.0,
    created_at: new Date("2026-01-02"),
    updated_at: new Date("2026-01-10")
  },
  {
    _id: ObjectId(),
    external_id: "CS-102",
    title: "Design task management UI",
    description: "Create intuitive interface for viewing and managing tasks",
    description_embeddings: Array(1536).fill(0).map(() => Math.random()),
    type: "feature",
    status: "done",
    priority: "high",
    project_id: projects[0]._id,
    sprint_id: sprints[1]._id,
    current_assignee_ids: [users[4]._id],
    sprint_history: [sprints[1]._id],
    rollover_count: 0,
    total_time_spent_minutes: 360,
    total_cost: 540.0,
    created_at: new Date("2026-01-16"),
    updated_at: new Date("2026-01-25")
  },
  {
    _id: ObjectId(),
    external_id: "CS-103",
    title: "Implement AI skill matching algorithm",
    description: "Build LLM-powered system to match tasks with best-fit employees",
    description_embeddings: Array(1536).fill(0).map(() => Math.random()),
    type: "feature",
    status: "in_progress",
    priority: "high",
    project_id: projects[0]._id,
    sprint_id: sprints[2]._id,
    current_assignee_ids: [users[0]._id, users[1]._id],
    sprint_history: [sprints[2]._id],
    rollover_count: 0,
    total_time_spent_minutes: 240,
    total_cost: 372.0,
    created_at: new Date("2026-01-30"),
    updated_at: new Date()
  },
  {
    _id: ObjectId(),
    external_id: "CS-104",
    title: "Fix database connection pooling",
    description: "Optimize MongoDB connection handling to prevent timeouts",
    description_embeddings: Array(1536).fill(0).map(() => Math.random()),
    type: "bug",
    status: "todo",
    priority: "medium",
    project_id: projects[0]._id,
    sprint_id: sprints[2]._id,
    current_assignee_ids: [users[2]._id],
    sprint_history: [sprints[2]._id],
    rollover_count: 0,
    total_time_spent_minutes: 0,
    total_cost: 0.0,
    created_at: new Date("2026-02-05"),
    updated_at: new Date()
  },
  {
    _id: ObjectId(),
    external_id: "AD-201",
    title: "Create revenue analytics chart",
    description: "Build interactive chart showing revenue trends over time",
    description_embeddings: Array(1536).fill(0).map(() => Math.random()),
    type: "feature",
    status: "in_progress",
    priority: "high",
    project_id: projects[1]._id,
    sprint_id: sprints[3]._id,
    current_assignee_ids: [users[1]._id],
    sprint_history: [sprints[3]._id],
    rollover_count: 0,
    total_time_spent_minutes: 180,
    total_cost: 240.0,
    created_at: new Date("2026-02-02"),
    updated_at: new Date()
  },
  {
    _id: ObjectId(),
    external_id: "MA-301",
    title: "Implement push notifications",
    description: "Add Firebase Cloud Messaging for mobile push notifications",
    description_embeddings: Array(1536).fill(0).map(() => Math.random()),
    type: "feature",
    status: "todo",
    priority: "medium",
    project_id: projects[2]._id,
    sprint_id: null,
    current_assignee_ids: [],
    sprint_history: [],
    rollover_count: 0,
    total_time_spent_minutes: 0,
    total_cost: 0.0,
    created_at: new Date("2026-02-06"),
    updated_at: new Date()
  }
];

db.tasks.insertMany(tasks);
print(`Created ${tasks.length} tasks`);

// Create Commits
print("Creating mock commits...");

const commits = [
  {
    _id: ObjectId(),
    commit_hash: "a1b2c3d4e5f6",
    commit_message: "Add JWT authentication middleware",
    diff_content: "+++ auth.py\n+def verify_token(token):\n+    return jwt.decode(token)",
    summary: "Implemented JWT token verification for secure authentication",
    extracted_skills: ["Python", "JWT", "Security"],
    summary_embedding: Array(1536).fill(0).map(() => Math.random()),
    linked_task_id: tasks[0]._id,
    is_jira_tracked: true,
    author_email: "alice@coresight.com",
    author_name: "Alice Johnson",
    user_id: users[0]._id,
    repository: "CoreSight-Platform",
    branch: "main",
    project_id: projects[0]._id,
    timestamp: new Date("2026-01-05T10:30:00"),
    files_changed: 2,
    lines_added: 45,
    lines_deleted: 3,
    triggered_profile_update: false,
    created_at: new Date("2026-01-05T10:30:00")
  },
  {
    _id: ObjectId(),
    commit_hash: "b2c3d4e5f6a1",
    commit_message: "Design task card component",
    diff_content: "+++ TaskCard.tsx\n+export const TaskCard = ({ task }) => {\n+  return <div>...</div>\n+}",
    summary: "Created reusable task card component with status badges",
    extracted_skills: ["React", "TypeScript", "UI Design"],
    summary_embedding: Array(1536).fill(0).map(() => Math.random()),
    linked_task_id: tasks[1]._id,
    is_jira_tracked: true,
    author_email: "emma@coresight.com",
    author_name: "Emma Wilson",
    user_id: users[4]._id,
    repository: "CoreSight-Platform",
    branch: "feature/task-ui",
    project_id: projects[0]._id,
    timestamp: new Date("2026-01-20T14:15:00"),
    files_changed: 3,
    lines_added: 87,
    lines_deleted: 12,
    triggered_profile_update: false,
    created_at: new Date("2026-01-20T14:15:00")
  },
  {
    _id: ObjectId(),
    commit_hash: "c3d4e5f6a1b2",
    commit_message: "Implement skill embedding generation",
    diff_content: "+++ embeddings.py\n+def generate_skill_embedding(skills):\n+    return model.encode(skills)",
    summary: "Added AI model for generating skill embeddings",
    extracted_skills: ["Python", "Machine Learning", "AI"],
    summary_embedding: Array(1536).fill(0).map(() => Math.random()),
    linked_task_id: tasks[2]._id,
    is_jira_tracked: true,
    author_email: "alice@coresight.com",
    author_name: "Alice Johnson",
    user_id: users[0]._id,
    repository: "CoreSight-Platform",
    branch: "feature/ai-matching",
    project_id: projects[0]._id,
    timestamp: new Date("2026-02-01T09:45:00"),
    files_changed: 1,
    lines_added: 34,
    lines_deleted: 0,
    triggered_profile_update: true,
    created_at: new Date("2026-02-01T09:45:00")
  },
  {
    _id: ObjectId(),
    commit_hash: "d4e5f6a1b2c3",
    commit_message: "Add chart.js integration",
    diff_content: "+++ RevenueChart.tsx\n+import { Line } from 'react-chartjs-2'",
    summary: "Integrated Chart.js for revenue visualization",
    extracted_skills: ["React", "Chart.js", "Data Visualization"],
    summary_embedding: Array(1536).fill(0).map(() => Math.random()),
    linked_task_id: tasks[4]._id,
    is_jira_tracked: true,
    author_email: "bob@coresight.com",
    author_name: "Bob Smith",
    user_id: users[1]._id,
    repository: "Analytics-Dashboard",
    branch: "main",
    project_id: projects[1]._id,
    timestamp: new Date("2026-02-04T16:20:00"),
    files_changed: 2,
    lines_added: 56,
    lines_deleted: 8,
    triggered_profile_update: false,
    created_at: new Date("2026-02-04T16:20:00")
  }
];

db.commits.insertMany(commits);
print(`Created ${commits.length} commits`);

// Create Job Requisitions
print("Creating mock job requisitions...");

const jobRequisitions = [
  {
    _id: ObjectId(),
    task_id: tasks[5]._id,
    suggested_title: "Senior Mobile Developer",
    description: "<p>We're looking for an experienced mobile developer to implement push notifications using Firebase Cloud Messaging.</p><p><strong>Requirements:</strong></p><ul><li>5+ years mobile development experience</li><li>Expert in React Native or Flutter</li><li>Firebase integration experience</li></ul>",
    required_skills: ["React Native", "Firebase", "Mobile Development", "Push Notifications"],
    linkedin_job_title_id: "12345",
    linkedin_job_title_text: "Mobile Developer",
    linkedin_location_id: "67890",
    linkedin_location_text: "San Francisco, CA",
    workplace_type: "HYBRID",
    employment_type: "FULL_TIME",
    status: "ready",
    admin_approved: true,
    linkedin_job_id: null,
    created_at: new Date("2026-02-07"),
    updated_at: new Date(),
    created_by: "system"
  },
  {
    _id: ObjectId(),
    task_id: null,
    suggested_title: "DevOps Engineer",
    description: "<p>Seeking a DevOps engineer to help scale our infrastructure.</p><p><strong>Requirements:</strong></p><ul><li>Kubernetes expertise</li><li>CI/CD pipeline experience</li><li>Cloud platform knowledge (AWS/GCP)</li></ul>",
    required_skills: ["Kubernetes", "Docker", "AWS", "CI/CD", "Terraform"],
    linkedin_job_title_id: null,
    linkedin_job_title_text: null,
    linkedin_location_id: null,
    linkedin_location_text: null,
    workplace_type: "REMOTE",
    employment_type: "FULL_TIME",
    status: "pending",
    admin_approved: false,
    linkedin_job_id: null,
    created_at: new Date("2026-02-08"),
    updated_at: new Date(),
    created_by: "system"
  }
];

db.job_requisitions.insertMany(jobRequisitions);
print(`Created ${jobRequisitions.length} job requisitions`);

print("\n=== Mock Data Summary ===");
print(`Users: ${users.length}`);
print(`Projects: ${projects.length}`);
print(`Sprints: ${sprints.length}`);
print(`Tasks: ${tasks.length}`);
print(`Commits: ${commits.length}`);
print(`Job Requisitions: ${jobRequisitions.length}`);
print("\nMock data seeded successfully!");
