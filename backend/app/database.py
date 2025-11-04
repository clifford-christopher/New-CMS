from motor.motor_asyncio import AsyncIOMotorClient
import os
from typing import Optional

# Global MongoDB client
_mongo_client: Optional[AsyncIOMotorClient] = None
_database = None

def get_mongo_client() -> AsyncIOMotorClient:
    """Get or create MongoDB client"""
    global _mongo_client

    if _mongo_client is None:
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        _mongo_client = AsyncIOMotorClient(mongodb_uri)

    return _mongo_client

def get_database():
    """Get MongoDB database instance"""
    global _database

    if _database is None:
        client = get_mongo_client()
        db_name = os.getenv("MONGODB_DB_NAME", "news_cms")
        _database = client[db_name]

    return _database

async def connect_to_mongo():
    """Initialize MongoDB connection (startup event)"""
    global _mongo_client, _database

    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    _mongo_client = AsyncIOMotorClient(mongodb_uri)

    db_name = os.getenv("MONGODB_DB_NAME", "news_cms")
    _database = _mongo_client[db_name]

    # Test connection
    try:
        await _mongo_client.admin.command('ping')
        print(f"[OK] Connected to MongoDB: {db_name}")
    except Exception as e:
        print(f"[ERROR] Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close MongoDB connection"""
    global _mongo_client, _database

    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None
        _database = None
