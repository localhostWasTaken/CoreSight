# CoreSight Jira Integration Documentation

## Overview

CoreSight's Jira integration provides **AI-powered intelligent task assignment** using embeddings and LLM validation. The system automatically:

1. **Extracts required skills** from task descriptions using DeepSeek LLM
2. **Generates embeddings** for tasks and user skills using Yuan Embedding model
3. **Matches tasks to developers** based on skill similarity (cosine similarity)
4. **Validates assignments** using LLM to ensure developer capability
5. **Auto-assigns tasks** in the current sprint
6. **Generates critical reports** when no suitable developers are found

---

## Architecture

```
Jira Webhook → FastAPI → AI Processing → MongoDB
                  ↓
         ┌────────┴─────────┐
         ↓                  ↓
   Skill Extraction    Embedding Generation
   (DeepSeek LLM)      (Yuan Embedding)
         ↓                  ↓
         └────────┬─────────┘
                  ↓
         User Matching (Cosine Similarity)
                  ↓
         LLM Validation (DeepSeek)
                  ↓
         Assignment Decision
                  ↓
         Update MongoDB
```

---

## Setup

### 1. Environment Configuration

Create `.env` file:

```bash
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=coresight

# Featherless AI API
FEATHERLESS_API_KEY=rc_6592c9b70f6b793d73a2cb301a915a586d586fdad0e75d61e35e50ae22be29b7
FEATHERLESS_BASE_URL=https://api.featherless.ai/v1

# Models
EMBEDDING_MODEL=IEITYuan/Yuan-embedding-2.0-en
LLM_MODEL=deepseek-ai/DeepSeek-R1-0528

# API
API_PORT=8080
```

### 2. Install Dependencies

```bash
pip install fastapi uvicorn motor pymongo python-dotenv openai numpy pydantic
```

### 3. Start MongoDB

```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or use existing MongoDB instance
```

### 4. Run the API

```bash
python main.py
```

The API will be available at `http://localhost:8080`

---

## API Endpoints

### Health & Info

- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation (Swagger UI)

### Webhook

- `POST /api/webhook/jira` - Jira webhook endpoint

### User Management

#### Create User
```bash
POST /api/users
Content-Type: application/json

{
  "name": "Alice Johnson",
  "email": "alice@company.com",
  "role": "employee",
  "hourly_rate": 75.0,
  "skills": ["Python", "FastAPI", "MongoDB", "React", "Docker"],
  "github_username": "alicejohnson",
  "jira_account_id": "712020:xxxxx"
}
```

#### List Users
```bash
GET /api/users
```

### Task Management

#### List Tasks
```bash
GET /api/tasks
```

#### Get Task Recommendations
```bash
GET /api/tasks/{task_id}/recommendations
```

Returns best matching users for a task with match scores.

### Project & Sprint Management

```bash
GET /api/projects
GET /api/sprints
```

---

## Jira Webhook Configuration

### 1. Setup Webhook in Jira

1. Go to **Jira Settings** → **System** → **WebHooks**
2. Click **Create a WebHook**
3. Configure:
   - **Name**: CoreSight Integration
   - **Status**: Enabled
   - **URL**: `https://your-domain.com/api/webhook/jira`
   - **Events**: 
     - ✅ Issue → created
     - ✅ Issue → updated
     - ✅ Sprint → created
     - ✅ Sprint → started

### 2. Test Webhook

Create a new issue in Jira and check the CoreSight logs.

---

## Webhook Events Handled

### 1. `jira:issue_created` ✅ IMPLEMENTED

**Workflow:**

1. **Extract Data**: Parse issue details (title, description, project, sprint, priority)
2. **Create Project**: Get or create project in MongoDB
3. **Create Sprint**: Get or create sprint in MongoDB
4. **Skill Extraction**: Use DeepSeek LLM to extract required skills
   ```
   Input: "Implement user authentication with OAuth2"
   Output: ["Python", "FastAPI", "OAuth2", "Security", "JWT"]
   ```
5. **Generate Embeddings**: Create vector representation using Yuan Embedding
   - Task description → 768-dimensional vector
   - Required skills → 768-dimensional vector
