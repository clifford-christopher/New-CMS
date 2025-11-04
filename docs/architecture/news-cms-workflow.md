# News CMS Workflow Feature - Technical Architecture

## Overview

The News CMS Workflow Feature extends the News CMS platform to support configuration-driven news generation using structured financial data from Python report generators. This architecture document details the technical design for integrating `generate_full_report.py`, implementing multi-mode data handling (OLD/NEW/OLD_NEW), managing multi-type prompts (paid/unpaid/crawler), and maintaining backward compatibility with existing news generation systems.

## Core Architecture Principles

1. **stockid-Specific Data Access**: All data operations require both `trigger_name` AND `stockid` parameters
2. **No Caching for Dynamic Data**: Structured data changes during market hours (9:15 AM - 3:30 PM IST), always generate fresh
3. **Cache Only Static Configs**: Prompt templates, model configurations, user metadata
4. **Backward Compatibility**: `isActive` flag determines routing between legacy (3-prompt) and new (single HTML prompt) generation methods
5. **Pre-population First**: Always display existing OLD data and prompts before configuration
6. **Shared Configuration**: Data config, section management, model selection shared across all prompt types
7. **Independent Prompts**: Separate templates per type (paid/unpaid/crawler) accessible via tabs

## System Components

### Backend Services

#### 1. StructuredDataService

**Purpose**: Generate fresh structured reports from Python script for specific stockid.

**Location**: `backend/app/services/structured_data_service.py`

**Key Methods**:
```python
class StructuredDataService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.script_path = Path(__file__).parent.parent.parent / "structured_report_builder" / "generate_full_report.py"

    async def generate_report(
        self,
        stockid: int,
        sections: List[int] = None,  # Defaults to all 14
        section_order: List[int] = None,
        exchange: int = 0
    ) -> Dict[str, Any]:
        """
        Generates structured report for stockid via subprocess execution.

        Args:
            stockid: Stock ID to generate report for
            sections: List of section numbers to include (1-14)
            section_order: Order to arrange sections
            exchange: Exchange code (default 0)

        Returns:
            {
                "stockid": int,
                "sections": {
                    "1": {"title": str, "content": str},
                    "2": {"title": str, "content": str},
                    ...
                },
                "section_order": List[int],
                "metadata": {
                    "generated_at": datetime,
                    "script_execution_time": float,
                    "data_source": "generate_full_report.py"
                }
            }
        """
        # Execute Python script via subprocess
        process = await asyncio.create_subprocess_exec(
            "python",
            str(self.script_path),
            str(stockid),
            str(exchange),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=60.0  # 60 second timeout
        )

        if process.returncode != 0:
            raise ScriptExecutionError(f"Script failed: {stderr.decode()}")

        # Parse output (14 sections separated by 80 "=" characters)
        raw_output = stdout.decode()
        parsed_sections = self._parse_sections(raw_output)

        # Filter and reorder sections
        if sections:
            parsed_sections = {k: v for k, v in parsed_sections.items() if int(k) in sections}
        if section_order:
            # Reorder dictionary based on section_order
            parsed_sections = {str(k): parsed_sections[str(k)] for k in section_order}

        return {
            "stockid": stockid,
            "sections": parsed_sections,
            "section_order": section_order or list(range(1, 15)),
            "metadata": {
                "generated_at": datetime.utcnow(),
                "script_execution_time": ...,  # Calculate from process timing
                "data_source": "generate_full_report.py"
            }
        }

    def _parse_sections(self, raw_output: str) -> Dict[str, Dict[str, str]]:
        """Parse 14 sections from script output."""
        # Split by 80 "=" characters
        sections = {}
        section_texts = raw_output.split("=" * 80)

        for idx, section_text in enumerate(section_texts, start=1):
            if idx > 14:
                break
            # Extract title and content
            lines = section_text.strip().split("\n")
            title = lines[0].strip() if lines else f"Section {idx}"
            content = "\n".join(lines[1:]) if len(lines) > 1 else ""

            sections[str(idx)] = {
                "title": title,
                "content": content
            }

        return sections
```

