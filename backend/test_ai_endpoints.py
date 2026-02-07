"""
Test Script for AI-Powered Issue and Commit Endpoints
Usage: python test_ai_endpoints.py
"""

import requests
import json
from datetime import datetime

import os
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def test_health_check():
    print_section("Testing Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"Response Text: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {BASE_URL}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_test_user():
    print_section("Creating Test User")
    
    user_data = {
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "role": "employee",
        "hourly_rate": 75.0,
        "skills": ["Python", "FastAPI", "MongoDB", "JWT", "Security", "Docker"],
        "github_username": "alicejohnson",
        "jira_account_id": "alice123"
    }
    
    print(f"User Data: {json.dumps(user_data, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/api/users", json=user_data)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.json()

def test_issue_endpoint_new():
    print_section("Testing POST /api/issues - New Issue")
    
    issue_data = {
        "title": "Implement user authentication with JWT",
        "description": "Need to add JWT-based authentication to the API with role-based access control. Should support login, logout, token refresh, and secure password hashing. Need to integrate with MongoDB for user storage.",
        "priority": "high",
        "source": "api",
        "external_id": "PROJ-101"
    }
    
    print(f"Issue Data: {json.dumps(issue_data, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/api/issues", json=issue_data)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.json()

def test_issue_endpoint_duplicate():
    print_section("Testing POST /api/issues - Duplicate Detection")
    
    # Submit a similar issue to test duplicate detection
    issue_data = {
        "title": "Add JWT authentication",
        "description": "We need JWT authentication for the API endpoints with user login and token validation",
        "priority": "medium",
        "source": "api"
    }
    
    print(f"Issue Data: {json.dumps(issue_data, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/api/issues", json=issue_data)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.json()

def test_issue_no_match():
    print_section("Testing POST /api/issues - No Matching Developer (Job Posting)")
    
    issue_data = {
        "title": "Build quantum computing simulator",
        "description": "Develop a quantum circuit simulator using Qiskit and implement Shor's algorithm for integer factorization",
        "priority": "high",
        "source": "api",
        "external_id": "PROJ-102"
    }
    
    print(f"Issue Data: {json.dumps(issue_data, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/api/issues", json=issue_data)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.json()

def test_commit_endpoint():
    print_section("Testing POST /api/commits")
    
    commit_data = {
        "commit_hash": "a1b2c3d4e5f6789",
        "commit_message": "Add MongoDB connection pooling and retry logic",
        "diff": """diff --git a/database.py b/database.py
index 1234567..abcdefg 100644
--- a/database.py
+++ b/database.py
@@ -1,10 +1,25 @@
 from motor.motor_asyncio import AsyncIOMotorClient
+from pymongo.errors import ConnectionFailure
+import asyncio

 class DatabaseManager:
     def __init__(self, db_url):
-        self.client = AsyncIOMotorClient(db_url)
+        self.client = AsyncIOMotorClient(
+            db_url,
+            maxPoolSize=50,
+            minPoolSize=10,
+            serverSelectionTimeoutMS=5000
+        )
         self.db = self.client.coresight
     
+    async def connect_with_retry(self, max_retries=3):
+        for attempt in range(max_retries):
+            try:
+                await self.client.admin.command('ping')
+                print("Connected to MongoDB")
+                return True
+            except ConnectionFailure:
+                if attempt < max_retries - 1:
+                    await asyncio.sleep(2 ** attempt)
+        return False
""",
        "author_email": "alice@example.com",
        "author_name": "Alice Johnson",
        "repository": "coresight-backend",
        "branch": "main",
        "files_changed": 1,
        "lines_added": 20,
        "lines_deleted": 2
    }
    
    print(f"Commit Data (truncated): {json.dumps({k: v if k != 'diff' else v[:100] + '...' for k, v in commit_data.items()}, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/api/commits", json=commit_data)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.json()

def test_commit_with_profile_update():
    print_section("Testing POST /api/commits - Profile Evolution")
    
    commit_data = {
        "commit_hash": "xyz789abc123",
        "commit_message": "Implement Redis caching layer for sessions",
        "diff": """diff --git a/cache.py b/cache.py
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/cache.py
@@ -0,0 +1,45 @@
+import redis.asyncio as redis
+from typing import Optional
+import json
+
+class CacheManager:
+    def __init__(self, redis_url: str):
+        self.redis = redis.from_url(redis_url)
+    
+    async def get(self, key: str) -> Optional[dict]:
+        value = await self.redis.get(key)
+        return json.loads(value) if value else None
+    
+    async def set(self, key: str, value: dict, ttl: int = 3600):
+        await self.redis.setex(key, ttl, json.dumps(value))
""",
        "author_email": "alice@example.com",
        "author_name": "Alice Johnson",
        "repository": "coresight-backend",
        "branch": "feature/redis-cache",
        "files_changed": 1,
        "lines_added": 45,
        "lines_deleted": 0
    }
    
    print(f"Commit Data (truncated): {json.dumps({k: v if k != 'diff' else v[:100] + '...' for k, v in commit_data.items()}, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/api/commits", json=commit_data)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.json()

def list_users():
    print_section("Listing All Users")
    
    response = requests.get(f"{BASE_URL}/api/users")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.json()

def main():
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║         AI-Powered Issue & Commit Endpoints - Test Suite         ║
║                          CoreSight API                            ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Test health check
        if not test_health_check():
            print("\n❌ Server is not responding. Please ensure the server is running.")
            print(f"   Expected URL: {BASE_URL}")
            print("\n   Run in a separate terminal:")
            print("   cd backend")
            print("   python main.py")
            print("\n   Or check if server is running on a different port.")
            print("   Default port is now 8000 (changed from 8080 to avoid conflicts)")
            return
        
        print("\n✅ Server is running!\n")
        
        # Create test user
        input("Press Enter to create a test user...")
        user_result = create_test_user()
        
        # Test Issue Endpoint - New Issue
        input("\nPress Enter to test Issue endpoint (new issue)...")
        issue_result_1 = test_issue_endpoint_new()
        
        # Test Issue Endpoint - Duplicate
        input("\nPress Enter to test Issue endpoint (duplicate detection)...")
        issue_result_2 = test_issue_endpoint_duplicate()
        
        # Test Issue Endpoint - No Match
        input("\nPress Enter to test Issue endpoint (no matching developer)...")
        issue_result_3 = test_issue_no_match()
        
        # Test Commit Endpoint
        input("\nPress Enter to test Commit endpoint...")
        commit_result_1 = test_commit_endpoint()
        
        # Test Commit with Profile Update
        input("\nPress Enter to test Commit endpoint (profile evolution)...")
        commit_result_2 = test_commit_with_profile_update()
        
        # List all users
        input("\nPress Enter to list all users (to see profile updates)...")
        users = list_users()
        
        print_section("Test Suite Completed")
        print("✅ All tests executed successfully!")
        print("\nYou can now:")
        print(f"1. Open {BASE_URL}/docs for interactive API documentation")
        print("2. Check MongoDB to see the created documents")
        print("3. Review the detailed responses above")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error: Cannot connect to the API server.")
        print(f"   Please ensure the server is running on {BASE_URL}")
        print("   Run: python main.py")
    except KeyboardInterrupt:
        print("\n\n⚠️  Test suite interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