6. **Find Matching Users**: Calculate cosine similarity between:
   - Task skill embeddings ↔ User skill embeddings (70% weight)
   - Task description ↔ User work profile (30% weight)
7. **LLM Validation**: Ask DeepSeek to validate if user can do the task
   ```json
   {
     "can_do": true,
     "confidence": 0.85,
     "reasoning": "Developer has Python and FastAPI experience...",
     "recommendations": "Review OAuth2 documentation"
   }
   ```
8. **Auto-Assign**: If validated (confidence > 0.5), assign to best match
9. **Create Work Session**: Start tracking time

**Response Scenarios:**

✅ **Success - Assigned**
```json
{
  "status": "assigned",
  "task_id": "507f1f77bcf86cd799439011",
  "issue_key": "PROJ-123",
  "assigned_to": {
    "user_id": "507f...",
    "name": "Alice Johnson",
    "match_score": 0.87
  },
  "validation": {
    "can_do": true,
    "confidence": 0.85,
    "reasoning": "..."
  },
  "required_skills": ["Python", "FastAPI"]
}
```

⚠️ **No Match Found**
```json
{
  "status": "no_match",
  "task_id": "507f...",
  "report": {
    "severity": "critical",
    "message": "No developers with required skills",
    "missing_skills": ["Rust", "WebAssembly"],
    "recommendations": [
      "Consider upskilling current team",
      "External hiring required"
    ],
    "should_post_job": true,
    "suggested_job_title": "Rust Developer - WebAssembly"
  },
  "action_required": "create_job_posting"
}
```

❌ **Validation Failed**
```json
{
  "status": "validation_failed",
  "attempted_user": "Bob Smith",
  "validation": {
    "can_do": false,
    "confidence": 0.45,
    "reasoning": "Lacks OAuth2 experience"
  },
  "alternative_users": [
    {"name": "Alice", "match_score": 0.78}
  ]
}
```

### 2. `jira:issue_updated` ⏳ TODO

Planned features:
- Track status changes
- Update work sessions when issue transitions
- Re-assign if needed

### 3. `sprint:created` ⏳ BASIC

Creates sprint in database with metadata.

### 4. `sprint:started` ⏳ TODO

Planned features:
- Auto-assign all pending tasks
- Load balance across team
- Skill-based distribution

---

## AI Models Used

### 1. **Yuan Embedding Model** (IEITYuan/Yuan-embedding-2.0-en)

**Purpose**: Generate semantic embeddings for text

**Used For**:
- Task descriptions → vectors
- User skills → vectors
- Similarity matching

**Output**: 768-dimensional float vector

### 2. **DeepSeek LLM** (deepseek-ai/DeepSeek-R1-0528)

**Purpose**: Intelligent text analysis and decision making

**Used For**:
1. **Skill Extraction**
   - Input: Task title + description
   - Output: JSON array of required skills
   
2. **Assignment Validation**
   - Input: User skills + Task requirements
   - Output: JSON decision with reasoning
   
3. **Critical Gap Analysis**
   - Input: Task + Available team
   - Output: JSON report with recommendations

---

## Database Schema

### Users Collection

```javascript
{
  "_id": ObjectId,
  "name": "Alice Johnson",
  "email": "alice@company.com",
  "role": "employee",  // "admin" | "employee"
  "hourly_rate": 75.0,
  "skills": ["Python", "FastAPI", "MongoDB"],
  "work_profile_embeddings": [0.123, 0.456, ...],  // 768 floats
  "project_metrics": {
    "project_id_1": 120.5,  // hours spent (familiarity)
    "project_id_2": 45.0
  },
  "github_username": "alicejohnson",
  "jira_account_id": "712020:xxxxx"
}
```

### Tasks Collection

```javascript
{
  "_id": ObjectId,
  "external_id": "PROJ-123",  // Jira issue key
  "title": "Implement OAuth2 authentication",
  "description": "Full task description...",
  "description_embeddings": [0.234, 0.567, ...],  // 768 floats
  "type": "feature",  // "feature" | "bug" | "tech_debt" | "docs"
  "status": "todo",  // "todo" | "in_progress" | "review" | "done"
  "priority": "High",
  "project_id": "507f...",
  "sprint_id": "507f...",
  "current_assignee_ids": ["507f..."],  // Multi-user support
  "sprint_history": ["507f...", "507f..."],
  "rollover_count": 2,
  "total_time_spent_minutes": 480,
  "total_cost": 600.0,
  "created_at": ISODate,
  "updated_at": ISODate
}
```

