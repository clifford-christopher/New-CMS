"""
Quick script to check MongoDB mmfrontend database contents
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient


async def check_database():
    """Check what's in the mmfrontend database."""
    mongodb_uri = "mongodb://localhost:27017"
    db_name = "mmfrontend"

    print(f"Connecting to: {mongodb_uri}")
    print(f"Database: {db_name}\n")

    client = AsyncIOMotorClient(mongodb_uri)
    db = client[db_name]

    try:
        # Verify connection
        await client.admin.command('ping')
        print("✅ MongoDB connection successful\n")

        # List all collections
        collections = await db.list_collection_names()
        print(f"Collections in '{db_name}' database:")
        print("=" * 60)

        if not collections:
            print("⚠️  No collections found!")
            return

        for collection_name in collections:
            count = await db[collection_name].count_documents({})
            print(f"  📁 {collection_name}: {count:,} documents")

        print("\n" + "=" * 60)

        # Check trigger_prompts specifically
        if "trigger_prompts" in collections:
            print("\n📋 Sample trigger_prompts documents:")
            print("=" * 60)
            cursor = db.trigger_prompts.find().limit(5)
            docs = await cursor.to_list(length=5)

            if docs:
                for i, doc in enumerate(docs, 1):
                    print(f"\n{i}. Trigger: {doc.get('trigger_name', 'NO NAME')}")
                    print(f"   Fields: {list(doc.keys())}")
                    print(f"   isActive: {doc.get('isActive', 'N/A')}")
            else:
                print("⚠️  No documents in trigger_prompts collection!")
        else:
            print("\n⚠️  'trigger_prompts' collection does NOT exist!")

        # Check news_triggers (for OLD data)
        if "news_triggers" in collections:
            print("\n📰 Sample news_triggers document:")
            print("=" * 60)
            cursor = db.news_triggers.find().limit(1)
            docs = await cursor.to_list(length=1)

            if docs:
                doc = docs[0]
                print(f"Trigger: {doc.get('trigger_name', 'NO NAME')}")
                print(f"Stock ID: {doc.get('stockid', 'N/A')}")
                print(f"Fields: {list(doc.keys())}")
                print(f"Has 'data' node: {'data' in doc}")
            else:
                print("⚠️  No documents in news_triggers collection!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise
    finally:
        client.close()
        print("\n✅ Connection closed.")


if __name__ == "__main__":
    print("="*60)
    print("MongoDB Database Check - mmfrontend")
    print("="*60 + "\n")
    asyncio.run(check_database())
