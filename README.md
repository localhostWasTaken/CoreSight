# CoreSight

**AI-Driven Enterprise Delivery & Workforce Intelligence System**

> Hackathon Project: DataZen - Somaiya Vidyavihar University

CoreSight transforms raw engineering activity into **actionable business intelligence**. It leverages AI to analyze commits, match developers to tasks, detect burnout risks, and provide comprehensive workforce analytics.

---

## Features

### AI-Powered Intelligence
- **Smart Task Matching** - Automatically matches developers to tasks based on skills and work history using vector embeddings
- **Skill Extraction** - Extracts skills from commit diffs and task descriptions using LLM analysis
- **Duplicate Detection** - AI-powered issue duplicate checking
- **Profile Evolution** - Tracks and updates developer skills based on their actual work
- **Job Requisition Generation** - Automatically generates job postings when no matching internal candidates are found

### Analytics & Insights
- **Maker vs. Mender Score** - Categorizes developer work (new features vs. refactoring vs. cleanup)
- **True Task Costing** - Calculates actual task costs by aggregating work sessions
- **Burnout Detection** - Analyzes context switching patterns to detect burnout risk
- **Project Budget Tracking** - Tracks time and cost against project budgets

### Integrations
- **GitHub Webhooks** - Real-time commit and PR tracking
- **Jira Integration** - Task synchronization and status tracking

---

## Architecture

```
CoreSight/
├── backend/                    # FastAPI Backend (Python)
│   ├── main.py                 # Application entry point
│   ├── routes/                 # API endpoints (10 routers)
│   ├── services/               # Business logic layer
│   ├── ai/                     # AI/ML utilities
│   ├── entities/               # Pydantic models
│   ├── scripts/                # DB init & seed scripts
│   └── utils/                  # Database & auth utilities
└── frontend/                   # React Frontend (TypeScript)
    └── src/
        ├── pages/              # Application pages
        ├── components/         # Layout & route guards
        ├── contexts/           # Auth context
        └── lib/                # API client & utilities
```

---

## Backend

### Tech Stack
- **Framework**: FastAPI
- **Database**: MongoDB (Motor async driver)
- **AI/ML**: Google Generative AI (Gemini), OpenAI
- **Auth**: JWT (python-jose)

### API Routes

| Route | Description |
|-------|-------------|
| `/auth` | Authentication (login, logout) |
| `/users` | User management & profiles |
| `/tasks` | Task CRUD & assignment |
| `/projects` | Project management |
| `/jobs` | Job requisition management |
| `/webhooks` | GitHub/Jira webhook handlers |
| `/issues` | Issue tracking with duplicate detection |
| `/commits` | Commit analysis & skill extraction |
| `/analytics` | Analytics & reporting endpoints |
| `/careers` | Public careers page API |

### AI Modules

| Module | Purpose |
|--------|---------|
| `embeddings.py` | Generate text embeddings & calculate similarity |
| `matching.py` | Find best matching users for tasks |
| `skills.py` | Extract skills from tasks & code |
| `validation.py` | LLM-based candidate evaluation |
| `reports.py` | Generate no-match reports & job descriptions |
| `analysis.py` | Commit analysis & duplicate detection |

### Data Models

- **User** - Developer profiles with skills, embeddings, and hourly rate
- **Project** - Projects with budget tracking
- **Task** - Work items with multi-user assignment
- **Sprint** - Sprint tracking with goals and dates
- **Issue** - Issues with duplicate detection
- **Commit** - Git commits with skill extraction
- **JobRequisition** - AI-generated job postings

---

## Frontend

### Tech Stack
- **Framework**: React 19
- **Build Tool**: Vite 7
- **Language**: TypeScript
- **Styling**: TailwindCSS 4
- **Charts**: Recharts
- **Routing**: React Router 7

### Pages

| Page | Route | Description |
|------|-------|-------------|
| Dashboard | `/dashboard` | Overview with key metrics |
| Users | `/users` | User management list |
| User Form | `/users/new`, `/users/:id` | Create/edit users |
| User Analytics | `/users/:userId/analytics` | Individual user analytics |
| Tasks | `/tasks` | Task management |
| Projects | `/projects` | Project management |
| Analytics | `/analytics` | Team-wide analytics |
| Activity | `/activity` | Activity feed |
| Job Requisitions | `/jobs` | Manage job postings |
| Careers | `/careers` | Public job listings (no auth) |
| Login | `/login` | Authentication |

---

## 🛠️ Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys and MongoDB URL

# Run server
python main.py
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

> **Note:** The frontend uses a Vite dev-server proxy (`/api` → `http://localhost:8000`) so no `VITE_API_URL` configuration is needed during local development.

---

## Environment Variables

### Backend (.env)

| Variable | Description |
|----------|-------------|
| `MONGODB_URL` | MongoDB connection string |
| `MONGODB_DB_NAME` | Database name (default: `coresight`) |
| `GOOGLE_API_KEY` | Google Generative AI API key |
| `OPENAI_API_KEY` | OpenAI API key (optional) |
| `JWT_SECRET_KEY` | Secret for JWT token signing |
| `API_PORT` | API server port (default: `8000`) |

### Frontend (.env)

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend API URL (leave empty for local dev — Vite proxy handles it) |

---

## API Documentation

Once running, access the interactive API docs:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## Authentication

CoreSight uses JWT-based authentication with two user roles:

| Role | Authentication | Description |
|------|----------------|-------------|
| **Admin** | Local password | Full access, requires password |
| **Employee** | External SSO (future) | Limited access, no local password |

---

## Key Analytics Features

### Maker vs. Mender Score
Analyzes commit patterns to categorize work:
- **New Feature** - Mostly additions (building new capabilities)
- **Refactoring** - Mostly modifications (improving existing code)
- **Cleanup** - Mostly deletions (removing technical debt)

### Burnout Detection
Monitors context switching to identify at-risk developers:
- Tracks daily task switches
- Flags users with >4 switches/day as "High Risk"

### True Task Costing
Calculates actual costs by:
- Aggregating all work sessions
- Multiplying by user hourly rates
- Comparing against project budgets

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project was created for the DataZen Hackathon at Somaiya Vidyavihar University.

---

## 👥 Team

CoreSight Intelligence Engine — Version 1.1.0