### Work Sessions Collection

```javascript
{
  "_id": ObjectId,
  "task_id": "507f...",
  "user_id": "507f...",
  "start_time": ISODate,
  "end_time": ISODate,  // null = currently working
  "duration_minutes": 120.0,
  "assigned_by_user_id": "507f..."  // null = system assigned
}
```

### Projects Collection

```javascript
{
  "_id": ObjectId,
  "name": "CoreSight",
  "repo_url": "https://github.com/company/coresight",
  "total_budget": 50000.0
}
```

### Sprints Collection

```javascript
{
  "_id": ObjectId,
  "project_id": "507f...",
  "name": "Sprint 1",
  "start_date": ISODate,
  "end_date": ISODate,
  "goal": "Complete authentication module",
  "is_active": true
}
```

---

## Testing

### 1. Create Test Users

```bash
curl -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Johnson",
    "email": "alice@company.com",
    "role": "employee",
    "hourly_rate": 75.0,
    "skills": ["Python", "FastAPI", "MongoDB", "React", "Docker"],
    "github_username": "alice"
  }'
```

Create multiple users with different skill sets.

### 2. Trigger Jira Webhook

Create an issue in Jira or manually send webhook:

```bash
curl -X POST http://localhost:8080/api/webhook/jira \
  -H "Content-Type: application/json" \
  -d @webhook_test.json
```

### 3. Check Logs

Watch the console for:
- ✅ Skill extraction results
- ✅ Embedding generation
- ✅ User matching scores
- ✅ LLM validation output
- ✅ Assignment decision

### 4. Query Results

```bash
# List tasks
curl http://localhost:8080/api/tasks

# Get recommendations for a task
curl http://localhost:8080/api/tasks/{task_id}/recommendations
```

---

## Algorithm Details

### Cosine Similarity Calculation

```python
similarity = dot(vec_a, vec_b) / (norm(vec_a) * norm(vec_b))
```

Range: -1 to 1 (we use 0 to 1)

### Combined Matching Score

```python
combined_score = (skill_similarity * 0.7) + (profile_similarity * 0.3)
```

- **70%** weight on skill match (explicit skills)
- **30%** weight on work profile (past experience patterns)

### Validation Threshold

- **Confidence > 0.5**: Auto-assign
- **Confidence ≤ 0.5**: Manual review required

---

## Future Enhancements

### TODO List

1. ✅ Issue creation handling
2. ⏳ Issue update handling
3. ⏳ Sprint auto-assignment
4. ⏳ Load balancing algorithm
5. ⏳ Job posting API integration
6. ⏳ GitHub commit tracking
7. ⏳ Time tracking automation
8. ⏳ Sprint rollover handling
9. ⏳ Performance analytics
10. ⏳ Skill recommendation engine

### Placeholder Functions

```python
async def create_job_posting_placeholder(required_skills, task_title):
    """
    TODO: Implement job posting logic
    - Generate job description using LLM
    - Post to job board API (LinkedIn, Indeed)
    - Create internal requisition
    """
    pass
```

---

## Troubleshooting

### Issue: Embeddings return zero vectors

**Solution**: Check if Featherless AI API key is valid. The system will fallback to hash-based embeddings.

### Issue: No users matched

**Cause**: Empty users collection or skill mismatch

**Solution**: Create users with relevant skills using `/api/users` endpoint

### Issue: LLM returns invalid JSON

**Cause**: Model output contains extra text

**Solution**: System automatically extracts JSON from response. Check logs for "Error extracting skills"

### Issue: MongoDB connection failed

**Cause**: MongoDB not running or wrong connection string

**Solution**: Start MongoDB and verify `MONGODB_URL` in `.env`

---

## Contact & Support

For issues and questions:
- Check logs for detailed error messages
- Review `/docs` endpoint for API documentation
- All webhook events are logged with full context

**Built for DataZen Hackathon - Somaiya Vidyavihar University**
