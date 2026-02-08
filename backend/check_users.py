
import asyncio
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

async def check_users():
    mongo_uri = os.getenv("MONGODB_URI")
    client = MongoClient(mongo_uri)
    db = client[os.getenv("DB_NAME", "coresight")]
    
    users = list(db.users.find().limit(5))
    print(f"Found {len(users)} sample users")
    
    for user in users:
        print(f"User: {user.get('name')}, Email: {user.get('email')}, ID: {user.get('_id')}")

if __name__ == "__main__":
    asyncio.run(check_users())
