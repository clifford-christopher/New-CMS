"""
AI-Powered News CMS - FastAPI Application Entry Point

This is the main FastAPI application that serves the News CMS backend.
It includes:
- CORS configuration for frontend communication
- API route registration
- Middleware setup
- Application lifecycle management
"""

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
from .database import connect_to_mongo, close_mongo_connection
from .routers import health, triggers, stocks, data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application instance
app = FastAPI(
    title="AI-Powered News CMS API",
    description="Backend API for managing news generation configurations, triggers, and LLM integrations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
# TODO: Update origins with actual frontend URL in production
origins = [
    "http://localhost:3000",  # Next.js development server
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:3003",
    "http://localhost:3004",
    "http://localhost:3005",  # Frontend dev servers (multiple ports)
    "http://localhost:8000",  # Backend dev server (for testing)
    # Add production frontend URLs here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Application startup event handler."""
    logger.info("Starting AI-Powered News CMS Backend API")
    logger.info(f"Application started at: {datetime.utcnow().isoformat()}")
    # Initialize MongoDB connection
    await connect_to_mongo()
    # TODO: Load configuration from AWS Secrets Manager


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event handler."""
    logger.info("Shutting down AI-Powered News CMS Backend API")
    # Close MongoDB connection
    await close_mongo_connection()
    # TODO: Cleanup resources


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API status check.

    Returns:
        JSON response with API status and version
    """
    return JSONResponse(
        content={
            "message": "AI-Powered News CMS API",
            "version": "1.0.0",
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Register routers
app.include_router(health.router)
app.include_router(triggers.router)  # Story 1.4: Trigger Management Dashboard
app.include_router(stocks.router)  # Stock data from news_triggers collection
app.include_router(data.router)  # Story 2.4: Structured data generation

# TODO: Register additional routers (Story 2+)
# from app.routers import configuration, data, generation
# app.include_router(configuration.router, prefix="/api/config", tags=["Configuration"])
# app.include_router(data.router, prefix="/api/data", tags=["Data"])
# app.include_router(generation.router, prefix="/api/generation", tags=["Generation"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
