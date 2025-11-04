"""
Unit tests for health check endpoint
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import connect_to_mongo, close_mongo_connection


@pytest.fixture(scope="module")
async def setup_database():
    """Setup database connection for tests"""
    await connect_to_mongo()
    yield
    await close_mongo_connection()


@pytest.mark.asyncio
async def test_health_check_endpoint_returns_ok(setup_database):
    """Test health check endpoint returns ok status"""
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "timestamp" in data

    # If database is connected
    if data["status"] == "ok":
        assert data["database"] == "connected"
        assert data["database_name"] == "mmfrontend"
        assert "collections" in data
        assert "news_triggers" in data["collections"]
        assert "trigger_prompts" in data["collections"]
        assert "configurations" in data["collections"]


@pytest.mark.asyncio
async def test_health_check_includes_collection_counts(setup_database):
    """Test health check includes collection counts"""
    client = TestClient(app)
    response = client.get("/api/health")

    if response.status_code == 200:
        data = response.json()
        if data["status"] == "ok":
            collections = data["collections"]
            assert isinstance(collections["news_triggers"], int)
            assert isinstance(collections["trigger_prompts"], int)
            assert isinstance(collections["configurations"], int)
            assert collections["news_triggers"] > 0
            assert collections["trigger_prompts"] > 0
