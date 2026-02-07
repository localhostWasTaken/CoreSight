# AI-Powered Issue and Commit Endpoints

## Overview

This document describes the two new AI-powered endpoints that utilize Vector Database embeddings and LLM reasoning to intelligently process issues and commits.

## Tech Stack

- **Backend**: Python/FastAPI
- **Database**: MongoDB with Motor (async driver)
- **Vector Storage**: In-memory vector similarity using NumPy
- **LLM**: Featherless AI (DeepSeek-R1)
- **Embeddings**: Yuan-embedding-2.0-en

## Architecture

### Vector Search Flow
1. Generate embeddings for text content (issues/commits)
2. Store embeddings in MongoDB as arrays
3. Calculate cosine similarity using NumPy for similarity search
4. LLM analyzes top results for intelligent decision-making

---

## Endpoint 1: POST /api/issues

### Purpose
Intelligently process new issues by detecting duplicates, extracting skills, and automatically assigning to developers.

### Request Body

```json
{
  "title": "Implement user authentication",
  "description": "Need to add JWT-based authentication to the API with role-based access control",
  "priority": "high",
  "project_id": "optional_project_id",
  "source": "api",
  "external_id": "PROJ-123"
}
```

### Logic Flow

#### Step 1: Ingest & Embed
- Receives issue description
- Generates embedding using `generate_embedding()`
- Ensures embeddings are stored in the database

#### Step 2: Similarity Search
- Queries Vector DB for top 5 similar existing issues
- Uses cosine similarity with threshold 0.7
- Returns issues with similarity scores

#### Step 3: LLM Reasoning
- Sends new issue + similar results to LLM
- LLM determines if duplicate or new issue

#### Scenario A: Duplicate/Existing Issue
If LLM identifies it as existing:
1. Updates activity log of parent task
2. Checks if priority changed (using LLM)
3. Checks if new skills are required
4. Updates parent task metadata
5. Re-generates embeddings if skills changed

#### Scenario B: New Issue
If unique:
1. Creates new Task document
2. Extracts required technical skills (using LLM)
3. Generates skill embeddings
4. Matches against Employee/Developer profiles
   - **Match found**: Assigns task to best developer
   - **No match**: Calls `trigger_job_posting()` function

### Response Examples

#### Scenario A: Duplicate Issue
```json
{
  "analysis": {
    "is_duplicate": true,
    "parent_task_id": "507f1f77bcf86cd799439011",
    "confidence": 0.92,
    "reasoning": "This issue describes the same OAuth integration mentioned in existing Issue #2",
    "priority_change": "increased",
    "new_skills_required": ["OAuth 2.0", "Azure AD"]
  },
  "similar_issues_found": 3,
  "action": "updated_existing",
  "parent_task_id": "507f1f77bcf86cd799439011",
  "message": "Duplicate issue - parent task updated"
}
```

#### Scenario B: New Issue with Assignment
```json
{
  "analysis": {
    "is_duplicate": false,
    "confidence": 1.0,
    "reasoning": "No similar issues found"
  },
  "issue_id": "507f191e810c19729de860ea",
  "required_skills": ["Python", "FastAPI", "JWT", "MongoDB", "Security"],
  "action": "created_and_assigned",
  "assigned_to": {
    "user_id": "507f1f77bcf86cd799439012",
    "name": "Alice Johnson",
    "match_score": 0.87
  },
  "matching_candidates": [
    {
      "user_id": "507f1f77bcf86cd799439012",
      "name": "Alice Johnson",
      "match_score": 0.87,
      "skills": ["Python", "FastAPI", "MongoDB", "Security", "Docker"]
    }
  ]
}
```

#### Scenario B: New Issue requiring Job Posting
```json
{
  "analysis": {
    "is_duplicate": false,
    "confidence": 1.0,
    "reasoning": "No similar issues found"
  },
  "issue_id": "507f191e810c19729de860eb",
  "required_skills": ["Rust", "WebAssembly", "Systems Programming"],
  "action": "created_requires_posting",
  "job_posting": {
    "triggered": true,
    "job_title": "Implement user authentication",
    "required_skills": ["Rust", "WebAssembly", "Systems Programming"],
    "status": "pending_recruiter_review",
    "message": "Job posting will be created by recruiter"
  }
}
```

### Database Collections Used

- **issues**: Stores issue documents with embeddings
- **users**: Employee profiles with skills and embeddings
- **tasks**: Jira/project tasks (for similarity matching)

