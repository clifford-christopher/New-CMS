"""
FastAPI router for structured data generation endpoints
Implements async job pattern for generating structured report sections
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
from bson import ObjectId
from datetime import datetime
import logging
import traceback

from ..database import get_database
from ..models.structured_data import (
    GenerateRequest,
    JobResponse,
    JobStatusResponse,
    SectionData
)
from ..services.structured_data_service import StructuredDataService

router = APIRouter(prefix="/api/data", tags=["data"])
logger = logging.getLogger(__name__)

# Initialize service
structured_service = StructuredDataService()


async def _process_generation_job(job_id: str, stock_id: str, sections: list[str]):
    """
    Background task to process structured data generation

    IMPORTANT: This function generates the COMPLETE report (all 14 sections)
    and stores ALL sections in the database. The frontend can then filter
    which sections to display based on user selection.

    Args:
        job_id: MongoDB ObjectId as string
        stock_id: Numeric stock ID
        sections: List of section IDs initially requested (for reference only)
    """
    db = get_database()
    if db is None:
        logger.error(f"Database not connected for job {job_id}")
        return

    try:
        # Update job status to running
        await db.structured_data_jobs.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": {"status": "running"}}
        )

        logger.info(f"Starting job {job_id} for stock {stock_id}")
        logger.info(f"Generating FULL report (all 14 sections), initially requested: {sections}")

        # Generate ALL 14 sections (pass all section IDs)
        all_section_ids = [str(i) for i in range(1, 15)]
        sections_data = await structured_service.generate_sections(stock_id, all_section_ids)

        # Convert SectionData objects to dict for MongoDB storage
        sections_dict = [section.model_dump() for section in sections_data]

        # Update job as completed with ALL sections
        await db.structured_data_jobs.update_one(
            {"_id": ObjectId(job_id)},
            {
                "$set": {
                    "status": "completed",
                    "all_sections_data": sections_dict,  # Store ALL sections
                    "completed_at": datetime.utcnow()
                }
            }
        )

        logger.info(f"Job {job_id} completed successfully with ALL {len(sections_data)} sections generated")

    except Exception as e:
        # Capture full exception details
        exception_type = type(e).__name__
        exception_msg = str(e) if str(e) else "(empty exception message)"
        error_message = f"{exception_type}: {exception_msg}"

        logger.error(f"Job {job_id} failed: {error_message}")
        logger.error(f"Traceback: {traceback.format_exc()}")

        # Ensure error message is never empty
        if not error_message or error_message == ": ":
            error_message = f"Unknown error occurred while processing job. Exception type: {exception_type}"

        # Update job as failed
        await db.structured_data_jobs.update_one(
            {"_id": ObjectId(job_id)},
            {
                "$set": {
                    "status": "failed",
                    "error": error_message,
                    "completed_at": datetime.utcnow()
                }
            }
        )


@router.post("/structured/generate", response_model=JobResponse)
async def generate_structured_data(
    request: GenerateRequest,
    background_tasks: BackgroundTasks
):
    """
    Create a new job to generate structured data sections

    This endpoint creates an async job and returns immediately with a job_id.
    Use GET /api/data/structured/jobs/{job_id} to poll the job status.

    Args:
        request: GenerateRequest containing stock_id and sections list

    Returns:
        JobResponse with job_id and status "pending"

    Raises:
        HTTPException: 400 for invalid input, 503 if database not connected, 500 on other errors
    """
    try:
        db = get_database()
        if db is None:
            raise HTTPException(status_code=503, detail="Database not connected")

        # Validate stock_id is numeric
        try:
            int(request.stock_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid stock_id '{request.stock_id}'. Must be numeric."
            )

        # Validate sections
        valid_sections = set(str(i) for i in range(1, 15))
        invalid_sections = set(request.sections) - valid_sections
        if invalid_sections:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid section IDs: {invalid_sections}. Must be between 1-14."
            )

        # Create job document
        job_doc = {
            "stock_id": request.stock_id,
            "requested_sections": request.sections,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "completed_at": None,
            "sections_data": None,
            "error": None
        }

        # Insert into database
        result = await db.structured_data_jobs.insert_one(job_doc)
        job_id = str(result.inserted_id)

        logger.info(f"Created job {job_id} for stock {request.stock_id}, sections: {request.sections}")

        # Add background task to process the job
        background_tasks.add_task(_process_generation_job, job_id, request.stock_id, request.sections)

        return JobResponse(
            job_id=job_id,
            status="pending",
            message="Job created successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create generation job: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")


@router.get("/structured/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get the status of a structured data generation job

    Poll this endpoint to check job progress and retrieve results when completed.

    Args:
        job_id: MongoDB ObjectId as string

    Returns:
        JobStatusResponse with current job status and data (if completed)

    Raises:
        HTTPException: 400 for invalid job_id, 404 if job not found, 503 if database not connected, 500 on other errors
    """
    try:
        db = get_database()
        if db is None:
            raise HTTPException(status_code=503, detail="Database not connected")

        # Validate job_id format
        try:
            object_id = ObjectId(job_id)
        except Exception:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid job_id format: '{job_id}'"
            )

        # Fetch job from database
        job = await db.structured_data_jobs.find_one({"_id": object_id})

        if not job:
            raise HTTPException(
                status_code=404,
                detail=f"Job not found: {job_id}"
            )

        # Build response
        response_data = {
            "job_id": job_id,
            "status": job["status"],
            "stock_id": job.get("stock_id"),
            "requested_sections": job.get("requested_sections"),
            "created_at": job.get("created_at"),
            "completed_at": job.get("completed_at")
        }

        # Add ALL sections_data if completed
        # The job stores all_sections_data (all 14 sections)
        # Frontend can filter which ones to display based on user selection
        if job["status"] == "completed":
            # Try new field name first (all_sections_data), fallback to old name (sections_data)
            sections_data = job.get("all_sections_data") or job.get("sections_data")
            if sections_data:
                response_data["sections_data"] = [
                    SectionData(**section) for section in sections_data
                ]

        # Add error if failed
        if job["status"] == "failed" and job.get("error"):
            response_data["error"] = job["error"]

        logger.info(f"Retrieved status for job {job_id}: {job['status']}")

        return JobStatusResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve job status for {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve job status: {str(e)}")
