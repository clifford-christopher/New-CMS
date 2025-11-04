"""
Health check endpoint for MongoDB connection status.
"""
from fastapi import APIRouter
from datetime import datetime
from ..database import get_database
import logging

router = APIRouter(prefix="/api", tags=["health"])
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify MongoDB connection status.
    Returns status, database connection state, collection counts, and timestamp.

    Returns:
        dict: Health status with database connection info and collection counts
    """
    try:
        db = get_database()

        if db is None:
            return {
                "status": "error",
                "database": "disconnected",
                "timestamp": datetime.utcnow().isoformat()
            }

        # Ping database to verify connection
        await db.command('ping')

        # Get collection counts
        news_triggers_count = await db.news_triggers.count_documents({})
        trigger_prompts_count = await db.trigger_prompts.count_documents({})

        # Check if configurations collection exists
        collections = await db.list_collection_names()
        configurations_count = await db.configurations.count_documents({}) if "configurations" in collections else 0

        return {
            "status": "ok",
            "database": "connected",
            "database_name": "mmfrontend",
            "collections": {
                "news_triggers": news_triggers_count,
                "trigger_prompts": trigger_prompts_count,
                "configurations": configurations_count
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "error",
            "database": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
