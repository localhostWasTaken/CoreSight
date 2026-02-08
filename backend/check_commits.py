
import asyncio
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

async def check_commits():
    mongo_uri = os.getenv("MONGODB_URI")
    client = MongoClient(mongo_uri)
    db = client[os.getenv("DB_NAME", "coresight")]
    
    commits = list(db.commits.find().limit(5))
    print(f"Found {len(commits)} sample commits")
    
    for commit in commits:
        uid = commit.get("user_id")
        print(f"Commit: {commit.get('commit_hash')}, User ID: {uid}, Type: {type(uid)}")

if __name__ == "__main__":
    asyncio.run(check_commits())
