"""
Generation API Router

Endpoints for:
- Generating news with LLM models
- Retrieving generation history
- Listing available models
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ..services.news_generation_service import NewsGenerationService
from ..llm_providers import GenerationResponse, ProviderRegistry
from ..models.generation_history import GenerationHistoryResponse

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class GenerateNewsRequest(BaseModel):
    """Request model for generating news"""
    trigger_name: str = Field(..., description="Trigger identifier")
    stock_id: str = Field(..., description="Stock symbol")
    prompt_type: str = Field(..., description="Prompt type: paid, unpaid, or crawler")
    model_id: str = Field(default="gpt-4o", description="Model identifier")
    structured_data: Dict[str, Any] = Field(..., description="Configured data from DataContext")
    temperature: Optional[float] = Field(None, description="Temperature (0.0-1.0)")
    max_tokens: Optional[int] = Field(None, description="Max tokens to generate")
    session_id: Optional[str] = Field(None, description="Optional session ID for grouping")
    prompt_template: Optional[str] = Field(None, description="Optional in-memory prompt template (bypasses DB lookup)")

    class Config:
        json_schema_extra = {
            "example": {
                "trigger_name": "52wk_high",
                "stock_id": "AAPL",
                "prompt_type": "paid",
                "model_id": "gpt-4o",
                "structured_data": {
                    "stock_id": "AAPL",
                    "data_mode": "OLD_NEW",
                    "sections": {
                        "section_1": "Apple Inc. reached new highs...",
                        "section_2": "Market analysis shows..."
                    },
                    "data": {
                        "price": 175.50,
                        "change": 2.5
                    }
                },
                "temperature": 0.7,
                "max_tokens": 500,
                "session_id": "test-session-123"
            }
        }


class ModelInfo(BaseModel):
    """Model information"""
    model_id: str
    display_name: str
    provider: str
    description: str
    pricing: Dict[str, float]


class ModelsListResponse(BaseModel):
    """Response model for models list"""
    models: List[ModelInfo]
    total: int


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/news/generate", response_model=GenerationResponse, tags=["Generation"])
async def generate_news(request: GenerateNewsRequest):
    """
    Generate news article using selected LLM model

    This endpoint:
    1. Fetches the prompt template for the trigger and prompt type
    2. Substitutes placeholders with the provided structured data
    3. Calls the selected LLM provider
    4. Saves the generation to history
    5. Returns the generated text with metadata

    **Cost**: Varies by model. Check /api/news/models for pricing.

    **Example**:
    ```json
    {
        "trigger_name": "52wk_high",
        "stock_id": "AAPL",
        "prompt_type": "paid",
        "model_id": "gpt-4o",
        "structured_data": {
            "stock_id": "AAPL",
            "data_mode": "OLD_NEW",
            "sections": {...}
        }
    }
    ```
    """
    try:
        service = NewsGenerationService()

        response = await service.generate_news(
            trigger_name=request.trigger_name,
            stock_id=request.stock_id,
            prompt_type=request.prompt_type,
            model_id=request.model_id,
            structured_data=request.structured_data,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            session_id=request.session_id,
            prompt_template=request.prompt_template  # Pass in-memory prompt template
        )

        return response

    except ValueError as e:
        logger.error(f"Validation error in generate_news: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Error in generate_news: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.get("/news/history", response_model=GenerationHistoryResponse, tags=["Generation"])
async def get_generation_history(
    trigger_name: Optional[str] = Query(None, description="Filter by trigger name"),
    stock_id: Optional[str] = Query(None, description="Filter by stock symbol"),
    prompt_type: Optional[str] = Query(None, description="Filter by prompt type"),
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Records per page")
):
    """
    Retrieve generation history with optional filters

    Returns a paginated list of generation records.

    **Filters**:
    - `trigger_name`: Filter by trigger (e.g., "52wk_high")
    - `stock_id`: Filter by stock symbol (e.g., "AAPL")
    - `prompt_type`: Filter by type (paid, unpaid, crawler)
    - `session_id`: Filter by session ID

    **Pagination**:
    - `page`: Page number (starts at 1)
    - `page_size`: Records per page (1-100)
    """
    try:
        service = NewsGenerationService()

        skip = (page - 1) * page_size

        result = await service.get_generation_history(
            trigger_name=trigger_name,
            stock_id=stock_id,
            prompt_type=prompt_type,
            session_id=session_id,
            limit=page_size,
            skip=skip
        )

        return GenerationHistoryResponse(**result)

    except Exception as e:
        logger.error(f"Error in get_generation_history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")


@router.get("/news/models", response_model=ModelsListResponse, tags=["Generation"])
async def list_available_models():
    """
    List all available LLM models with pricing

    Returns information about all available models including:
    - Model ID
    - Display name
    - Provider (openai, anthropic, gemini)
    - Description
    - Pricing (per 1M tokens)

    **Example Response**:
    ```json
    {
        "models": [
            {
                "model_id": "gpt-4o",
                "display_name": "GPT-4o",
                "provider": "openai",
                "description": "Most capable OpenAI model",
                "pricing": {
                    "input": 2.50,
                    "output": 10.00
                }
            }
        ],
        "total": 15
    }
    ```
    """
    try:
        models = ProviderRegistry.list_available_models()

        # Convert to response format
        model_infos = []
        for model in models:
            model_infos.append(ModelInfo(
                model_id=model["model_id"],
                display_name=model["display_name"],
                provider=model["provider"],
                description=model["description"],
                pricing=model["pricing"]
            ))

        return ModelsListResponse(
            models=model_infos,
            total=len(model_infos)
        )

    except Exception as e:
        logger.error(f"Error in list_available_models: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")


@router.get("/news/models/{provider}", response_model=ModelsListResponse, tags=["Generation"])
async def list_models_by_provider(provider: str):
    """
    List models for a specific provider

    **Providers**:
    - `openai`: OpenAI models (GPT-4o, GPT-4o-mini, etc.)
    - `anthropic`: Anthropic models (Claude Sonnet, Haiku, etc.)
    - `gemini`: Google Gemini models (2.0-flash, 2.0-flash-lite)

    **Example**: `/api/news/models/openai`
    """
    try:
        models = ProviderRegistry.list_models_by_provider(provider.lower())

        if not models:
            raise HTTPException(
                status_code=404,
                detail=f"No models found for provider: {provider}"
            )

        # Convert to response format
        model_infos = []
        for model in models:
            model_infos.append(ModelInfo(
                model_id=model["model_id"],
                display_name=model["display_name"],
                provider=model["provider"],
                description=model["description"],
                pricing=model["pricing"]
            ))

        return ModelsListResponse(
            models=model_infos,
            total=len(model_infos)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in list_models_by_provider: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")