---

## Endpoint 2: POST /api/commits

### Purpose
Analyze commit diffs using LLM to extract skills, link to tasks, and evolve developer profiles.

### Request Body

```json
{
  "commit_hash": "a1b2c3d4e5f6",
  "commit_message": "Add MongoDB connection pooling and retry logic",
  "diff": "diff --git a/database.py b/database.py\n...",
  "author_email": "dev@example.com",
  "author_name": "John Developer",
  "repository": "coresight-backend",
  "branch": "main",
  "files_changed": 3,
  "lines_added": 150,
  "lines_deleted": 45
}
```

### Logic Flow

#### Step 1: Ingest & Analyze
- Receives GitHub commit diff
- Sends diff to LLM for analysis

#### Step 2: LLM Extraction
LLM extracts:
- Summary of problem solved or feature built
- Technical skills used in this specific commit
- Impact assessment (minor/moderate/significant)

#### Step 3: Task Linking
- Embeds the summary
- Searches Vector DB for existing Issue/Task
- **Match found** (similarity ≥ 0.7): Logs commit under that Task ID
- **No match**: Logs as "Non-Jira Tracked Activity"

#### Step 4: Profile Evolution
1. Fetches user's current Work Profile and Embeddings
2. Sends Current Profile + New Commit Skills to LLM
3. LLM determines if profile needs updating
4. **If yes**: 
   - Updates text profile
   - Adds new skills to user's skill list
   - Re-generates profile embedding
   - Saves to DB

### Response Example

```json
{
  "commit_id": "507f191e810c19729de860ec",
  "commit_hash": "a1b2c3d4e5f6",
  "analysis": {
    "summary": "Implemented connection pooling for MongoDB with automatic retry logic to improve database reliability and performance",
    "skills_extracted": ["Python", "MongoDB", "Database Optimization", "Error Handling", "Async Programming"],
    "impact_assessment": "moderate"
  },
  "task_linking": {
    "linked_task_id": "507f1f77bcf86cd799439013",
    "is_jira_tracked": true,
    "matching_tasks_found": 2,
    "similar_tasks": [
      {
        "task_id": "507f1f77bcf86cd799439013",
        "external_id": "PROJ-45",
        "title": "Improve database connection reliability",
        "similarity_score": 0.85
      }
    ]
  },
  "profile_evolution": {
    "updated": true,
    "new_skills_added": ["Database Optimization"],
    "total_skills": 12
  }
}
```

### Database Collections Used

- **commits**: Stores commit documents with analysis
- **tasks**: Searches for matching tasks
- **users**: Updates developer profiles

---

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Variables

Create `.env` file:

```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=coresight

# AI Services
FEATHERLESS_BASE_URL=https://api.featherless.ai/v1
FEATHERLESS_API_KEY=your_api_key_here
EMBEDDING_MODEL=IEITYuan/Yuan-embedding-2.0-en
LLM_MODEL=deepseek-ai/DeepSeek-R1-0528
```

### 3. Run the Server

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --reload --port 8000
```

Or use a custom port:

```bash
API_PORT=8888 python main.py
```

### 4. Access API Documentation

Navigate to: `http://localhost:8000/docs`

---

## Testing the Endpoints

### Test POST /api/issues

```bash
curl -X POST http://localhost:8000/api/issues \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Add Redis caching layer",
    "description": "Implement Redis caching for frequently accessed data to improve API response times",
    "priority": "high"
  }'
```

### Test POST /api/commits

```bash
curl -X POST http://localhost:8000/api/commits \
  -H "Content-Type: application/json" \
  -d '{
    "commit_hash": "abc123def456",
    "commit_message": "Add Redis caching for user sessions",
    "diff": "diff --git a/cache.py...",
    "author_email": "dev@example.com",
    "author_name": "Developer",
    "repository": "backend",
    "branch": "main",
    "files_changed": 2,
    "lines_added": 100,
    "lines_deleted": 10
  }'
```

---

## Key Features

### Vector Search
- **Cosine Similarity**: Measures semantic similarity between embeddings
- **Threshold-based**: Only considers matches above similarity threshold
- **Top-K Results**: Returns configurable number of top matches

### LLM Reasoning
- **Context-Aware**: Provides full context to LLM for better decisions
- **Structured Output**: LLM returns JSON for easy parsing
- **Fallback Logic**: Handles LLM failures gracefully

