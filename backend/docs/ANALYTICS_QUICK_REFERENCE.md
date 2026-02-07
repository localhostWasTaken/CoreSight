# Analytics Module - Quick Reference

## 🚀 Quick Start

The Analytics module is already integrated into your CoreSight FastAPI application. No additional setup required!

## 📊 Available Endpoints

### 1. Code Impact Analysis - "Maker vs. Mender"
```bash
GET /api/analytics/user/{user_id}/impact_breakdown
```

**What it does**: Analyzes commit patterns to categorize developers
- Calculates refactor ratio
- Categorizes commits: New Feature / Refactoring / Cleanup
- Identifies developer profile: Maker / Mender / Cleaner / Balanced

### 2. True Task Costing
```bash
GET /api/analytics/task/{task_id}/cost
```

**What it does**: Calculates actual task costs
- Aggregates all work sessions
- Calculates: duration × hourly_rate per user
- Compares against project budget
- Shows per-user breakdown

### 3. Context Switching (Burnout Detection)
```bash
GET /api/analytics/team/focus_health?days=7&threshold=4
```

**What it does**: Detects excessive task switching
- Counts distinct tasks per day per user
- Flags high-risk patterns (≥4 switches/day)
- Provides team-wide health metrics

---

## 🔥 Usage Examples

### Check a specific user's coding profile
```bash
curl http://localhost:8080/api/analytics/user/507f1f77bcf86cd799439011/impact_breakdown
```

### Get cost breakdown for a task
```bash
curl http://localhost:8080/api/analytics/task/507f1f77bcf86cd799439012/cost
```

### Monitor team health (last 7 days)
```bash
curl "http://localhost:8080/api/analytics/team/focus_health?days=7&threshold=4"
```

### Get analytics overview
```bash
curl http://localhost:8080/api/analytics/summary
```

---

## 📈 Key Metrics Explained

### Refactor Ratio
```
(lines_deleted + lines_modified) / (lines_added + lines_deleted + lines_modified)
```
- **< 0.3**: New Feature (mostly additions)
- **0.3 - 0.6**: Refactoring (balanced)
- **> 0.6**: Cleanup (mostly deletions)

### Developer Profiles
- **Maker**: 50%+ new features (builders)
- **Mender**: 40%+ refactoring (maintainers)
- **Cleaner**: 40%+ cleanup (tech debt resolvers)
- **Balanced**: Mix of all

### Context Switches
```
Number of distinct tasks in a day - 1
```
- **High Risk**: ≥4 switches/day
- **Medium Risk**: ≥2.8 switches/day
- **Low Risk**: <2.8 switches/day

---

## 🎯 When to Use Each Endpoint

| Scenario | Endpoint | Frequency |
|----------|----------|-----------|
| Weekly team review | `/team/focus_health` | Weekly |
| Sprint retrospective | All endpoints | End of sprint |
| Performance review | `/user/{id}/impact_breakdown` | Quarterly |
| Budget tracking | `/task/{id}/cost` | Per task completion |
| Project planning | `/task/{id}/cost` (historical) | Before sprint planning |

---

## ⚙️ Files Added

```
backend/
├── services/
│   └── analytics_service.py          # Core analytics logic
├── routes/
│   └── analytics.py                  # API endpoints
└── docs/
    ├── ANALYTICS_API_GUIDE.md        # Full documentation
    └── ANALYTICS_QUICK_REFERENCE.md  # This file
```

---

## 🔗 Integration with Existing Models

The analytics module uses your existing data models:

- **Commit**: For code impact analysis
- **WorkSession**: For task costing and context switching
- **Task**: For linking work to projects
- **User**: For hourly rates and identification
- **Project**: For budget comparison

**No database changes required!** ✅

---

## 🧪 Testing the Endpoints

### Using the Swagger UI
1. Start your FastAPI server: `python main.py`
2. Open: `http://localhost:8080/docs`
3. Navigate to "Analytics" section
4. Try each endpoint with test data

### Using cURL
See examples above or check the full documentation.

### Using Python
```python
import httpx

async def test_analytics():
    async with httpx.AsyncClient() as client:
        # Get team health
        response = await client.get(
            "http://localhost:8080/api/analytics/team/focus_health",
            params={"days": 7, "threshold": 4}
        )
        print(response.json())
```

---

## 💡 Tips & Best Practices

1. **Start with team focus health** - easiest way to see value
2. **Tune the threshold** - adjust context switching threshold for your team
3. **Run regularly** - analytics are most valuable over time
4. **Act on insights** - don't just collect data, use it to improve
5. **Combine metrics** - use all three together for full picture

---

## 🐛 Common Issues

### "No data found"
- Ensure you have commits, work sessions, or tasks in the database
- Check that IDs are correct (use valid ObjectId format)
- Verify date ranges contain data

### "Database not initialized"
- Make sure the server is fully started
- Check MongoDB connection in logs

### Unexpected results
- Verify work sessions have `end_time` set (duration calculated on completion)
- Check user `hourly_rate` values are correct
- Ensure commits have proper line count data

---

## 📚 More Information

- **Full Documentation**: `docs/ANALYTICS_API_GUIDE.md`
- **API Docs**: `http://localhost:8080/docs#/Analytics`
- **Models Reference**: `entities/models.py`

---

## 🎉 What's Next?

Try these quick wins:

1. ✅ Test `/analytics/health` to verify setup
2. ✅ Run `/team/focus_health` on real data
3. ✅ Review `/summary` for capabilities overview
4. ✅ Integrate into your monitoring dashboard
5. ✅ Set up weekly health check reports

---

**Happy Analyzing! 📊**
