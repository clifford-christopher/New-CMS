# Data Models and APIs

## Planned Data Models

**Note**: These models do not exist yet. They will be created as Pydantic models in backend/app/models/ during Epic 1, Story 1.2.

### Trigger Model
```python
# backend/app/models/trigger.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Trigger(BaseModel):
    id: str = Field(alias="_id")
    name: str                           # e.g., "Earnings Alert"
    description: str
    trigger_type: str                   # e.g., "earnings", "price_movement"
    status: str                         # "configured" | "unconfigured" | "in_progress"
    last_updated: datetime
    created_at: datetime
    created_by: str                     # User ID
```

### Configuration Model (Multi-Prompt Type Support)
```python
# backend/app/models/configuration.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Optional

class PromptConfig(BaseModel):
    template: str
    version_history: List[Dict]         # List of {template, timestamp, user_id}
    last_test_generation: Optional[Dict]  # {timestamp, stock_id, results}

class Configuration(BaseModel):
    id: str = Field(alias="_id")
    trigger_id: str
    version: int

    # SHARED across all prompt types (configured once, applies to all)
    data_sections: List[str]            # Selected section IDs (e.g., ["1", "2", "3", "5", "7"])
    section_order: List[str]            # Order of sections
    model_config: Dict                  # {selected_models, temperature, max_tokens}

    # SEPARATE per prompt type (independent templates)
    prompts: Dict[str, PromptConfig]    # {"paid": PromptConfig, "unpaid": PromptConfig, "crawler": PromptConfig}

    # Metadata
    created_by: str
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
    is_active: bool                     # True if production version
```

### User Model
```python
# backend/app/models/user.py
from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: str = Field(alias="_id")
    username: str
    email: str
    role: str                           # "content_manager" | "analyst" | "team_lead"
    created_at: datetime
```

### Audit Log Model
```python
# backend/app/models/audit_log.py
from pydantic import BaseModel
from datetime import datetime
from typing import Dict

class AuditLog(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    action: str                         # "created", "updated", "published", "api_added", "prompt_edited"
    trigger_id: str
    timestamp: datetime
    details: Dict                       # JSON diff or action details
```

## Planned API Specifications

**Status**: APIs do not exist yet. Will be implemented throughout Epic 1-5.

**API Documentation**: FastAPI will auto-generate OpenAPI documentation at `/docs` (Swagger UI) and `/redoc` (ReDoc).

### Epic 1 - Foundation APIs

**Health Check** (Story 1.2):
```
GET /api/health
Response: { "status": "ok", "database": "connected", "timestamp": "..." }
```

**Trigger Management** (Story 1.4):
```
GET /api/triggers
Response: [{ "id": "...", "name": "...", "status": "...", "last_updated": "..." }, ...]

GET /api/triggers/:id/config
Response: { "trigger_id": "...", "data_sections": [...], "prompts": {...}, ... }
```

### Epic 2 - Data Pipeline APIs

**API Configuration** (Story 2.1):
```
POST /api/triggers/:id/config/apis
Body: { "api_id": "earnings_api" }
Response: { "success": true, "configured_apis": [...] }

DELETE /api/triggers/:id/config/apis/:apiId
Response: { "success": true, "configured_apis": [...] }
```

**Data Retrieval** (Story 2.3):
```
POST /api/triggers/:id/data/fetch
Body: { "stock_id": "AAPL", "section_ids": ["1", "2", "3"] }
Response: { "raw_data": { "section_1": {...}, "section_2": {...} }, "status": {...} }
```

**Data Parsing** (Story 2.4):
```
POST /api/triggers/:id/data/parse
Body: { "raw_data": {...} }
Response: { "structured_data": { "sections": [...] }, "errors": [] }
```

### Epic 4 - LLM Generation APIs

**Multi-Model Generation** (Story 4.3):
```
POST /api/triggers/:id/generate
Body: {
  "stock_id": "AAPL",
  "selected_models": ["gpt-4", "claude-3-sonnet"],
  "prompt_types": ["paid", "unpaid"],        # Only checked types
  "prompts": {
    "paid": "...",
    "unpaid": "..."
  },
  "structured_data": {...},
  "model_settings": {...}
}
Response (SSE stream or polling):
{
  "generation_id": "...",
  "status": {
    "paid": {
      "gpt-4": "generating",
      "claude-3-sonnet": "complete"
    },
    "unpaid": {
      "gpt-4": "pending",
      "claude-3-sonnet": "generating"
    }
  },
  "results": {
    "paid": {
      "gpt-4": null,
      "claude-3-sonnet": {
        "text": "...",
        "tokens": 456,
        "cost": 0.08,
        "latency": 8.3
      }
    },
    "unpaid": {...}
  }
}
```

### Epic 5 - Publishing APIs

**Publish Configuration** (Story 5.2):
```
POST /api/triggers/:id/publish
Body: { "configuration": {...} }  # Includes all 3 prompt types
Response: { "success": true, "version": 2, "timestamp": "..." }
```

**Active Configuration** (Story 5.5):
```
GET /api/triggers/:id/active-config
Response: {
  "trigger_id": "...",
  "data_sections": [...],
  "prompts": {
    "paid": {...},
    "unpaid": {...},
    "crawler": {...}
  },
  "model_config": {...}
}
```

## MongoDB Collections Schema Design

**Collections** (to be created in Story 1.2):
- `triggers`: Trigger definitions
- `configurations`: Configuration versions (includes all 3 prompt types in single document)
- `users`: User accounts (may integrate with existing auth system)
- `audit_log`: Change tracking
- `generation_history`: Test generation results (session-level, 30-day retention)

**Indexes** (to be created):
- `triggers`: `{ trigger_id: 1 }`
- `configurations`: `{ trigger_id: 1, is_active: 1 }`, `{ version: -1 }`
- `audit_log`: `{ trigger_id: 1, timestamp: -1 }`, `{ user_id: 1 }`
