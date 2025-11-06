"""
News Generation Service

Simplified service for generating news using LLM providers.
- Fetches prompt templates from MongoDB
- Substitutes placeholders with configured data
- Calls selected LLM provider
- Saves generation history
- Returns normalized response
"""

import logging
import re
from typing import Dict, Any, Optional
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient

from ..database import get_database
from ..models.generation_history import GenerationHistory
from ..llm_providers import ProviderRegistry, GenerationResponse
from ..config import get_llm_api_keys, get_llm_config

logger = logging.getLogger(__name__)


class NewsGenerationService:
    """
    Service for generating news articles using LLM providers
    """

    def __init__(self):
        """Initialize news generation service"""
        self.db = None  # Will be set when database is available
        self.api_keys = get_llm_api_keys()
        self.llm_config = get_llm_config()

    async def generate_news(
        self,
        trigger_name: str,
        stock_id: str,
        prompt_type: str,
        model_id: str,
        structured_data: Dict[str, Any],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        session_id: Optional[str] = None,
        prompt_template: Optional[str] = None  # Add prompt_template parameter
    ) -> GenerationResponse:
        """
        Generate news article using selected LLM model

        Args:
            trigger_name: Trigger identifier (e.g., "52wk_high")
            stock_id: Stock symbol (e.g., "AAPL")
            prompt_type: Prompt type ("paid", "unpaid", or "crawler")
            model_id: Model identifier (e.g., "gpt-4o", "claude-sonnet-4-5")
            structured_data: Configured data from DataContext (OLD/NEW/OLD_NEW)
            temperature: Temperature for generation (default from config)
            max_tokens: Max tokens to generate (default from config)
            session_id: Optional session ID for grouping
            prompt_template: Optional in-memory prompt template (bypasses DB lookup)

        Returns:
            GenerationResponse with generated text and metadata

        Raises:
            ValueError: If prompt template not found or model not available
            Exception: If generation fails
        """
        try:
            # Get database connection
            db = get_database()

            # 1. Get prompt template (from parameter or MongoDB)
            if prompt_template:
                # Use provided in-memory template from Monaco editor
                logger.info(f"Using provided prompt template (length: {len(prompt_template)})")
                template = prompt_template
            else:
                # Fetch from MongoDB
                template = await self._get_prompt_template(db, trigger_name, prompt_type)
                if not template:
                    raise ValueError(f"Prompt template not found for trigger '{trigger_name}' type '{prompt_type}'")

            # 2. Substitute placeholders with structured data
            final_prompt = self._substitute_placeholders(template, structured_data)

            # 3. Get LLM provider
            provider = await self._get_provider(model_id)

            # 4. Generate news
            temp = temperature if temperature is not None else self.llm_config["default_temperature"]
            max_tok = max_tokens if max_tokens is not None else self.llm_config["default_max_tokens"]

            response = await provider.generate(
                prompt=final_prompt,
                model=model_id,
                temperature=temp,
                max_tokens=max_tok
            )

            # 5. Save to generation history
            await self._save_generation_history(
                db=db,
                trigger_name=trigger_name,
                stock_id=stock_id,
                prompt_type=prompt_type,
                data_mode=structured_data.get("data_mode", "UNKNOWN"),
                model_id=model_id,
                prompt_template=template,  # Save the actual template used (not the parameter)
                final_prompt=final_prompt,
                response=response,
                session_id=session_id
            )

            logger.info(
                f"Generated news | Trigger: {trigger_name} | Stock: {stock_id} | "
                f"Type: {prompt_type} | Model: {model_id} | Cost: ${response.cost:.6f}"
            )

            return response

        except Exception as e:
            logger.error(f"News generation failed: {e}", exc_info=True)
            raise

    async def _get_prompt_template(
        self,
        db: AsyncIOMotorClient,
        trigger_name: str,
        prompt_type: str
    ) -> Optional[str]:
        """
        Fetch prompt template from MongoDB

        Args:
            db: Database connection
            trigger_name: Trigger name
            prompt_type: Prompt type

        Returns:
            Prompt template string or None
        """
        try:
            # Query trigger_prompts collection
            collection = db["trigger_prompts"]

            # Find the latest draft for this trigger
            result = await collection.find_one(
                {"trigger_name": trigger_name},
                sort=[("version", -1)]
            )

            if not result:
                logger.warning(f"No prompt found for trigger: {trigger_name}")
                return None

            # Extract prompt for the specific type
            prompts = result.get("prompts", {})
            prompt_data = prompts.get(prompt_type, {})

            # Get template (handle both new and legacy formats)
            # Legacy format: prompts.paid = "string"
            # New format: prompts.paid = {"template": "string", "character_count": 123}
            if isinstance(prompt_data, str):
                template = prompt_data  # Legacy format
            elif isinstance(prompt_data, dict):
                template = prompt_data.get("template", "")  # New format
            else:
                template = ""

            if not template:
                logger.warning(f"Empty template for trigger: {trigger_name}, type: {prompt_type}")
                return None

            logger.debug(f"Loaded prompt template for {trigger_name}/{prompt_type} (length: {len(template)})")

            return template

        except Exception as e:
            logger.error(f"Failed to fetch prompt template: {e}")
            raise

    def _substitute_placeholders(
        self,
        template: str,
        structured_data: Dict[str, Any]
    ) -> str:
        """
        Substitute placeholders in template with actual data

        Supports:
        - {{section_name}} - Section placeholders
        - {data.field} - Data field placeholders
        - {{stock_id}} - Stock symbol

        Args:
            template: Prompt template with placeholders
            structured_data: Data dictionary

        Returns:
            Final prompt with substitutions
        """
        final_prompt = template

        # Substitute stock_id if present
        stock_id = structured_data.get("stock_id", "")
        if stock_id:
            final_prompt = final_prompt.replace("{{stock_id}}", stock_id)

        # Substitute section placeholders: {{section_name}}
        # Uses case-insensitive matching to handle variations like {{OLD Data}} vs {{old_data}}
        sections = structured_data.get("sections", {})
        for section_name, section_content in sections.items():
            # Convert section content to string if it's a dict
            if isinstance(section_content, dict):
                section_text = str(section_content)
            else:
                section_text = str(section_content)

            # Create exact match placeholder
            placeholder = f"{{{{{section_name}}}}}"
            final_prompt = final_prompt.replace(placeholder, section_text)

            # Also try case-insensitive replacement for variations
            # Find all {{...}} patterns and check if they match case-insensitively
            pattern = r'\{\{([^}]+)\}\}'
            matches = re.finditer(pattern, final_prompt)
            for match in matches:
                placeholder_name = match.group(1).strip()
                if placeholder_name.lower() == section_name.lower():
                    # Replace this occurrence with section content
                    final_prompt = final_prompt.replace(match.group(0), section_text)

        # Substitute data field placeholders: {data.field}
        # Extract data from nested structure
        data_fields = structured_data.get("data", {})
        if data_fields:
            # Find all {data.field} patterns
            pattern = r'\{data\.([a-zA-Z0-9_\.]+)\}'
            matches = re.findall(pattern, final_prompt)

            for field_path in matches:
                # Navigate nested structure
                value = self._get_nested_value(data_fields, field_path)
                if value is not None:
                    placeholder = f"{{data.{field_path}}}"
                    final_prompt = final_prompt.replace(placeholder, str(value))

        return final_prompt

    def _get_nested_value(self, data: Dict, path: str) -> Any:
        """
        Get value from nested dictionary using dot notation

        Args:
            data: Data dictionary
            path: Dot-separated path (e.g., "earnings.summary")

        Returns:
            Value at path or None
        """
        keys = path.split('.')
        value = data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None

        return value

    async def _get_provider(self, model_id: str):
        """
        Get LLM provider instance for model

        Args:
            model_id: Model identifier

        Returns:
            Provider instance

        Raises:
            ValueError: If model not found or API key missing
        """
        # Determine provider from model_id
        if "gpt" in model_id or "openai" in model_id:
            provider_name = "openai"
        elif "claude" in model_id or "anthropic" in model_id:
            provider_name = "anthropic"
        elif "gemini" in model_id or "google" in model_id:
            provider_name = "gemini"
        else:
            raise ValueError(f"Unknown provider for model: {model_id}")

        # Get API key
        api_key = self.api_keys.get(provider_name)

        if not api_key:
            raise ValueError(f"API key not found for provider: {provider_name}")

        # Get provider from registry
        provider = ProviderRegistry.get_provider(
            model_id=model_id,
            api_key=api_key,
            config={
                "timeout": self.llm_config["timeout"],
                "max_retries": self.llm_config["max_retries"]
            }
        )

        return provider

    async def _save_generation_history(
        self,
        db: AsyncIOMotorClient,
        trigger_name: str,
        stock_id: str,
        prompt_type: str,
        data_mode: str,
        model_id: str,
        prompt_template: str,
        final_prompt: str,
        response: GenerationResponse,
        session_id: Optional[str] = None
    ) -> None:
        """
        Save generation to history collection

        Args:
            db: Database connection
            trigger_name: Trigger name
            stock_id: Stock symbol
            prompt_type: Prompt type
            data_mode: Data mode (OLD/NEW/OLD_NEW)
            model_id: Model used
            prompt_template: Original template
            final_prompt: Final prompt after substitution
            response: Generation response
            session_id: Optional session ID
        """
        try:
            # Truncate prompts for storage (1000 chars)
            prompt_template_truncated = prompt_template[:1000]
            final_prompt_truncated = final_prompt[:1000]

            # Create history record
            history_record = GenerationHistory(
                trigger_name=trigger_name,
                stock_id=stock_id,
                prompt_type=prompt_type,
                data_mode=data_mode,
                model=model_id,
                provider=response.provider,
                prompt_template=prompt_template_truncated,
                final_prompt=final_prompt_truncated,
                generated_text=response.generated_text,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                total_tokens=response.total_tokens,
                cost=response.cost,
                latency=response.latency,
                timestamp=response.timestamp,
                session_id=session_id,
                error=response.error,
                temperature=response.temperature,
                max_tokens=response.max_tokens,
                finish_reason=response.finish_reason
            )

            # Insert into MongoDB
            collection = db["generation_history"]
            await collection.insert_one(history_record.model_dump())

            logger.debug(f"Saved generation history for {trigger_name}/{stock_id}/{prompt_type}")

        except Exception as e:
            logger.error(f"Failed to save generation history: {e}")
            # Don't raise - history save failure shouldn't break generation

    async def get_generation_history(
        self,
        trigger_name: Optional[str] = None,
        stock_id: Optional[str] = None,
        prompt_type: Optional[str] = None,
        session_id: Optional[str] = None,
        limit: int = 10,
        skip: int = 0
    ) -> Dict[str, Any]:
        """
        Retrieve generation history with filters

        Args:
            trigger_name: Filter by trigger
            stock_id: Filter by stock
            prompt_type: Filter by prompt type
            session_id: Filter by session
            limit: Maximum records to return
            skip: Number of records to skip (pagination)

        Returns:
            Dict with generations and total count
        """
        try:
            db = get_database()
            collection = db["generation_history"]

            # Build filter query
            query = {}
            if trigger_name:
                query["trigger_name"] = trigger_name
            if stock_id:
                query["stock_id"] = stock_id
            if prompt_type:
                query["prompt_type"] = prompt_type
            if session_id:
                query["session_id"] = session_id

            # Get total count
            total = await collection.count_documents(query)

            # Fetch records
            cursor = collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
            records = await cursor.to_list(length=limit)

            # Convert to GenerationHistory objects
            generations = [GenerationHistory(**record) for record in records]

            return {
                "generations": generations,
                "total": total,
                "page": (skip // limit) + 1,
                "page_size": limit
            }

        except Exception as e:
            logger.error(f"Failed to retrieve generation history: {e}")
            raise