**API Endpoint**:
- `POST /api/data/structured/generate`
- Request Body:
  ```json
  {
    "stockid": 513374,
    "sections": [1, 2, 3, 5, 7, 9, 12],
    "section_order": [1, 2, 3, 5, 7, 9, 12],
    "exchange": 0
  }
  ```
- Response: See `generate_report` return type above
- **No caching**: Always generates fresh data
- Timeout: 60 seconds (configurable)

#### 2. DataMergeService

**Purpose**: Merge OLD (trigger) data with NEW (structured) data based on data_mode.

**Location**: `backend/app/services/data_merge_service.py`

**Key Methods**:
```python
class DataMergeService:
    def __init__(self, db: AsyncIOMotorDatabase, structured_service: StructuredDataService):
        self.db = db
        self.structured_service = structured_service

    async def merge_data(
        self,
        trigger_name: str,
        stockid: int,
        data_mode: str,  # "old" | "new" | "old_new"
        sections: List[int] = None,
        section_order: List[int] = None
    ) -> Dict[str, Any]:
        """
        Merge OLD and NEW data based on data_mode.

        Args:
            trigger_name: Trigger identifier
            stockid: Stock ID to fetch/generate data for
            data_mode: "old" (trigger data only), "new" (structured only), "old_new" (both)
            sections: Section numbers to include if generating NEW data
            section_order: Order for NEW sections

        Returns:
            {
                "data_mode": str,
                "stockid": int,
                "merged_data": Dict,  # Structure depends on data_mode
                "metadata": {
                    "old_data_source": str,
                    "new_data_source": str,
                    "merged_at": datetime
                }
            }
        """
        if data_mode == "old":
            # Return only OLD data from news_triggers
            trigger = await self.db.news_triggers.find_one({
                "trigger_name": [trigger_name],
                "stockid": stockid
            })
            if not trigger:
                raise DataNotFoundError(f"No data for trigger '{trigger_name}' with stockid {stockid}")

            return {
                "data_mode": "old",
                "stockid": stockid,
                "merged_data": trigger.get("data", {}),
                "metadata": {
                    "old_data_source": "news_triggers",
                    "new_data_source": None,
                    "merged_at": datetime.utcnow()
                }
            }

        elif data_mode == "new":
            # Generate and return only NEW data
            structured_data = await self.structured_service.generate_report(
                stockid, sections, section_order
            )

            return {
                "data_mode": "new",
                "stockid": stockid,
                "merged_data": structured_data["sections"],
                "metadata": {
                    "old_data_source": None,
                    "new_data_source": "generate_full_report.py",
                    "merged_at": datetime.utcnow()
                }
            }

        elif data_mode == "old_new":
            # Fetch OLD and generate NEW, then merge
            trigger = await self.db.news_triggers.find_one({
                "trigger_name": [trigger_name],
                "stockid": stockid
            })

            old_data = trigger.get("data", {}) if trigger else {}
            if not trigger:
                logger.warning(f"No OLD data for trigger '{trigger_name}' with stockid {stockid}, proceeding with NEW only")

            structured_data = await self.structured_service.generate_report(
                stockid, sections, section_order
            )

            # Merge: OLD data + NEW sections
            merged = {
                **old_data,  # Spread OLD data fields
                "structured_sections": structured_data["sections"]  # Add NEW sections
            }

            return {
                "data_mode": "old_new",
                "stockid": stockid,
                "merged_data": merged,
                "metadata": {
                    "old_data_source": "news_triggers" if trigger else None,
                    "new_data_source": "generate_full_report.py",
                    "merged_at": datetime.utcnow()
                }
            }

        else:
            raise ValidationError(f"Invalid data_mode: {data_mode}. Must be 'old', 'new', or 'old_new'")
```

**API Endpoint**:
- `POST /api/data/merge`
- Request Body:
  ```json
  {
    "trigger_name": "earnings_result",
    "stockid": 513374,
    "data_mode": "old_new",
    "sections": [1, 2, 3],
    "section_order": [1, 2, 3]
  }
  ```
