"""
Migration script to create MongoDB indexes for News CMS Workflow collections.

Run with: python backend/scripts/create_workflow_indexes.py

Creates indexes for:
- trigger_prompts (extended with new fields)
- generation_history (NEW collection)
- prompt_versions (NEW collection)
- structured_data_jobs (NEW collection from Story 2.4)
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def create_indexes():
    """Create MongoDB indexes for News CMS Workflow collections."""
    # Connect to MongoDB
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    mongodb_db = os.getenv("MONGODB_DB_NAME", "mmfrontend")

    print(f"Connecting to MongoDB: {mongodb_uri}")
    print(f"Database: {mongodb_db}")

    client = AsyncIOMotorClient(mongodb_uri)
    db = client[mongodb_db]

    try:
        # Verify connection
        await client.admin.command('ping')
        print("✓ MongoDB connection successful\n")

        # ==========================================
        # 1. trigger_prompts collection
        # ==========================================
        print("Creating indexes for trigger_prompts collection...")

        # Unique index on trigger_name
        await db.trigger_prompts.create_index("trigger_name", unique=True)
        print("  ✓ trigger_name (unique)")

        # Index on isActive for quick filtering
        await db.trigger_prompts.create_index("isActive")
        print("  ✓ isActive")

        # ==========================================
        # 2. generation_history collection (NEW)
        # ==========================================
        print("\nCreating indexes for generation_history collection...")

        # Compound index for quick lookups by trigger + stockid + time
        await db.generation_history.create_index([
            ("trigger_name", 1),
            ("stockid", 1),
            ("timestamp", -1)
        ])
        print("  ✓ trigger_name + stockid + timestamp (compound)")

        # Index on prompt_type for analytics
        await db.generation_history.create_index("prompt_type")
        print("  ✓ prompt_type")

        # Index on timestamp for time-based queries
        await db.generation_history.create_index([("timestamp", -1)])
        print("  ✓ timestamp (descending)")

        # Index on status for filtering successes/failures
        await db.generation_history.create_index("status")
        print("  ✓ status")

        # ==========================================
        # 3. prompt_versions collection (NEW)
        # ==========================================
        print("\nCreating indexes for prompt_versions collection...")

        # Compound index on trigger_name + version
        await db.prompt_versions.create_index([
            ("trigger_name", 1),
            ("version", -1)
        ])
        print("  ✓ trigger_name + version (compound, descending)")

        # Index on published_at for time-based queries
        await db.prompt_versions.create_index([("published_at", -1)])
        print("  ✓ published_at (descending)")

        # ==========================================
        # 4. structured_data_jobs collection (NEW - Story 2.4)
        # ==========================================
        print("\nCreating indexes for structured_data_jobs collection...")

        # Unique index on job_id
        await db.structured_data_jobs.create_index("job_id", unique=True)
        print("  ✓ job_id (unique)")

        # TTL index on created_at (auto-delete after 24 hours)
        await db.structured_data_jobs.create_index(
            "created_at",
            expireAfterSeconds=86400  # 24 hours
        )
        print("  ✓ created_at (TTL: 24 hours)")

        # Index on status for filtering
        await db.structured_data_jobs.create_index("status")
        print("  ✓ status")

        print("\n" + "="*60)
        print("✓ All indexes created successfully!")
        print("="*60)

        # Display index information
        print("\nIndex Summary:")
        print(f"  trigger_prompts: {len(await db.trigger_prompts.index_information())} indexes")
        print(f"  generation_history: {len(await db.generation_history.index_information())} indexes")
        print(f"  prompt_versions: {len(await db.prompt_versions.index_information())} indexes")
        print(f"  structured_data_jobs: {len(await db.structured_data_jobs.index_information())} indexes")

    except Exception as e:
        print(f"\n✗ Error creating indexes: {e}")
        raise
    finally:
        client.close()
        print("\nMongoDB connection closed.")


if __name__ == "__main__":
    print("News CMS Workflow - Index Creation Script")
    print("="*60)
    asyncio.run(create_indexes())
