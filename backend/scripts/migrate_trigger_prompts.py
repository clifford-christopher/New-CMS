"""
Migration script to add News CMS Workflow fields to existing trigger_prompts documents.

Adds default values for new fields:
- isActive: false (legacy mode by default)
- version: 1
- created_at, updated_at: current timestamp
- published_at, published_by: null

Preserves all existing fields for backward compatibility.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv()


async def migrate_triggers():
    """Add News CMS Workflow fields to existing trigger_prompts documents."""
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DB_NAME", "mmfrontend")

    print(f"Connecting to: {mongodb_uri}")
    print(f"Database: {db_name}\n")

    client = AsyncIOMotorClient(mongodb_uri)
    db = client[db_name]

    try:
        await client.admin.command('ping')
        print("✅ MongoDB connection successful\n")

        # Get all trigger_prompts documents
        count = await db.trigger_prompts.count_documents({})
        print(f"Found {count} trigger_prompts documents\n")

        # Check how many already have isActive field
        has_active = await db.trigger_prompts.count_documents({"isActive": {"$exists": True}})
        needs_migration = count - has_active

        print(f"  Already migrated: {has_active}")
        print(f"  Needs migration: {needs_migration}\n")

        if needs_migration == 0:
            print("✅ All documents already migrated!")
            return

        # Migrate documents without isActive field
        print("Starting migration...")
        print("="*60)

        now = datetime.now(timezone.utc)

        # Update all documents that don't have isActive field
        result = await db.trigger_prompts.update_many(
            {"isActive": {"$exists": False}},
            {
                "$set": {
                    "isActive": False,  # Default to legacy mode
                    "version": 1,
                    "created_at": now,
                    "updated_at": now,
                    "published_at": None,
                    "published_by": None
                }
            }
        )

        print(f"✅ Migration complete!")
        print(f"   Modified {result.modified_count} documents")
        print("="*60)

        # Verify migration
        print("\n📋 Sample migrated documents:")
        print("="*60)
        cursor = db.trigger_prompts.find({"isActive": {"$exists": True}}).limit(3)
        docs = await cursor.to_list(length=3)

        for i, doc in enumerate(docs, 1):
            print(f"\n{i}. Trigger: {doc.get('trigger_name')}")
            print(f"   isActive: {doc.get('isActive')}")
            print(f"   version: {doc.get('version')}")
            print(f"   created_at: {doc.get('created_at')}")

        print("\n" + "="*60)
        print("✅ Migration verification complete!")
        print("\nNOTE: All triggers are set to isActive=false (legacy mode)")
        print("Use the CMS UI to configure individual triggers for the new workflow.")

    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        raise
    finally:
        client.close()
        print("\n✅ Connection closed.")


if __name__ == "__main__":
    print("="*60)
    print("News CMS Workflow - Trigger Prompts Migration")
    print("="*60 + "\n")
    asyncio.run(migrate_triggers())
