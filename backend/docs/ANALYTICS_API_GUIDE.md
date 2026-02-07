# CoreSight Analytics API Documentation

## Overview

The Analytics module provides advanced insights into code patterns, task costs, and team health for the CoreSight platform. It transforms raw engineering activity into actionable business intelligence.

## Table of Contents

1. [Code Impact Analysis](#code-impact-analysis)
2. [True Task Costing](#true-task-costing)
3. [Context Switching (Burnout Detection)](#context-switching-burnout-detection)
4. [API Reference](#api-reference)
5. [Use Cases](#use-cases)

---

## Code Impact Analysis

### "Maker vs. Mender" Score

Analyzes commit patterns to categorize developers based on their work style.

### Metrics

- **Refactor Ratio**: `(lines_deleted + lines_modified) / (lines_added + lines_deleted + lines_modified)`
- **Category Breakdown**: Percentage of work in each category

### Categories

| Category | Refactor Ratio | Description |
|----------|---------------|-------------|
| **New Feature** | < 0.3 | Mostly code additions - building new functionality |
| **Refactoring** | 0.3 - 0.6 | Balanced changes - improving existing code |
| **Cleanup** | > 0.6 | Mostly deletions - removing dead code/tech debt |

### Developer Profiles

| Profile | Criteria | Description |
|---------|----------|-------------|
| **Maker** | ≥50% New Features | Builders and creators - focus on new development |
| **Mender** | ≥40% Refactoring | Maintainers - focus on code quality and improvements |
| **Cleaner** | ≥40% Cleanup | Tech debt resolvers - focus on cleanup and simplification |
| **Balanced** | Mixed distribution | Versatile developers working across all areas |

### Endpoint

```
GET /api/analytics/user/{user_id}/impact_breakdown
```

### Example Response

```json
{
  "success": true,
  "data": {
    "user_id": "507f1f77bcf86cd799439011",
    "total_commits": 45,
    "total_lines_added": 3420,
    "total_lines_deleted": 1280,
    "total_lines_modified": 560,
    "overall_refactor_ratio": 0.35,
    "profile": "maker",
    "category_breakdown": {
      "new_feature": {
        "count": 28,
        "percentage": 62.2
      },
      "refactoring": {
        "count": 12,
        "percentage": 26.7
      },
      "cleanup": {
        "count": 5,
        "percentage": 11.1
      }
    },
    "recent_commits": [
      {
        "commit_hash": "abc123def456",
        "commit_message": "Implement user authentication flow",
        "lines_added": 234,
        "lines_deleted": 12,
        "lines_modified": 15,
        "refactor_ratio": 0.103,
        "category": "new_feature",
        "timestamp": "2026-02-01T10:30:00Z"
      }
    ]
  }
}
```

### Business Value

- **Team Composition**: Balance makers (builders) vs menders (maintainers)
- **Tech Debt Tracking**: Monitor cleanup work and refactoring efforts
- **Skill Assessment**: Identify developer strengths and specializations
- **Resource Planning**: Allocate resources based on project needs (new features vs maintenance)

---

## True Task Costing

### Overview

Calculates the actual cost of tasks by aggregating all work sessions and user hourly rates.

### Cost Calculation

```
Task Cost = Σ (work_session.duration_hours × user.hourly_rate)
```

### Budget Analysis

- **Pro-rated Budget**: `project.total_budget / task_count`
- **Budget Variance**: `actual_cost - prorated_budget`
- **Variance Percentage**: `(variance / prorated_budget) × 100`

### Endpoint

```
GET /api/analytics/task/{task_id}/cost
```

### Example Response

```json
{
  "success": true,
  "data": {
    "task_id": "507f1f77bcf86cd799439012",
    "task_title": "Implement payment gateway integration",
    "task_type": "feature",
    "task_status": "done",
    "total_cost": 4250.00,
    "total_hours": 68.5,
    "average_hourly_rate": 62.04,
    "user_breakdown": [
      {
        "user_id": "507f1f77bcf86cd799439011",
        "user_name": "Alice Johnson",
        "hourly_rate": 75.00,
        "hours_worked": 42.5,
        "total_cost": 3187.50,
        "session_count": 12
      },
      {
        "user_id": "507f1f77bcf86cd799439013",
        "user_name": "Bob Smith",
        "hourly_rate": 50.00,
        "hours_worked": 26.0,
        "total_cost": 1062.50,
        "session_count": 8
      }
    ],
    "budget_analysis": {
      "project_name": "E-Commerce Platform",
      "project_total_budget": 100000.00,
      "task_count_in_project": 45,
      "prorated_task_budget": 2222.22,
      "budget_variance": 2027.78,
      "budget_variance_percentage": 91.3,
      "status": "over_budget"
    }
  }
}
```

### Business Value

- **Accurate Costing**: True task costs vs estimates
- **Budget Monitoring**: Real-time budget tracking and alerts
- **Resource Optimization**: Identify expensive tasks and optimize allocation
- **Future Estimation**: Historical data for better project estimation
- **Client Billing**: Accurate time and cost tracking for billable work

### Insights

- Tasks consistently over budget may indicate:
  - Underestimation in planning
  - Technical complexity issues
  - Resource skill mismatches
  - Scope creep
- Use variance trends to improve estimation accuracy

---

## Context Switching (Burnout Detection)

### Overview

Analyzes work session patterns to detect excessive task switching, a key indicator of developer burnout and productivity loss.

### Metrics

- **Context Switches per Day**: Number of distinct tasks worked on - 1
- **Risk Level**: Based on average switches and high-risk days
- **Focus Health Score**: Team-wide productivity indicator

### Risk Thresholds

| Risk Level | Criteria | Action Required |
|------------|----------|-----------------|
| **High** | ≥4 switches/day average OR ≥40% high-risk days | Immediate intervention |
| **Medium** | ≥2.8 switches/day (70% of threshold) | Monitor closely |
| **Low** | <2.8 switches/day | Healthy focus pattern |

### Endpoint

```
GET /api/analytics/team/focus_health?days=7&threshold=4
```

### Query Parameters

- `days` (optional): Analysis period (1-30 days, default: 7)
- `threshold` (optional): Context switches per day to flag as high risk (2-10, default: 4)

### Example Response

```json
{
  "success": true,
  "data": {
    "analysis_period": {
      "days": 7,
      "start_date": "2026-02-01",
      "end_date": "2026-02-08"
    },
    "team_summary": {
      "total_users_analyzed": 12,
      "high_risk_users": 3,
      "medium_risk_users": 4,
      "low_risk_users": 5,
      "total_context_switches": 156,
      "average_switches_per_user": 13.0
    },
    "alert": {
      "high_risk_threshold": 4,
      "users_flagged": [
        "Alice Johnson",
        "Charlie Davis",
        "Eve Williams"
      ],
      "message": "3 user(s) showing signs of context switching overload"
    },
    "user_details": [
      {
        "user_id": "507f1f77bcf86cd799439011",
        "user_name": "Alice Johnson",
        "total_context_switches": 32,
        "average_switches_per_day": 4.57,
        "max_switches_in_day": 7,
        "high_risk_days": 5,
        "days_analyzed": 7,
        "risk_level": "high",
        "daily_breakdown": [
          {
            "date": "2026-02-08",
            "unique_tasks": 6,
            "context_switches": 5,
            "risk_level": "high"
          },
          {
            "date": "2026-02-07",
            "unique_tasks": 8,
            "context_switches": 7,
            "risk_level": "high"
          }
        ]
      }
    ]
  }
}
```

### Business Value

- **Burnout Prevention**: Early detection of overwhelmed developers
- **Productivity Optimization**: Reduce context switching costs (studies show 20-40% productivity loss)
- **Resource Management**: Identify workload distribution issues
- **Sprint Planning**: Better task allocation based on focus patterns
- **Team Health**: Monitor and maintain sustainable work pace

### Research-Backed Insights

**Context Switching Costs:**
- Average 23 minutes to fully refocus after switching tasks
- 40% productivity loss with frequent interruptions
- Strong correlation with developer burnout

**Recommendations for High-Risk Users:**
- Reduce active task assignments
- Implement "focus time" blocks (2-4 hour uninterrupted periods)
- Batch similar tasks together
- Limit to 2-3 active tasks maximum
- Review workload in sprint planning

---

## API Reference

### Base URL

```
http://localhost:8080/api/analytics
```

### Authentication

All endpoints use the same authentication as the main CoreSight API.

### Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/user/{user_id}/impact_breakdown` | GET | Code impact analysis |
| `/task/{task_id}/cost` | GET | Task cost analysis |
| `/team/focus_health` | GET | Team context switching analysis |
| `/health` | GET | Service health check |
| `/summary` | GET | Analytics capabilities overview |

### Error Handling

All endpoints return standard error responses:

```json
{
  "detail": "Error message"
}
```

**Common Error Codes:**
- `404`: User, task, or resource not found
- `422`: Invalid parameters (e.g., days out of range)
- `500`: Internal server error

---

## Use Cases

### 1. Weekly Team Review

**Goal**: Identify at-risk developers and assess team health

**Steps:**
1. Run `GET /team/focus_health` for the past 7 days
2. Review high-risk users and daily patterns
3. Adjust task assignments for flagged developers
4. Run `GET /user/{user_id}/impact_breakdown` for each user
5. Assess team composition (makers vs menders)

### 2. Sprint Planning

**Goal**: Optimize task assignments based on historical data

**Steps:**
1. Review previous sprint's task costs
2. Identify patterns in over-budget tasks
3. Use cost data to improve estimates
4. Check team focus health before assigning new tasks
5. Balance task assignments based on developer profiles

### 3. Project Budget Tracking

**Goal**: Monitor project spending and forecast completion costs

**Steps:**
1. Pull cost analysis for all completed tasks
2. Calculate average cost per task type
3. Compare variance trends over time
4. Forecast remaining budget needs
5. Identify cost optimization opportunities

### 4. Developer Performance Review

**Goal**: Data-driven performance assessment

**Steps:**
1. Review developer's impact breakdown
2. Analyze task contributions and costs
3. Assess focus health and context switching patterns
4. Identify strengths and growth areas
5. Set data-backed development goals

### 5. Tech Debt Management

**Goal**: Track and prioritize technical debt work

**Steps:**
1. Filter commits by "cleanup" category
2. Track refactoring vs feature work ratio
3. Identify "cleaner" profile developers
4. Allocate dedicated tech debt sprints
5. Measure cleanup impact on codebase health

---

## Integration Examples

### Python Client

```python
import httpx

BASE_URL = "http://localhost:8080/api/analytics"

async def get_team_health():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/team/focus_health",
            params={"days": 7, "threshold": 4}
        )
        return response.json()

async def get_task_cost(task_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/task/{task_id}/cost"
        )
        return response.json()
```

### cURL Examples

```bash
# Get user impact breakdown
curl -X GET "http://localhost:8080/api/analytics/user/507f1f77bcf86cd799439011/impact_breakdown"

# Get task cost analysis
curl -X GET "http://localhost:8080/api/analytics/task/507f1f77bcf86cd799439012/cost"

# Get team focus health (7 days, threshold 4)
curl -X GET "http://localhost:8080/api/analytics/team/focus_health?days=7&threshold=4"
```

### JavaScript/TypeScript

```typescript
const BASE_URL = 'http://localhost:8080/api/analytics';

async function getTeamFocusHealth(days = 7, threshold = 4) {
  const response = await fetch(
    `${BASE_URL}/team/focus_health?days=${days}&threshold=${threshold}`
  );
  return await response.json();
}

async function getUserImpact(userId: string) {
  const response = await fetch(
    `${BASE_URL}/user/${userId}/impact_breakdown`
  );
  return await response.json();
}
```

---

## Best Practices

### 1. Regular Monitoring

- Run focus health analysis weekly
- Review cost variance monthly
- Track impact breakdown trends quarterly

### 2. Threshold Tuning

- Adjust context switching threshold based on your team
- Consider team size and project complexity
- Start conservative (threshold=4) and tune based on results

### 3. Action on Insights

- Don't just collect data - act on it
- High-risk developers need workload reduction
- Over-budget tasks need process review
- Profile imbalances need hiring or training

### 4. Combine Metrics

- Use all three analytics together for full picture
- High context switching + mender profile = potential burnout
- High cost + many refactoring commits = tech debt issues

### 5. Privacy & Ethics

- Use data to help, not punish
- Focus on process improvement, not individual blame
- Share insights transparently with the team
- Respect developer privacy and autonomy

---

## Troubleshooting

### No Data Returned

**Problem**: Empty results or "No data found" messages

**Solutions:**
- Ensure commits, work sessions, and tasks are being tracked
- Check date ranges - data may be outside analysis period
- Verify user/task IDs are correct
- Confirm database connections are healthy

### Inaccurate Cost Calculations

**Problem**: Task costs seem wrong

**Solutions:**
- Verify user hourly rates are set correctly
- Check work session duration calculations
- Ensure all work sessions have end_time set
- Review if sessions are properly linked to tasks

### High Risk False Positives

**Problem**: Too many users flagged as high risk

**Solutions:**
- Increase threshold parameter (e.g., 5 or 6)
- Reduce analysis period if short-term spike
- Consider if your team naturally works on many small tasks
- Review if work sessions are being created correctly

---

## Future Enhancements

### Planned Features

1. **Predictive Analytics**: ML models for task cost estimation
2. **Team Collaboration Metrics**: PR review patterns and collaboration scores
3. **Code Quality Trends**: Correlate impact patterns with bug rates
4. **Custom Dashboards**: Configurable analytics views
5. **Alerts & Notifications**: Automated alerts for high-risk conditions
6. **Historical Comparisons**: Sprint-over-sprint trend analysis
7. **Export & Reporting**: PDF/Excel report generation

### API Versioning

Current version: `v1.0.0`

Breaking changes will be communicated via:
- Version headers
- Deprecation notices in responses
- Migration guides in documentation

---

## Support

For issues, questions, or feature requests related to the Analytics module:

- Open an issue on the project repository
- Contact the development team
- Refer to the main CoreSight documentation

---

## Changelog

### Version 1.0.0 (2026-02-08)

**Initial Release**

- ✅ Code Impact Analysis (Maker vs. Mender Score)
- ✅ True Task Costing with budget variance
- ✅ Context Switching (Burnout Detection)
- ✅ Comprehensive API documentation
- ✅ Integration with existing CoreSight models

---

**Built with ❤️ for the DataZen Hackathon - Somaiya Vidyavihar University**
