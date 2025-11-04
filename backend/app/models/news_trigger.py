"""
Pydantic model for existing news_triggers collection
READ ONLY - matches existing schema with 684K documents
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any


class NewsTrigger(BaseModel):
    """Model for existing news_triggers collection (684K documents)"""
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")
    stockid: int
    comp_name: str
    sector: str
    industry: str
    date_time_trigger: str
    trigger_name: List[str]
    date: str
    status: int
    category: List[str]
    data: str  # Contains market analysis text
    types_of_trigger: List[str]
    result: Optional[str] = None
    result_quarter: Optional[int] = None
    upcoming_result: Optional[Any] = None
    scoreText: str  # "Buy", "Strong Buy", etc.
    score: int
    scoreTxtChngDate: str
    prevScoreText: str
    mcapsizerank: str  # "midcap", "largecap", etc.
    trigger_date: str
    mcap_grade: int
    stock_1y_return: str
    sensex_1y_return: str
    turn_arround: str