- **No caching**: Always fetches/generates fresh
- Used by preview and publish flows

#### 3. NewsGenerationService

**Purpose**: Adaptive news generation with backward compatibility via `isActive` flag.

**Location**: `backend/app/services/news_generation_service.py`

**Key Classes**:

```python
from abc import ABC, abstractmethod

class NewsGenerator(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate(
        self,
        stock_data: str,
        prompt: str,
        model_config: Dict
    ) -> str:
        """Generate HTML news article."""
        pass

class ClaudeNewsGenerator(NewsGenerator):
    """Claude Sonnet 4.5 implementation."""

    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"

    async def generate(
        self,
        stock_data: str,
        prompt: str,
        model_config: Dict
    ) -> str:
        """
        Generate HTML article using Claude.

        Args:
            stock_data: Merged data (OLD/NEW/OLD_NEW) as formatted string
            prompt: Prompt template with placeholders already substituted
            model_config: {"temperature": float, "max_tokens": int}

        Returns:
            Full HTML string with <title>, <meta description>, <article>
        """
        response = self.client.messages.create(
            model=self.model,
            max_tokens=model_config.get("max_tokens", 20000),
            temperature=model_config.get("temperature", 0.7),
            messages=[
                {"role": "user", "content": f"{prompt}\n\nStock Data:\n{stock_data}"}
            ]
        )

        return response.content[0].text

class OpenAINewsGenerator(NewsGenerator):
    """OpenAI GPT-4o implementation."""

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o"

    async def generate(
        self,
        stock_data: str,
        prompt: str,
        model_config: Dict
    ) -> str:
        """Generate HTML article using OpenAI."""
        response = await self.client.chat.completions.create(
            model=self.model,
            max_tokens=model_config.get("max_tokens", 20000),
            temperature=model_config.get("temperature", 0.7),
            messages=[
                {"role": "user", "content": f"{prompt}\n\nStock Data:\n{stock_data}"}
            ]
        )

        return response.choices[0].message.content

class NewsGenerationService:
    """Main service for adaptive news generation."""

    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        data_merge_service: DataMergeService,
        claude_api_key: str,
        openai_api_key: str
    ):
        self.db = db
        self.data_merge_service = data_merge_service
        self.generators = {
            "claude": ClaudeNewsGenerator(claude_api_key),
            "openai": OpenAINewsGenerator(openai_api_key)
        }

    async def generate_news(
        self,
        trigger_name: str,
        stockid: int,
        prompt_type: str  # "paid" | "unpaid" | "crawler"
    ) -> Dict[str, Any]:
        """
        Generate news with adaptive routing based on isActive flag.

        Returns:
            {
                "title": str,
                "summary": str,
                "article": str,
                "metadata": {
                    "method": "new" | "legacy",
                    "model": str,
                    "tokens_used": int,
                    "generation_time": float,
                    "cost": float,
                    "prompt_type": str
                }
            }
        """
        # Check for active configuration
        config = await self.db.trigger_prompts.find_one({
            "trigger_name": trigger_name,
            "isActive": True
        })

        if not config or not config.get("isActive"):
            # Legacy method: Existing 3-prompt generation
            logger.info(f"Using LEGACY method for trigger '{trigger_name}' (isActive=false or not found)")
            return await self._legacy_generation(trigger_name, stockid, prompt_type)

        # New method: Single HTML prompt
        logger.info(f"Using NEW method for trigger '{trigger_name}' (isActive=true)")

        # 1. Merge data based on config
        merged_data = await self.data_merge_service.merge_data(
            trigger_name,
            stockid,
            config["data_config"]["data_mode"],
            config["data_config"].get("sections"),
            config["data_config"].get("section_order")
        )

        # 2. Format data for prompt
        formatted_data = self._format_data_for_prompt(merged_data["merged_data"])

        # 3. Get prompt template and substitute placeholders
        prompt_template = config["prompts"][prompt_type]
        final_prompt = self._substitute_placeholders(prompt_template, merged_data["merged_data"])

        # 4. Generate HTML via selected provider
        provider = config["model_config"]["provider"]
        generator = self.generators[provider]

        start_time = time.time()
        html_output = await generator.generate(
            formatted_data,
            final_prompt,
            config["model_config"]
        )
        generation_time = time.time() - start_time

        # 5. Extract title, summary, article from HTML
        extracted = self._extract_components(html_output)

        # 6. Calculate cost and metadata
        # (Placeholder - implement token counting and cost calculation)
        tokens_used = len(html_output) // 4  # Rough estimate
        cost = self._calculate_cost(provider, tokens_used)

        return {
            **extracted,
            "metadata": {
                "method": "new",
                "model": config["model_config"]["model"],
                "tokens_used": tokens_used,
                "generation_time": generation_time,
                "cost": cost,
                "prompt_type": prompt_type
            }
        }

    async def _legacy_generation(
        self,
        trigger_name: str,
        stockid: int,
        prompt_type: str
    ) -> Dict[str, Any]:
        """
        Call existing generate_news_og.py script (3-prompt method).

        This maintains backward compatibility for triggers without active configs.
        """
        # Execute existing script via subprocess or direct import
        # (Implementation depends on existing script structure)
        pass

    def _extract_components(self, html_content: str) -> Dict[str, str]:
        """
        Extract title, summary, article from HTML using regex.

        Expected HTML structure:
        <html>
          <head>
            <title>Article Title</title>
            <meta name="description" content="Summary text">
          </head>
          <body>
            <article>Full article content</article>
          </body>
        </html>
        """
        import re

        # Extract title
        title_match = re.search(r'<title>(.*?)</title>', html_content, re.DOTALL)
        title = title_match.group(1).strip() if title_match else "Untitled"

        # Extract summary from meta description
        summary_match = re.search(r'<meta\s+name="description"\s+content="(.*?)"', html_content, re.DOTALL)
        summary = summary_match.group(1).strip() if summary_match else ""

        # Extract article body
        article_match = re.search(r'<article>(.*?)</article>', html_content, re.DOTALL)
        article = article_match.group(1).strip() if article_match else html_content

        return {
            "title": title,
            "summary": summary,
            "article": article
        }

    def _format_data_for_prompt(self, data: Dict) -> str:
        """Format merged data as string for LLM input."""
        # Convert dict to formatted string (JSON or custom format)
        return json.dumps(data, indent=2)

    def _substitute_placeholders(self, template: str, data: Dict) -> str:
        """Replace placeholders like {{section_1}} with actual data."""
        # Simple string replacement (can be enhanced with Jinja2)
        result = template
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
        return result

    def _calculate_cost(self, provider: str, tokens: int) -> float:
        """Calculate cost based on provider pricing."""
        # Placeholder pricing (update with actual rates)
        pricing = {
            "claude": 0.000003,  # per token
            "openai": 0.000002
        }
        return tokens * pricing.get(provider, 0)
```