### Profile Evolution
- **Automatic Skill Detection**: Discovers new skills from commits
- **Incremental Updates**: Only updates when significant changes detected
- **Deduplicated Skills**: Prevents duplicate skills in user profiles

### Job Posting Trigger
- **Automated Detection**: Identifies skill gaps immediately
- **Placeholder Function**: Ready for ATS integration
- **Clear Notifications**: Provides detailed job posting requirements

---

## Data Models

### Issue Model
```python
{
    "title": str,
    "description": str,
    "description_embedding": List[float],  # 768-dim vector
    "required_skills": List[str],
    "skill_embeddings": List[float],
    "priority": str,
    "is_duplicate": bool,
    "parent_task_id": Optional[str],
    "assigned_user_id": Optional[str],
    "assignment_status": str,  # pending, assigned, posting_required
    "activity_log": List[str],
    "created_at": datetime,
    "updated_at": datetime
}
```

### Commit Model
```python
{
    "commit_hash": str,
    "commit_message": str,
    "diff_content": str,
    "summary": str,
    "extracted_skills": List[str],
    "summary_embedding": List[float],
    "linked_task_id": Optional[str],
    "is_jira_tracked": bool,
    "author_email": str,
    "author_name": str,
    "user_id": Optional[str],
    "repository": str,
    "branch": str,
    "triggered_profile_update": bool,
    "created_at": datetime
}
```

---

## Performance Considerations

### Vector Search Optimization
- **In-Memory Calculation**: Fast for small-medium datasets (<10k items)
- **Future Optimization**: Consider MongoDB Atlas Vector Search for large datasets
- **Caching**: Embeddings are cached in database to avoid regeneration

### LLM Usage
- **Rate Limiting**: Be mindful of API rate limits
- **Cost Management**: Each call costs tokens
- **Fallback Logic**: Always has non-LLM fallback for reliability

---

## Integration Examples

### GitHub Webhook Integration
```python
@app.post("/webhook/github")
async def github_webhook(request: Request):
    payload = await request.json()
    
    if payload.get("ref") == "refs/heads/main":
        commits = payload.get("commits", [])
        
        for commit in commits:
            await process_commit_with_ai(Request({
                "json": {
                    "commit_hash": commit["id"],
                    "commit_message": commit["message"],
                    "diff": "...",  # Fetch from GitHub API
                    "author_email": commit["author"]["email"],
                    # ...
                }
            }))
```

### Jira Integration
```python
@app.post("/webhook/jira")
async def jira_webhook(request: Request):
    data = await request.json()
    
    if data["webhookEvent"] == "jira:issue_created":
        issue = data["issue"]
        
        await create_issue_with_ai(Request({
            "json": {
                "title": issue["fields"]["summary"],
                "description": issue["fields"]["description"],
                "priority": issue["fields"]["priority"]["name"].lower(),
                "external_id": issue["key"]
            }
        }))
```

---

## Troubleshooting

### Issue: "Database not available"
**Solution**: Ensure MongoDB is running and connection string is correct in `.env`

### Issue: "LLM returns invalid JSON"
**Solution**: The code has fallback logic that handles this. Check logs for details.

### Issue: "No embeddings generated"
**Solution**: Verify Featherless API key is valid and has sufficient credits.

### Issue: "No matching users found"
**Solution**: Ensure users exist in database with skills populated. Use `/api/users` endpoint to create users.

---

## Future Enhancements

1. **Vector Database**: Migrate to dedicated vector DB (Pinecone, Weaviate, Qdrant)
2. **Batch Processing**: Process multiple issues/commits in parallel
3. **Real-time Updates**: WebSocket notifications for assignments
4. **Advanced Matching**: Consider workload, availability, project history
5. **Skill Taxonomy**: Standardize skill names and hierarchies
6. **Analytics Dashboard**: Visualize profile evolution over time

---

## API Reference

### Health Check
```
GET /health
Response: { "status": "healthy", "version": "1.0.0" }
```

### List Users
```
GET /api/users
Response: { "count": int, "users": [...] }
```

### Create User
```
POST /api/users
Body: { "name", "email", "skills", "hourly_rate", ... }
```

### List Issues
You can query the database directly or add a GET endpoint:
```python
@app.get("/api/issues")
async def list_issues():
    issues = await db_manager.find_many("issues", {})
    return {"count": len(issues), "issues": issues}
```

---

## Contact & Support

For questions or issues, please refer to the main [README.md](../README.md) or contact the development team.
