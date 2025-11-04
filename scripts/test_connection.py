"""
Test MongoDB connection to mmfrontend database
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test_connection():
    """Test connection to existing mmfrontend database"""
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient("mongodb://localhost:27017/")
        db = client["mmfrontend"]

        # Verify connection
        await client.admin.command('ping')
        print("[PASS] Successfully connected to MongoDB")

        # Get collection names
        collections = await db.list_collection_names()
        print(f"[PASS] Collections found: {collections}")

        # Verify news_triggers collection
        news_triggers_count = await db.news_triggers.count_documents({})
        print(f"[PASS] news_triggers collection: {news_triggers_count:,} documents")

        # Verify trigger_prompts collection
        trigger_prompts_count = await db.trigger_prompts.count_documents({})
        print(f"[PASS] trigger_prompts collection: {trigger_prompts_count} documents")

        # Get sample document from each collection
        sample_trigger = await db.news_triggers.find_one()
        if sample_trigger:
            print(f"[PASS] Sample trigger fields: {list(sample_trigger.keys())[:10]}...")

        sample_prompt = await db.trigger_prompts.find_one()
        if sample_prompt:
            print(f"[PASS] Sample prompt fields: {list(sample_prompt.keys())}")

        client.close()
        print("\n[PASS] Connection test PASSED")
        return True

    except Exception as e:
        print(f"[FAIL] Connection test FAILED: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())