**API Endpoint**:
- `POST /api/news/generate`
- Request Body:
  ```json
  {
    "trigger_name": "earnings_result",
    "stockid": 513374,
    "prompt_type": "paid"
  }
  ```
- Response: See `generate_news` return type

### API Endpoints Summary

| Method | Endpoint | Purpose | Caching |
|--------|----------|---------|---------|
| GET | `/api/triggers/{trigger_name}/data?stockid={stockid}` | Fetch OLD data from news_triggers | No |
| GET | `/api/triggers/{trigger_name}/prompts` | Fetch existing prompts for pre-population | Yes (5 min TTL) |
| POST | `/api/data/structured/generate` | Generate NEW structured data via Python script | No |
| POST | `/api/data/merge` | Merge OLD + NEW data based on data_mode | No |
| POST | `/api/config/save` | Save draft configuration (isActive=false) | No |
| POST | `/api/config/publish` | Publish configuration (isActive=true) | No |
| GET | `/api/config/{trigger_name}` | Get current configuration | Yes (5 min TTL) |
| POST | `/api/news/generate` | Generate news (adaptive routing) | No |
| GET | `/api/history?trigger_name={name}&stockid={id}` | Fetch generation history | No |
| GET | `/api/versions/{trigger_name}` | Get version history | Yes (5 min TTL) |
| POST | `/api/config/rollback/{trigger_name}/{version}` | Rollback to previous version | No |

