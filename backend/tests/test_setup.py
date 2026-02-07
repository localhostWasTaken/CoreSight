#!/usr/bin/env python3
"""
Test Script for CoreSight Jira Integration

This script helps you:
1. Create test users with different skill sets
2. Test the webhook processing
3. Verify the assignment algorithm
"""

import asyncio
import json
from motor.motor_asyncio import AsyncIOMotorClient
from database import DatabaseManager
from ai import generate_embedding
import os
from dotenv import load_dotenv

load_dotenv()


async def create_sample_users(db: DatabaseManager):
    """Create sample users with different skill profiles"""
    
    sample_users = [
        {
            "name": "Alice Johnson",
            "email": "alice@coresight.dev",
            "role": "employee",
            "hourly_rate": 75.0,
            "skills": ["Python", "FastAPI", "MongoDB", "React", "Docker", "REST API"],
            "github_username": "alicejohnson",
            "jira_account_id": "712020:alice001",
        },
        {
            "name": "Bob Smith",
            "email": "bob@coresight.dev",
            "role": "employee",
            "hourly_rate": 80.0,
            "skills": ["JavaScript", "Node.js", "React", "TypeScript", "GraphQL", "AWS"],
            "github_username": "bobsmith",
            "jira_account_id": "712020:bob002",
        },
        {
            "name": "Carol Martinez",
            "email": "carol@coresight.dev",
            "role": "employee",
            "hourly_rate": 85.0,
            "skills": ["Python", "Django", "PostgreSQL", "Kubernetes", "CI/CD", "Testing"],
            "github_username": "carolmart",
            "jira_account_id": "712020:carol003",
        },
        {
            "name": "David Lee",
            "email": "david@coresight.dev",
            "role": "employee",
            "hourly_rate": 70.0,
            "skills": ["Java", "Spring Boot", "MySQL", "Redis", "Microservices"],
            "github_username": "davidlee",
            "jira_account_id": "712020:david004",
        },
        {
            "name": "Emma Wilson",
            "email": "emma@coresight.dev",
            "role": "employee",
            "hourly_rate": 90.0,
            "skills": ["Python", "FastAPI", "MongoDB", "Machine Learning", "PyTorch", "Docker"],
            "github_username": "emmawilson",
            "jira_account_id": "712020:emma005",
        },
    ]
    
    print("\n" + "="*60)
    print("🚀 Creating Sample Users")
    print("="*60)
    
    created_users = []
    
    for user_data in sample_users:
        # Check if user already exists
        existing = await db.find_one("users", {"email": user_data["email"]})
        
        if existing:
            print(f"✅ User already exists: {user_data['name']}")
            created_users.append(existing)
            continue
        
        # Generate embeddings for skills
        skills_text = ", ".join(user_data["skills"])
        embeddings = generate_embedding(skills_text)
        
        user_doc = {
            **user_data,
            "work_profile_embeddings": embeddings,
            "project_metrics": {},
        }
        
        user_id = await db.insert_one("users", user_doc)
        print(f"✅ Created user: {user_data['name']} - Skills: {', '.join(user_data['skills'][:3])}...")
        
        user_doc["_id"] = user_id
        created_users.append(user_doc)
    
    print(f"\n📊 Total users in database: {len(created_users)}")
    return created_users


async def test_webhook_processing(db: DatabaseManager):
    """Test the webhook processing with a sample payload"""
    
    from services.jira_handlers import handle_issue_created
    
    print("\n" + "="*60)
    print("🧪 Testing Webhook Processing")
    print("="*60)
    
    # Sample webhook payload (based on actual Jira webhook)
    test_webhook = {
        "timestamp": 1770488555510,
        "webhookEvent": "jira:issue_created",
        "issue_event_type_name": "issue_created",
        "issue": {
            "id": "10999",
            "key": "TEST-999",
            "fields": {
                "summary": "Implement OAuth2 authentication for API endpoints",
                "description": "Add OAuth2 authentication to secure all API endpoints. This requires implementing JWT tokens, refresh tokens, and proper validation middleware using Python and FastAPI.",
                "project": {
                    "id": "10001",
                    "key": "TEST",
                    "name": "CoreSight Test Project"
                },
                "issuetype": {
                    "name": "Task"
                },
                "status": {
                    "name": "To Do"
                },
                "priority": {
                    "name": "High"
                },
                "customfield_10020": [
                    {
                        "id": 1,
                        "name": "Test Sprint 1",
                        "state": "active",
                        "startDate": "2026-02-08T00:00:00.000Z",
                        "endDate": "2026-02-22T00:00:00.000Z",
                        "goal": "Complete authentication module"
                    }
                ]
            }
        }
    }
    
    print("\n📝 Processing test issue: TEST-999")
    print("   Title: Implement OAuth2 authentication for API endpoints")
    
    result = await handle_issue_created(test_webhook, db)
    
    print("\n" + "="*60)
    print("📊 Processing Result")
    print("="*60)
    print(json.dumps(result, indent=2, default=str))
    
    return result


async def list_all_data(db: DatabaseManager):
    """List all data in the database"""
    
    print("\n" + "="*60)
    print("📊 Database Summary")
    print("="*60)
    
    # Count documents
    users = await db.find_many("users", {})
    projects = await db.find_many("projects", {})
    tasks = await db.find_many("tasks", {})
    sprints = await db.find_many("sprints", {})
    work_sessions = await db.find_many("work_sessions", {})
    
    print(f"\n📈 Statistics:")
    print(f"   Users: {len(users)}")
    print(f"   Projects: {len(projects)}")
    print(f"   Tasks: {len(tasks)}")
    print(f"   Sprints: {len(sprints)}")
    print(f"   Work Sessions: {len(work_sessions)}")
    
    if tasks:
        print(f"\n📋 Recent Tasks:")
        for task in tasks[-5:]:
            assignees = task.get("current_assignee_ids", [])
            status = "✅ Assigned" if assignees else "⏳ Unassigned"
            print(f"   {status} - {task.get('external_id')} - {task.get('title')[:50]}")


async def main():
    """Main test function"""
    
    print("\n" + "="*60)
    print("🎯 CoreSight Jira Integration Test Suite")
    print("="*60)
    
    # Connect to MongoDB
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DB_NAME", "coresight")
    
    print(f"\n🔌 Connecting to MongoDB...")
    print(f"   URL: {mongodb_url}")
    print(f"   Database: {db_name}")
    
    try:
        mongo_client = AsyncIOMotorClient(mongodb_url)
        db = mongo_client[db_name]
        db_manager = DatabaseManager(db)
        
        # Test connection
        await db.command("ping")
        print("✅ MongoDB connected successfully")
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return
    
    try:
        # Step 1: Create sample users
        users = await create_sample_users(db_manager)
        
        # Step 2: Test webhook processing
        result = await test_webhook_processing(db_manager)
        
        # Step 3: List all data
        await list_all_data(db_manager)
        
        print("\n" + "="*60)
        print("✅ Test Suite Completed Successfully!")
        print("="*60)
        print("\n💡 Next Steps:")
        print("   1. Start the API: python main.py")
        print("   2. Visit: http://localhost:8080/docs")
        print("   3. Configure Jira webhook to point to your API")
        print("   4. Create issues in Jira and watch the magic! ✨")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
