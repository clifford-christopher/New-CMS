"""
Initialize NEW collections with indexes in mmfrontend database.
Creates: configurations, users, audit_log collections.
Existing collections (news_triggers, trigger_prompts) are left untouched.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os


async def init_collections():
    """Initialize NEW collections with appropriate indexes"""
    try:
        # Connect to MongoDB
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        db_name = os.getenv("MONGODB_DB_NAME", "mmfrontend")

        print(f"Connecting to MongoDB at {mongodb_uri}{db_name}")
        client = AsyncIOMotorClient(mongodb_uri)
        db = client[db_name]

        # Verify connection
        await client.admin.command('ping')
        print("[PASS] Connected to MongoDB successfully")

        # Get existing collections
        existing_collections = await db.list_collection_names()
        print(f"[INFO] Existing collections: {existing_collections}")

        # Create indexes for configurations collection
        print("\n[INFO] Creating indexes for 'configurations' collection...")
        await db.configurations.create_index([("trigger_key", 1), ("is_active", 1)], name="trigger_key_is_active")
        await db.configurations.create_index([("version", -1)], name="version_desc")
        await db.configurations.create_index("trigger_key", name="trigger_key")
        print("[PASS] Configurations indexes created")

        # Create indexes for users collection
        print("\n[INFO] Creating indexes for 'users' collection...")
        await db.users.create_index("username", unique=True, name="username_unique")
        await db.users.create_index("email", unique=True, name="email_unique")
        print("[PASS] Users indexes created")

        # Create indexes for audit_log collection
        print("\n[INFO] Creating indexes for 'audit_log' collection...")
        await db.audit_log.create_index([("trigger_key", 1), ("timestamp", -1)], name="trigger_key_timestamp")
        await db.audit_log.create_index([("user_id", 1)], name="user_id")
        print("[PASS] Audit log indexes created")

        # Verify NEW collections were created
        updated_collections = await db.list_collection_names()
        new_collections = set(updated_collections) - set(existing_collections)

        print(f"\n[INFO] Updated collections list: {updated_collections}")
        if new_collections:
            print(f"[PASS] NEW collections created: {new_collections}")
        else:
            print("[INFO] No new collections created (may already exist)")

        # List all indexes for verification
        print("\n[INFO] Verifying indexes...")
        for collection_name in ["configurations", "users", "audit_log"]:
            if collection_name in updated_collections:
                indexes = await db[collection_name].index_information()
                print(f"  {collection_name}: {list(indexes.keys())}")

        client.close()
        print("\n[PASS] Initialization complete!")
        return True

    except Exception as e:
        print(f"\n[FAIL] Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(init_collections())
    exit(0 if success else 1)
