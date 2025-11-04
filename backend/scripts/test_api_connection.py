"""
Test script to verify the backend will connect to the correct database.
This simulates what happens when the backend starts up.

Run with: python backend/scripts/test_api_connection.py
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables (simulating main.py)
load_dotenv()


async def test_connection():
    """Test MongoDB connection with loaded environment variables."""
    print("="*60)
    print("Testing Backend Database Connection")
    print("="*60 + "\n")

    # Get environment variables
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DB_NAME", "news_cms")

    print(f"Environment Variables:")
    print(f"   MONGODB_URI: {mongodb_uri}")
    print(f"   MONGODB_DB_NAME: {db_name}")
    print()

    # Connect to MongoDB
    print(f"Connecting to database: {db_name}...")
    client = AsyncIOMotorClient(mongodb_uri)
    db = client[db_name]

    try:
        # Test connection
        await client.admin.command('ping')
        print(f"[OK] Successfully connected to MongoDB: {db_name}\n")

        # Check trigger_prompts collection
        count = await db.trigger_prompts.count_documents({})
        print(f"trigger_prompts collection:")
        print(f"   Total documents: {count}")

        # Check how many have isActive field (migrated)
        migrated_count = await db.trigger_prompts.count_documents({"isActive": {"$exists": True}})
        print(f"   Migrated documents: {migrated_count}")

        # Sample a few documents
        if count > 0:
            print(f"\nSample trigger names:")
            cursor = db.trigger_prompts.find({}).limit(5)
            docs = await cursor.to_list(length=5)
            for i, doc in enumerate(docs, 1):
                trigger_name = doc.get('trigger_name', 'N/A')
                is_active = doc.get('isActive', 'N/A')
                print(f"   {i}. {trigger_name} (isActive: {is_active})")

        print("\n" + "="*60)
        if db_name == "mmfrontend" and count == 54 and migrated_count == 54:
            print("[OK] VERIFICATION PASSED!")
            print("   - Connected to correct database (mmfrontend)")
            print("   - Found 54 trigger documents")
            print("   - All documents migrated")
            print("   - Backend should work correctly after restart")
        else:
            print("[WARNING] VERIFICATION ISSUES:")
            if db_name != "mmfrontend":
                print(f"   - Wrong database: {db_name} (should be mmfrontend)")
            if count != 54:
                print(f"   - Wrong document count: {count} (should be 54)")
            if migrated_count != count:
                print(f"   - Not all documents migrated: {migrated_count}/{count}")
        print("="*60)

    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(test_connection())
