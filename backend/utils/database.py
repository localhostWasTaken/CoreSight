from bson import ObjectId
from typing import Optional, Dict, Any

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

class DatabaseManager:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    @property
    def client(self):
        """Access to the underlying MongoDB client for transactions."""
        return self.db.client
    
    def close(self):
        if hasattr(self.db.client, "close"):
            self.db.client.close()
        elif hasattr(self.db.client, "disconnect"):
            self.db.client.disconnect()
    
    def get_collection(self, collection_name: str) -> AsyncIOMotorCollection:
        return self.db[collection_name]
    
    async def create_indexes(self, collection_name: str, indexes: list):
        """Create indexes for a collection."""
        collection = self.get_collection(collection_name)
        if indexes:
            await collection.create_indexes(indexes)

    async def find_one(self, collection_name: str, filter_dict: Dict[str, Any], session=None) -> Optional[Dict[str, Any]]:
        collection = self.get_collection(collection_name)
        return await collection.find_one(filter_dict, session=session)
    
    async def find_many(self, collection_name: str, filter_dict: Dict[str, Any], session=None) -> list[Dict[str, Any]]:
        collection = self.get_collection(collection_name)
        cursor = collection.find(filter_dict, session=session)
        return await cursor.to_list(length=None)
    
    async def insert_one(self, collection_name: str, document: Dict[str, Any], session=None) -> ObjectId:
        collection = self.get_collection(collection_name)
        result = await collection.insert_one(document, session=session)
        return result.inserted_id
    
    async def update_one(self, collection_name: str, filter_dict: Dict[str, Any], update_dict: Dict[str, Any], session=None) -> bool:
        collection = self.get_collection(collection_name)
        result = await collection.update_one(filter_dict, {"$set": update_dict}, session=session)
        return result.modified_count > 0
    
    async def upsert_one(self, collection_name: str, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> bool:
        collection = self.get_collection(collection_name)
        result = await collection.update_one(filter_dict, {"$set": update_dict}, upsert=True)
        return result.matched_count > 0

    async def update_one_raw(self, collection_name: str, filter_dict: Dict[str, Any], update_dict: Dict[str, Any], session=None) -> bool:
        collection = self.get_collection(collection_name)
        result = await collection.update_one(filter_dict, update_dict, session=session)
        return result.modified_count > 0
    
    async def delete_one(self, collection_name: str, filter_dict: Dict[str, Any], session=None) -> bool:
        collection = self.get_collection(collection_name)
        result = await collection.delete_one(filter_dict, session=session)
        return result.deleted_count > 0