"""
Unit tests for MongoDB database connection
"""
import pytest
from app.database import connect_to_mongo, close_mongo_connection, get_database
import os


@pytest.mark.asyncio
async def test_mongodb_connection_success():
    """Test successful MongoDB connection to mmfrontend"""
    await connect_to_mongo()
    db = get_database()
    assert db is not None
    assert db.name == "mmfrontend"
    await close_mongo_connection()


@pytest.mark.asyncio
async def test_get_database_returns_instance():
    """Test get_database returns valid database instance"""
    await connect_to_mongo()
    db = get_database()
    assert db is not None
    # Verify we can list collections
    collections = await db.list_collection_names()
    assert isinstance(collections, list)
    await close_mongo_connection()


@pytest.mark.asyncio
async def test_mongodb_ping():
    """Test MongoDB ping command works"""
    await connect_to_mongo()
    db = get_database()
    result = await db.command('ping')
    assert result.get('ok') == 1.0
    await close_mongo_connection()


@pytest.mark.asyncio
async def test_existing_collections_accessible():
    """Test that existing collections are accessible"""
    await connect_to_mongo()
    db = get_database()

    # Verify news_triggers collection exists
    news_triggers_count = await db.news_triggers.count_documents({})
    assert news_triggers_count > 0  # Should have 684K+ documents

    # Verify trigger_prompts collection exists
    trigger_prompts_count = await db.trigger_prompts.count_documents({})
    assert trigger_prompts_count > 0  # Should have 54 documents

    await close_mongo_connection()