## Database Schema

### Collection: `trigger_prompts` (Extended)

```javascript
{
  _id: ObjectId,
  trigger_name: string,  // e.g., "earnings_result"

  // NEW FIELDS for News CMS Workflow
  isActive: boolean,  // Default: false. If true, use new method; if false, use legacy

  model_config: {
    provider: "openai" | "claude",
    model: string,  // e.g., "claude-sonnet-4-5-20250929", "gpt-4o"
    temperature: float,  // 0.0 to 1.0
    max_tokens: int  // e.g., 20000
  },

  data_config: {
    data_mode: "old" | "new" | "old_new",
    sections: [int],  // e.g., [1, 2, 3, 5, 7, 9] - selected from 14
    section_order: [int]  // e.g., [1, 2, 3, 5, 7, 9] - reordered
  },

  prompts: {
    paid: string,  // Required - primary prompt template
    unpaid: string,  // Optional - for free content
    crawler: string  // Optional - for SEO/web crawler content
  },

  version: int,  // Auto-increment on each publish
  created_at: datetime,
  updated_at: datetime,
  published_at: datetime,
  published_by: string  // User ID
}
```

**Indexes**:
- `{ trigger_name: 1 }` - Unique
- `{ isActive: 1 }` - For quick filtering

**Backward Compatibility**:
- Existing documents without `isActive` field will default to `false` (use legacy method)
- Existing documents without `model_config`, `data_config`, `prompts` fields are valid (legacy-only triggers)

### Collection: `generation_history` (New)

```javascript
{
  _id: ObjectId,
  trigger_name: string,
  stockid: int,
  prompt_type: "paid" | "unpaid" | "crawler",
  data_mode: "old" | "new" | "old_new",
  model: string,  // e.g., "claude-sonnet-4-5-20250929"

  // Input data
  input_data: object,  // Merged data used for generation
  prompt_used: string,  // Final prompt with substitutions

  // Output
  generated_html: string,  // Full HTML output
  extracted_title: string,
  extracted_summary: string,
  extracted_article: string,

  // Metadata
  method: "new" | "legacy",
  tokens_used: int,
  cost: float,
  generation_time: float,  // seconds
  timestamp: datetime,
  status: "success" | "failed",
  error_message: string  // If failed
}
```

**Indexes**:
- `{ trigger_name: 1, stockid: 1, timestamp: -1 }` - For history queries
- `{ prompt_type: 1 }` - For filtering by type
- `{ timestamp: -1 }` - For recent history

### Collection: `prompt_versions` (New)

```javascript
{
  _id: ObjectId,
  trigger_name: string,
  version: int,

  // Full snapshot of configuration at publish time
  model_config: object,
  data_config: object,
  prompts: object,  // All 3 types

  published_at: datetime,
  published_by: string,  // User ID

  // Audit metadata
  test_generation_count: int,  // How many previews before publish
  avg_cost_per_generation: float,
  iteration_count: int
}
```

**Indexes**:
- `{ trigger_name: 1, version: -1 }` - For version history queries

## Frontend Architecture

### React Context Structure

