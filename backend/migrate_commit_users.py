
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

load_dotenv()

def migrate_commits():
    mongo_uri = os.getenv("MONGODB_URI")
    client = MongoClient(mongo_uri)
    db = client[os.getenv("DB_NAME", "coresight")]
    
    commits = list(db.commits.find())
    print(f"Found {len(commits)} commits to check")
    
    updated_count = 0
    
    for commit in commits:
        uid = commit.get("user_id")
        commit_id = commit.get("_id")
        updates = {}
        
        # Case 1: user_id is a string, convert to ObjectId
        if isinstance(uid, str):
            try:
                if ObjectId.is_valid(uid):
                    updates["user_id"] = ObjectId(uid)
                else:
                    print(f"Skipping invalid ObjectId string: {uid}")
            except Exception as e:
                print(f"Error converting user_id string for commit {commit_id}: {uid} - {e}")
        
        # Case 2: user_id is missing, try to find by email
        elif uid is None:
            email = commit.get("author_email")
            if email:
                user = db.users.find_one({"email": email})
                if user:
                    updates["user_id"] = user["_id"]
                    print(f"Matched commit {commit_id} to user {user.get('name')} ({email})")
        
        if updates:
            db.commits.update_one({"_id": commit_id}, {"$set": updates})
            updated_count += 1
            
    print(f"Migration complete. Updated {updated_count} commits.")

if __name__ == "__main__":
    migrate_commits()
