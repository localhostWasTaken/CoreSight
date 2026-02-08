
import os
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
import requests
import json
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "coresight")
API_URL = "http://localhost:8000"

def setup_test_data():
    client = MongoClient(MONGODB_URL)
    db = client[DB_NAME]
    print(f"DEBUG: DB_NAME={DB_NAME}, db_type={type(db)}")
    
    print("🧹 Cleaning up old test data...")
    timestamp = datetime.now().strftime("%H%M%S")
    
    # 1. Create User
    user_res = db.users.insert_one({
        "name": f"Value Test User {timestamp}",
        "email": f"valuetest{timestamp}@example.com",
        "role": "developer",
        "hourly_rate": 100 # Easy math
    })
    user_id = user_res.inserted_id
    print(f"👤 Created User: {user_id}")
    
    # 2. Create Commits with Value Scores
    # Commit 1: High Value
    db.commits.insert_one({
        "user_id": user_id,
        "commit_hash": f"abc{timestamp}",
        "commit_message": "Fix critical payment bug",
        "value_score": 95.0,
        "complexity": "high",
        "impact_reasoning": "Prevented revenue loss",
        "timestamp": datetime.utcnow()
    })
    
    # Commit 2: Medium Value
    db.commits.insert_one({
        "user_id": user_id,
        "commit_hash": f"def{timestamp}",
        "commit_message": "Refactor user service",
        "value_score": 50.0,
        "complexity": "medium",
        "impact_reasoning": "Improved maintainability",
        "timestamp": datetime.utcnow()
    })
    
    # Commit 3: Low Value
    db.commits.insert_one({
        "user_id": user_id,
        "commit_hash": f"ghi{timestamp}",
        "commit_message": "Fix typo in readme",
        "value_score": 5.0,
        "complexity": "low",
        "impact_reasoning": "Documentation only",
        "timestamp": datetime.utcnow()
    })
    
    print("✅ Test data seeded (3 commits, Total Value=150).")
    return user_id

def test_value_endpoint(user_id):
    print("\n🧪 Testing Value Endpoint...")
    print(f"[GET] /api/analytics/user/{user_id}/value")
    
    try:
        res = requests.get(f"{API_URL}/api/analytics/user/{user_id}/value")
        if res.status_code != 200:
            print(f"❌ Failed: {res.status_code} - {res.text}")
            return

        data = res.json()["data"]
        print(json.dumps(data, indent=2))
        
        # Verify Metrics
        # 3 commits * 2.5 hours = 7.5 hours
        # 7.5 hours * $100 = $750 Cost
        # Value = 95 + 50 + 5 = 150
        
        expected_cost = 750.0
        expected_value = 150.0
        
        if abs(data["total_cost"] - expected_cost) < 0.1:
            print("✅ Cost calculation correct.")
        else:
            print(f"❌ Cost mismatch. Expected {expected_cost}, got {data['total_cost']}")
            
        if abs(data["total_value_score"] - expected_value) < 0.1:
            print("✅ Value score aggregation correct.")
        else:
            print(f"❌ Value mismatch. Expected {expected_value}, got {data['total_value_score']}")
            
        if len(data["high_impact_commits"]) > 0:
            print("✅ High impact commits returned.")
        else:
            print("❌ No high impact commits found.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    try:
        user_id = setup_test_data()
        test_value_endpoint(user_id)
    except Exception as e:
        print(f"❌ Script Error: {e}")