```typescript
// contexts/WorkflowContext.tsx
interface WorkflowContextType {
  // Step 1: Trigger Selection
  triggerName: string;
  stockid: number;
  oldData: any;  // From news_triggers
  existingPrompts: {
    paid: string;
    unpaid: string;
    crawler: string;
  };
  existingModelConfig?: ModelConfig;
  existingDataConfig?: DataConfig;

  // Step 2: Data Configuration
  dataMode: "old" | "new" | "old_new";
  selectedSections: number[];  // [1, 2, 3, 5, 7, 9, 12]
  sectionOrder: number[];  // [1, 2, 3, 5, 7, 9, 12]
  generatedSections?: any;  // Result from generate_full_report.py

  // Step 3: Prompt Configuration
  enabledPromptTypes: ("paid" | "unpaid" | "crawler")[];
  draftPrompts: {
    paid: string;
    unpaid: string;
    crawler: string;
  };

  // Step 4: Model Configuration
  modelConfig: {
    provider: "openai" | "claude";
    model: string;
    temperature: number;
    maxTokens: number;
  };

  // Step 5: Preview & Publish
  previewResults: {
    [promptType: string]: {
      title: string;
      summary: string;
      article: string;
      metadata: any;
    };
  };

  // Actions
  setTriggerContext: (name: string, id: number, oldData: any, prompts: any) => void;
  setDataConfig: (mode: string, sections: number[], order: number[]) => void;
  setPrompts: (type: string, content: string) => void;
  setModelConfig: (config: ModelConfig) => void;
  generatePreview: (promptType: string) => Promise<void>;
  publishConfiguration: () => Promise<void>;
}
```

### Page Structure

```
app/
├── workflow/
│   ├── page.tsx                          # Story 1.10: Trigger Selection
│   └── [trigger_name]/
│       ├── data-config/
│       │   └── page.tsx                  # Story 1.11: Data Configuration
│       ├── prompt-config/
│       │   └── page.tsx                  # Story 1.12: Prompt Configuration
│       ├── model-config/
│       │   └── page.tsx                  # Story 1.13: Model Configuration
│       └── preview-publish/
│           └── page.tsx                  # Story 1.14: Preview & Publish
├── history/
│   └── page.tsx                          # Story 1.16: Generation History
└── versions/
    └── [trigger_name]/
        └── page.tsx                      # Story 1.17: Version Control
```

### Key Components

1. **TriggerSelector**: Dropdown + stockid input
2. **DataModeSelector**: Radio buttons (OLD / NEW / OLD_NEW)
3. **SectionCheckboxList**: 14 checkboxes with drag-drop ordering (React DnD)
4. **MonacoPromptEditor**: Monaco Editor with syntax highlighting and validation
5. **PromptTypeTabs**: Tabbed interface for paid/unpaid/crawler
6. **ModelConfigForm**: Provider selection + settings (temperature, max_tokens)
7. **PreviewResults**: Grouped display by prompt type → model
8. **PublishConfirmModal**: Review and confirm before publish
9. **VersionTimeline**: Version history with diff view
10. **GenerationHistoryTable**: Filterable table of past generations

## Data Flow Diagrams

### 1. Workflow Configuration Flow

```
User → Trigger Selection → Data Configuration → Prompt Configuration → Model Configuration → Preview → Publish
         ↓                    ↓                      ↓                      ↓                    ↓         ↓
    Fetch OLD data      Generate NEW data      Create prompts         Select model         Generate    Update DB
    + existing prompts   (if NEW/OLD_NEW)      (pre-populated)       (OpenAI/Claude)      preview     (isActive=true)
```

### 2. Data Merge Flow (OLD_NEW mode)

```
trigger_name + stockid
         ↓
    ┌────┴────┐
    ↓         ↓
 OLD data  NEW data
 (news_    (generate_
 triggers)  full_report.py)
    ↓         ↓
    └────┬────┘
         ↓
   Merged Data
   {
     ...old_fields,
     "structured_sections": {...new_sections}
   }
         ↓
    LLM Prompt
```

### 3. Adaptive Generation Flow

```
News Generation Request
         ↓
  Check trigger_prompts.isActive
         ↓
    ┌────┴────┐
    ↓         ↓
 isActive   isActive
 = false    = true
    ↓         ↓
 Legacy    New Method
 Method    (single HTML prompt)
 (3 prompts) ↓
    ↓      Merge Data (OLD/NEW/OLD_NEW)
    ↓         ↓
    ↓      Generate HTML (Claude/OpenAI)
    ↓         ↓
    ↓      Extract title/summary/article
    ↓         ↓
    └────┬────┘
         ↓
   Save to news_stories
```

