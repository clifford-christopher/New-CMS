"""
FastAPI router for stock data endpoints from news_triggers collection
Returns OLD data from the 'data' node only
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..database import get_database
import logging

router = APIRouter(prefix="/api/stocks", tags=["stocks"])
logger = logging.getLogger(__name__)


@router.get("/{stock_id}/trigger-data")
async def get_stock_trigger_data(
    stock_id: str,
    trigger_name: Optional[str] = Query(None, description="Filter by specific trigger name")
):
    """
    Get OLD news trigger data for a specific stock from news_triggers collection.

    This endpoint searches by exact numeric stockid and optionally filters by trigger_name.
    Returns the most recent document sorted by 'date' field (descending).
    Returns ONLY the 'data' node content (OLD data), not the entire document.

    Args:
        stock_id: Numeric stock ID (e.g., "399834", "513374")
        trigger_name: Optional trigger name filter (e.g., "52wk_high")

    Returns:
        Data content from the 'data' node in news_triggers collection (OLD data)

    Raises:
        HTTPException: 400 if stock_id is not numeric, 404 if not found, 503 if database not connected, 500 on other errors
    """
    try:
        db = get_database()

        if db is None:
            raise HTTPException(status_code=503, detail="Database not connected")

        # Convert stock_id to integer for exact stockid matching
        try:
            stockid_int = int(stock_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid stock_id '{stock_id}'. Must be a numeric stockid."
            )

        # Build query - search by exact stockid only
        query = {"stockid": stockid_int}

        # Add trigger_name filter if provided
        if trigger_name:
            query["trigger_name"] = trigger_name

        # Find the most recent trigger data sorted by date field
        trigger_data = await db.news_triggers.find_one(
            query,
            sort=[("date", -1)]
        )

        if not trigger_data:
            raise HTTPException(
                status_code=404,
                detail=f"No trigger data found for stock '{stock_id}'" +
                       (f" with trigger '{trigger_name}'" if trigger_name else "")
            )

        # Remove MongoDB _id for JSON serialization
        trigger_data.pop("_id", None)

        # Return only the data node (OLD data from news_triggers)
        logger.info(f"Retrieved trigger data for stock '{stock_id}' (stockid: {trigger_data.get('stockid')})")
        return trigger_data.get("data")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve trigger data for stock '{stock_id}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve trigger data: {str(e)}")

