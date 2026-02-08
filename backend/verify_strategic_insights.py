
import os
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
import requests
import json
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "coresight")
API_URL = "http://localhost:8000"

def setup_test_data():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    print("🧹 Cleaning up old test data...")
    # Clean up any previous test data if needed, but for now we append with timestamps
    timestamp = datetime.now().strftime("%H%M%S")
    
    # 1. Create User
    user_res = db.users.insert_one({
        "name": f"Test User {timestamp}",
        "email": f"testuser{timestamp}@example.com",
        "role": "developer",
        "hourly_rate": 50
    })
    user_id = user_res.inserted_id
    print(f"👤 Created User: {user_id}")
    
    # 2. Create Projects
    p1_res = db.projects.insert_one({
        "name": f"Project A {timestamp}",
        "status": "active",
        "total_budget": 10000,
        "spent_budget": 2000
    })
    p2_res = db.projects.insert_one({
        "name": f"Project B {timestamp} (Budget Risk)",
        "status": "active",
        "total_budget": 10000,
        "spent_budget": 9000  # 90% spent
    })
    p3_res = db.projects.insert_one({
        "name": f"Project C {timestamp} (Stalled)",
        "status": "active",
        "total_budget": 10000,
        "spent_budget": 1000,
        "updated_at": datetime.utcnow() - timedelta(days=10) # Old update
    })
    
    # 3. Create Tasks (Assign to User across 3 projects)
    # Task in Project A
    db.tasks.insert_one({
        "title": f"Task A {timestamp}",
        "project_id": p1_res.inserted_id,
        "current_assignee_ids": [user_id],
        "status": "in_progress",
        "updated_at": datetime.utcnow()
    })
    # Task in Project B
    db.tasks.insert_one({
        "title": f"Task B {timestamp}",
        "project_id": p2_res.inserted_id,
        "current_assignee_ids": [user_id],
        "status": "in_progress",
        "updated_at": datetime.utcnow()
    })
    # Task in Project C
    db.tasks.insert_one({
        "title": f"Task C {timestamp}",
        "project_id": p3_res.inserted_id,
        "current_assignee_ids": [user_id],
        "status": "in_progress",
        "updated_at": datetime.utcnow() - timedelta(days=10)
    })
    
    print("✅ Test data seeded.")
    return user_id, [p1_res.inserted_id, p2_res.inserted_id, p3_res.inserted_id]

def test_endpoints(user_id):
    print("\n🧪 Testing Endpoints...")
    
    # 1. Test Burnout Risks
    print("\n[GET] /api/analytics/risks/burnout")
    try:
        res = requests.get(f"{API_URL}/api/analytics/risks/burnout")
        if res.status_code != 200:
            print(f"❌ Failed: {res.status_code} - {res.text}")
            return

        data = res.json()
        print(json.dumps(data, indent=2))
        
        risks = data.get("data", {}).get("risks", [])
        found = any(r["user_id"] == str(user_id) for r in risks)
        if found:
            print("✅ SUCCESS: Test User identified as burnout risk.")
        else:
            print("❌ FAILURE: Test User NOT found in burnout risks.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

    # 2. Test Business Recommendations
    print("\n[GET] /api/analytics/business/recommendations")
    try:
        res = requests.get(f"{API_URL}/api/analytics/business/recommendations")
        if res.status_code != 200:
            print(f"❌ Failed: {res.status_code} - {res.text}")
            return
            
        data = res.json()
        print(json.dumps(data, indent=2))
        
        recs = data.get("data", [])
        budget_risk = any("Budget Risk" in r.get("type", "") for r in recs) 
        stalled = any("stalled_project" in r.get("type", "") for r in recs)
        
        if budget_risk:
            print("✅ SUCCESS: Budget Risk identified.")
        else:
            print("❌ FAILURE: Budget Risk NOT found.")
            
        if stalled:
            print("✅ SUCCESS: Stalled Project identified.")
        else:
            print("❌ FAILURE: Stalled Project NOT found.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    try:
        user_id, project_ids = setup_test_data()
        test_endpoints(user_id)
    except Exception as e:
        print(f"❌ Script Error: {e}")