## Caching Strategy

### What NOT to Cache (Always Fresh)

1. **Trigger OLD Data** (`/api/triggers/{name}/data?stockid={id}`)
   - Reason: Changes during market hours (9:15 AM - 3:30 PM IST)
   - Impact: Every request queries MongoDB directly

2. **Structured NEW Data** (`/api/data/structured/generate`)
   - Reason: Time-sensitive, changes on every market data update
   - Impact: Every request runs Python script (60s timeout)

3. **Merged Data** (`/api/data/merge`)
   - Reason: Depends on non-cached OLD and NEW data
   - Impact: Fresh merge on every request

4. **Generation History** (`/api/history`)
   - Reason: Need real-time view of latest generations
   - Impact: Query MongoDB directly with filters

### What TO Cache (Static Until Updated)

1. **Existing Prompts** (`/api/triggers/{name}/prompts`)
   - TTL: 5 minutes
   - Reason: Prompts don't change frequently, only on manual edit/publish
   - Invalidation: On publish (`POST /api/config/publish`)

2. **Active Configuration** (`/api/config/{trigger_name}`)
   - TTL: 5 minutes
   - Reason: Configuration stable until republished
   - Invalidation: On publish or rollback

3. **Version History** (`/api/versions/{trigger_name}`)
   - TTL: 5 minutes
   - Reason: Historical data rarely changes (only on new publish)
   - Invalidation: On publish

**Caching Implementation**:
- Use in-memory Python dict with TTL (simple, sufficient for MVP)
- Alternative: Redis if scaling beyond single instance
- Cache key format: `{endpoint}:{trigger_name}:{stockid}`

## Error Handling

### Backend Error Types

1. **ScriptExecutionError**: `generate_full_report.py` fails
   - HTTP 500
   - Response: `{"error": "Script execution failed", "details": stderr_output}`
   - Retry: Client-side retry button

2. **DataNotFoundError**: stockid or trigger_name not in database
   - HTTP 404
   - Response: `{"error": "No data found for trigger '{name}' with stockid {id}"}`
   - Action: User enters different stockid or checks trigger_name

3. **ValidationError**: Invalid data_mode, sections, or configuration
   - HTTP 400
   - Response: `{"error": "Validation failed", "details": {...}}`
   - Action: UI prevents invalid input (client-side validation)

4. **LLMAPIError**: OpenAI or Claude API failure
   - HTTP 502
   - Response: `{"error": "LLM API error", "provider": "claude", "details": "..."}`
   - Retry: Exponential backoff (3 attempts)

5. **TimeoutError**: Script or LLM generation exceeds timeout
   - HTTP 504
   - Response: `{"error": "Operation timed out after 60s"}`
   - Action: User retries or checks data size

### Frontend Error Handling

- **Toast Notifications**: Bootstrap Toast for transient errors
- **Inline Error Messages**: Under form fields for validation errors
- **Error Boundaries**: React Error Boundary for component-level errors
- **Retry Buttons**: For recoverable errors (timeouts, API failures)
- **Graceful Degradation**: Show partial data if some sections fail

## Security Considerations

1. **stockid Validation**: Positive integer only, prevent injection
2. **API Key Protection**: Store Claude/OpenAI keys in AWS Secrets Manager
3. **Input Sanitization**: Sanitize prompt templates before storage (prevent XSS)
4. **MongoDB Injection Prevention**: Use Pydantic models for validation
5. **Rate Limiting**: Limit API calls per user (prevent abuse/cost overrun)
6. **Authentication**: Cookie-based auth for all endpoints (existing system)

## Performance Considerations

### Bottlenecks

1. **Python Script Execution**: 8-15 seconds per stockid
   - Mitigation: Async subprocess execution, don't block other requests
   - Future: Cache structured data after market hours

2. **LLM API Latency**: 10-20 seconds per generation
   - Mitigation: Client polling, display status updates
   - Future: Background job queue (Celery)

