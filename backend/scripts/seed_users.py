"""
Quick User Seeding Script for CoreSight
Creates 3 specialized users via API endpoint (embeddings generated automatically)

Usage: python seed_users.py
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Specialized user profiles
USERS = [
    {
        "name": "Sarah Chen",
        "email": "sarah.chen@example.com",
        "role": "employee",
        "hourly_rate": 85.0,
        "skills": [
            "React",
            "TypeScript",
            "OAuth 2.0",
            "JavaScript",
            "Frontend Development",
            "Authentication",
            "JWT",
            "REST API"
        ],
        "github_username": "sarachen",
        "jira_account_id": "sarah_001",
        "profile_description": "Senior Frontend Developer with 5+ years of experience specializing in React and TypeScript. Expert in implementing OAuth 2.0 authentication flows, JWT token management, and secure frontend authentication patterns. Has successfully integrated Google, GitHub, Microsoft, and custom OAuth providers into enterprise applications. Strong background in building secure, user-friendly authentication experiences with multi-factor authentication and session management."
    },
    {
        "name": "Marcus Johnson",
        "email": "marcus.johnson@example.com",
        "role": "employee",
        "hourly_rate": 95.0,
        "skills": [
            "Python",
            "FastAPI",
            "Payment Gateway Integration",
            "Stripe",
            "PayPal",
            "Security",
            "API Development",
            "PostgreSQL",
            "Redis",
            "Microservices"
        ],
        "github_username": "marcusj",
        "jira_account_id": "marcus_002",
        "profile_description": "Backend Engineer with extensive experience in payment processing systems and financial technology. Specialized in integrating payment gateways including Stripe, PayPal, Square, and custom payment processors. Expert in PCI compliance, secure payment handling, transaction processing, refund management, and webhook handling. Strong knowledge of financial regulations, fraud detection, and building reliable payment APIs. Has built payment systems handling millions in transactions with 99.99% uptime."
    },
    {
        "name": "Alex Kim",
        "email": "alex.kim@example.com",
        "role": "employee",
        "hourly_rate": 110.0,
        "skills": [
            "Python",
            "FastAPI",
            "React",
            "TypeScript",
            "Machine Learning",
            "TensorFlow",
            "OpenAI API",
            "LLM Integration",
            "Vector Databases",
            "Full Stack Development",
            "MongoDB",
            "Docker",
            "AI/ML",
            "Natural Language Processing"
        ],
        "github_username": "alexkim",
        "jira_account_id": "alex_003",
        "profile_description": "Full Stack AI Engineer with deep expertise in building production AI applications. Specialized in integrating Large Language Models (LLMs), vector databases, and semantic search into full-stack applications. Has built multiple AI-powered features including chatbots, recommendation engines, content generation systems, and intelligent search. Expert in prompt engineering, RAG (Retrieval-Augmented Generation) architectures, embeddings, and ML model deployment. Combines strong full-stack development skills with practical AI/ML implementation experience to create intelligent, scalable applications."
    }
]


def create_user(user_data):
    """Create a user via API endpoint"""
    print(f"\n{'='*60}")
    print(f"Creating User: {user_data['name']}")
    print(f"{'='*60}")
    print(f"Role: {', '.join(user_data['skills'][:3])} specialist")
    print(f"Email: {user_data['email']}")
    print(f"Rate: ${user_data['hourly_rate']}/hour")
    print(f"Skills: {', '.join(user_data['skills'])}")
    
    # The API endpoint will generate embeddings automatically
    api_payload = {
        "name": user_data["name"],
        "email": user_data["email"],
        "role": user_data["role"],
        "hourly_rate": user_data["hourly_rate"],
        "skills": user_data["skills"],
        "github_username": user_data["github_username"],
        "jira_account_id": user_data["jira_account_id"]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/users",
            json=api_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"\n✅ User created successfully!")
            print(f"   User ID: {result['user_id']}")
            print(f"   Embeddings: Generated automatically via API")
            return result
        else:
            print(f"\n❌ Failed to create user: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Cannot connect to API server at {BASE_URL}")
        print(f"   Please ensure the server is running:")
        print(f"   cd backend && python main.py")
        return None
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


def check_server():
    """Check if API server is running"""
    print("🔍 Checking API server...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ API server is running at {BASE_URL}")
            return True
        else:
            print(f"⚠️  Server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {BASE_URL}")
        print(f"\nPlease start the server first:")
        print(f"   cd backend")
        print(f"   python main.py")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False


def list_users():
    """List all created users"""
    print(f"\n{'='*60}")
    print("Fetching All Users...")
    print(f"{'='*60}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/users")
        if response.status_code == 200:
            data = response.json()
            users = data.get("users", [])
            print(f"\n📊 Total Users: {data.get('count', 0)}")
            
            for user in users:
                print(f"\n   • {user['name']} ({user['email']})")
                print(f"     Skills: {', '.join(user['skills'][:5])}")
                if len(user['skills']) > 5:
                    print(f"             + {len(user['skills']) - 5} more...")
            
            return users
        else:
            print(f"❌ Failed to fetch users: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error fetching users: {e}")
        return []


def main():
    print("\n" + "="*60)
    print("  CoreSight User Seeding Script")
    print("  Creates 3 Specialized Users via API")
    print("="*60)
    print("\n🎯 User Profiles:")
    print("   1. Sarah Chen - Frontend + OAuth Expert")
    print("   2. Marcus Johnson - Backend + Payment Gateway Expert")
    print("   3. Alex Kim - Full Stack + AI Apps Expert")
    print()
    
    # Check if server is running
    if not check_server():
        return
    
    print()
    
    # Ask for confirmation
    response = input("Create these users? (yes/no): ").strip().lower()
    
    if response != "yes":
        print("\n❌ Cancelled")
        return
    
    # Create users
    created_users = []
    for user_data in USERS:
        result = create_user(user_data)
        if result:
            created_users.append(result)
    
    # Summary
    print(f"\n{'='*60}")
    print("  Summary")
    print(f"{'='*60}")
    print(f"\n✅ Created {len(created_users)}/{len(USERS)} users")
    print(f"   • All embeddings generated automatically via API")
    print(f"   • Users ready for task assignment")
    
    # List all users
    list_users()
    
    print(f"\n💡 Next Steps:")
    print(f"   • Test issue creation: python test_ai_endpoints.py")
    print(f"   • View users: curl {BASE_URL}/api/users")
    print(f"   • API docs: {BASE_URL}/docs")
    print()


if __name__ == "__main__":
    main()