3. **MongoDB Queries**: Minimal impact (indexed queries <100ms)
   - Mitigation: Proper indexing on trigger_name, stockid, isActive

### Scaling Considerations

- **Current Target**: 5-10 concurrent users (MVP)
- **Single EC2 Instance**: Sufficient for MVP
- **Future Scaling**:
  - Add Redis for caching prompt configs
  - Use Celery for async job processing
  - Horizontal scaling with load balancer

## Testing Strategy

### Unit Tests (pytest)

- `StructuredDataService._parse_sections()`: Test section extraction
- `DataMergeService.merge_data()`: Test all 3 data modes
- `NewsGenerationService._extract_components()`: Test HTML parsing
- All Pydantic models: Test validation rules

### Integration Tests

- End-to-end: save config → publish → generate news → verify isActive routing
- Subprocess execution: Mock or use test version of `generate_full_report.py`
- MongoDB: Use test database with seed data

### E2E Tests (Playwright)

- Complete workflow: trigger selection → data config → prompt config → model config → preview → publish
- Test NEW data mode (section selection)
- Test OLD_NEW data mode (merged data)
- Test multi-type prompts (paid + unpaid + crawler)

## Deployment Notes

### Environment Variables

```bash
# MongoDB
MONGODB_URI=mongodb://localhost:27017/news_cms

# LLM API Keys (from AWS Secrets Manager)
CLAUDE_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Script Paths
STRUCTURED_DATA_SCRIPT_PATH=../structured_report_builder/generate_full_report.py

# Timeouts (seconds)
SCRIPT_TIMEOUT=60
LLM_TIMEOUT=30

# Caching
CACHE_TTL_PROMPTS=300  # 5 minutes
CACHE_TTL_CONFIG=300   # 5 minutes
```

### AWS Secrets Manager

Store sensitive keys in Secrets Manager:
- `news-cms/claude-api-key`
- `news-cms/openai-api-key`

Fetch at FastAPI startup:
```python
import boto3
secrets_client = boto3.client('secretsmanager', region_name='us-east-1')
claude_key = secrets_client.get_secret_value(SecretId='news-cms/claude-api-key')['SecretString']
```

## Rollout Plan

1. **Phase 1**: Deploy backend services (Stories 1.4-1.9)
   - Test with Postman/curl before UI
   - Verify isActive=false uses legacy method

2. **Phase 2**: Deploy frontend (Stories 1.10-1.14)
   - Test workflow with 2-3 test triggers
   - Verify preview generation works

3. **Phase 3**: Integration (Story 1.15)
   - Update existing news generation scripts
   - Test with 1-2 production triggers (isActive=true)
   - Monitor generation history

4. **Phase 4**: Full Rollout
   - Enable for all triggers incrementally
   - Monitor costs, errors, performance
   - Collect user feedback

## Backward Compatibility Checklist

- [x] Existing triggers without `isActive` field default to legacy method
- [x] Existing `generate_news_og.py` script continues to work unchanged
- [x] `news_triggers` collection schema unchanged (only query, not modify)
- [x] `news_stories` collection schema unchanged (both methods write same format)
- [x] No breaking changes to existing API endpoints
- [x] Gradual rollout: Test with isActive=true on subset of triggers first

## Future Enhancements (Post-MVP)

1. **Market Hours-Aware Caching**: Cache structured data after 3:30 PM IST with TTL until next market open
2. **Batch Generation**: Generate news for multiple stockids in parallel
3. **A/B Testing**: Compare legacy vs new method performance/quality
4. **Prompt Templates Library**: Reusable prompt snippets across triggers
5. **Advanced Validation**: Lint prompts for common errors before publish
6. **Cost Budgeting**: Set spending limits per trigger/user
7. **Webhook Notifications**: Alert on generation failures or high costs
8. **Multi-Language Support**: Generate news in multiple languages

---

**Document Version**: 1.0
**Last Updated**: 2025-10-30
**Author**: Dev Agent (Claude Code)
