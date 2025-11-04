# Prompt Extraction and MongoDB Collection Design Plan

**Date**: 2025-10-29
**Purpose**: Extract prompts and model configurations from existing news generation scripts into a centralized MongoDB collection

---

## Executive Summary

This document outlines the plan to:
1. Extract article prompts (paid, unpaid, crawler) for **ALL triggers** found in existing Python scripts (not limited to the 27 CMS-managed triggers)
2. Extract model configurations (model name, temperature, max_tokens) per trigger
3. Create a new MongoDB collection `trigger_prompts` to store this data
4. Modify both `generate_news.py` and `generate_result_claude_news.py` to read from the new collection

**Important**: This extraction covers ALL triggers found in both scripts, including triggers that may not be actively managed by the CMS. The 27 specific triggers mentioned in the PRD are a subset that the CMS will manage, but the extraction and storage will be comprehensive for all triggers.

---

## 1. MongoDB Collection Schema Design

### Collection Name
`trigger_prompts` (in `mmfrontend` database)

### Schema Structure

```javascript
{
  "_id": ObjectId,

  // Trigger Identification
  "trigger_name": "day low",              // Normalized form (spaces, lowercase)
  "trigger_key": "day_low",               // Underscore form for code lookups
  "trigger_display_name": "Day Low",      // Human-readable form

  // Model Configuration
  "model_config": {
    "model_name": "gpt-4o-mini",          // or "claude-sonnet-4-5-20250929"
    "provider": "openai",                 // or "anthropic" or "google"
    "temperature": 0.1,                   // Float: 0.0 - 1.0
    "max_tokens": 2000,                   // Integer
    "cost_per_1m_input_tokens": 0.150,    // USD (for OpenAI gpt-4o-mini)
    "cost_per_1m_output_tokens": 0.600    // USD (for OpenAI gpt-4o-mini)
  },

  // Prompts for Different Versions
  "prompts": {
    "paid": {
      "article": "Craft a SEO friendly news article...",
      "system": null  // Only used for Claude-based prompts
    },
    "unpaid": {
      "article": "Generate an informative brief...",
      "system": null
    },
    "crawler": {
      "article": "Generate a brief summary...",
      "system": null
    }
  },

  // Special Handling Rules
  "special_handling": {
    "has_irb_boilerplate": false,         // True only for "score grade change"
    "irb_stock_id": null,                 // 430474 for IRB Infrastructure
    "irb_boilerplate_text": null,         // Text to append for IRB stock
    "irb_unpaid_override": null,          // Special unpaid prompt for IRB
    "irb_crawler_override": null          // Special crawler prompt for IRB
  },

  // Metadata
  "metadata": {
    "created_at": ISODate("2025-10-29T00:00:00Z"),
    "updated_at": ISODate("2025-10-29T00:00:00Z"),
    "version": 1,
    "extracted_from": "generate_news.py",  // or "generate_result_claude_news.py"
    "extraction_date": ISODate("2025-10-29T00:00:00Z"),
    "notes": "Initial extraction from existing scripts",
    "cms_managed": false                    // True once CMS takes over management
  },

  // Usage Statistics (for future use)
  "stats": {
    "total_generations": 0,
    "last_used": null,
    "avg_generation_time_ms": null,
    "success_rate": null
  }
}
```

### Collection Indexes

```javascript
// Primary lookup index
db.trigger_prompts.createIndex({ "trigger_name": 1 }, { unique: true })

// Secondary lookup by key format
db.trigger_prompts.createIndex({ "trigger_key": 1 })

// Management queries
db.trigger_prompts.createIndex({ "metadata.cms_managed": 1 })
db.trigger_prompts.createIndex({ "model_config.provider": 1 })
```

---

## 2. ALL 48 Triggers Identified for Extraction

**COMPREHENSIVE SCOPE**: Analysis reveals 48 unique triggers across both scripts.

### 2.1 All Triggers from generate_news.py (47 triggers)

| # | Trigger Name | Source(s) | Temperature | CMS-Managed |
|---|--------------|-----------|-------------|-------------|
| 1 | 52_week_high_summary | IF/ELIF | 0.1 | No |
| 2 | 52wk_high | DICT, LIST | 0.1 | Yes |
| 3 | 52wk_high close | LIST | 0.1 | No |
| 4 | 52wk_low | LIST | 0.1 | Yes |
| 5 | 52wk_low close | LIST | 0.1 | No |
| 6 | all_time_high | DICT, IF/ELIF, LIST | 0.1 | Yes |
| 7 | all_time_low | IF/ELIF, LIST | 0.1 | Yes |
| 8 | bulk_block_deal | DICT, LIST | 0.1 | No |
| 9 | day high | DICT, LIST | 0.1 | Yes |
| 10 | day low | LIST | 0.1 | Yes |
| 11 | dealth_cross | LIST | 0.1 | Yes |
| 12 | downgrade_summary | IF/ELIF | 0.1 | No |
| 13 | fall_from_high | LIST | 0.1 | No |
| 14 | fall_from_peak | LIST | 0.1 | No |
| 15 | fintrend_dot | IF/ELIF, LIST | 0.1 | Yes |
| 16 | gap_down | LIST | 0.1 | Yes |
| 17 | gap_up | DICT, IF/ELIF, LIST | 0.1 | Yes |
| 18 | going_down_daily | LIST | 0.1 | No |
| 19 | going_up_daily | LIST | 0.1 | No |
| 20 | golden_cross | DICT, LIST | 0.1 | Yes |
| 21 | high_return_in_period | IF/ELIF | 0.1 | No |
| 22 | index_summary | IF/ELIF | 0.1 | No |
| 23 | ipo_listing | IF/ELIF, LIST | 0.1 | No |
| 24 | market_summary | IF/ELIF | 0.1 | No |
| 25 | most_active_equities_by_value | IF/ELIF | 0.6 | Yes |
| 26 | most_active_equities_by_volume | IF/ELIF | 0.6 | Yes |
| 27 | most_active_stocks_calls | IF/ELIF, LIST | 0.6 | Yes |
| 28 | most_active_stocks_puts | IF/ELIF, LIST | 0.6 | Yes |
| 29 | multibagger | IF/ELIF | 0.1 | Yes |
| 30 | new_stock_added | IF/ELIF | 0.1 | No |
| 31 | nifty_50_stock | LIST | 0.1 | Yes |
| 32 | oi_spurts_by_underlying | IF/ELIF, LIST | 0.1 | Yes |
| 33 | only_buyers | IF/ELIF, LIST | 0.1 | Yes |
| 34 | only_sellers | DICT, IF/ELIF, LIST | 0.1 | Yes |
| 35 | quality_dot | IF/ELIF, LIST | 0.1 | Yes |
| 36 | result | IF/ELIF | 0.1 (in this script, overridden by Claude script) | Yes |
| 37 | result_summary | IF/ELIF | 0.1 | No |
| 38 | rise_from_low | LIST | 0.1 | No |
| 39 | score grade change | IF/ELIF | 0.1 | Yes |
| 40 | sector_summary | IF/ELIF | 0.1 | No |
| 41 | smallcap_market_summary | IF/ELIF | 0.1 | No |
| 42 | stocks_hitting_lower_circuit | IF/ELIF, LIST | 0.1 | Yes |
| 43 | stocks_hitting_upper_circuit | IF/ELIF, LIST | 0.1 | Yes |
| 44 | tech_dot_summary | IF/ELIF | 0.1 | No |
| 45 | technical_dot | IF/ELIF, LIST | 0.1 | Yes |
| 46 | turnaround_fall | LIST | 0.1 | No |
| 47 | turnaround_gain | LIST | 0.1 | No |
| 48 | valuation_dot | IF/ELIF, LIST | 0.1 | Yes |

### 2.2 Trigger from generate_result_claude_news.py (1 trigger)

| # | Trigger Name | Model | Temperature | CMS-Managed |
|---|--------------|-------|-------------|-------------|
| 1 | result | claude-sonnet-4-5-20250929 | 0.7 | Yes |

**Note**: The "result" trigger appears in both scripts but is handled primarily by the Claude script.

### 2.3 Summary Statistics

- **Total Triggers**: 48 unique triggers
- **CMS-Managed**: 27 triggers (will have `cms_managed: true` in MongoDB)
- **Non-CMS-Managed**: 21 triggers (will have `cms_managed: false` in MongoDB)
- **OpenAI (GPT-4o-mini)**: 47 triggers in generate_news.py
- **Anthropic (Claude)**: 1 trigger in generate_result_claude_news.py
- **Temperature 0.1**: 44 triggers
- **Temperature 0.6**: 4 triggers (most_active_equities_by_value, most_active_equities_by_volume, most_active_stocks_calls, most_active_stocks_puts)
- **Temperature 0.7**: 1 trigger (result, in Claude script)

---

## 3. Extraction Strategy

### 3.1 Extraction from `generate_news.py`

**Source**: OpenAI GPT-4o-mini based script
**Triggers**: 26 triggers (all except "result")

#### Extraction Logic

The script has several prompt selection patterns to handle:

##### Pattern 1: Direct if/elif Conditionals
```python
if "result_summary" in m_l_trigger_name:
    news_prompt = "Craft a SEO friendly news article..."
elif "high_return_in_period" in m_l_trigger_name:
    news_prompt = "Craft a SEO friendly news article..."
```

##### Pattern 2: Dictionary Lookup (STOCK_IN_ACTION_PROMPTS)
```python
STOCK_IN_ACTION_PROMPTS = {
    "golden_cross": "Craft a SEO friendly news article...",
    "dealth_cross": "Craft a SEO friendly news article...",
    "day high": "Craft a SEO friendly news article...",
    # ... etc
}

if trigger_key in STOCK_IN_ACTION_PROMPTS:
    specific_prompt = STOCK_IN_ACTION_PROMPTS[trigger_key]
```

##### Pattern 3: Fallback Generic Prompt
```python
else:
    news_prompt = f"Create a financial news article about {stock_name}..."
```

#### Model Configuration Extraction

**Default Configuration:**
```python
model = "gpt-4o-mini"
max_tokens = 2000
temperature = 0.1  # Default
```

**Temperature Variations:**
```python
triggers_for_temp_0_6 = [
    "golden_cross", "dealth_cross", "day high", "day low",
    # ... specific triggers
]

if any(trigger in m_l_trigger_name for trigger in triggers_for_temp_0_6):
    headline_temperature = 0.6
else:
    headline_temperature = 0.1
```

#### Paid/Unpaid/Crawler Prompt Variants

The script generates different versions:

**Paid Prompt** (Full article):
```python
news_prompt = "Craft a SEO friendly news article with 150 to 200 words..."
```

**Unpaid Prompt** (Teaser):
```python
unpaid_prompt = f"Generate an informative brief article about {stock_name}..."
# Hides specific numbers, company names, percentages
```

**Crawler Prompt** (SEO-optimized):
```python
crawler_prompt = f"Generate a brief summary suitable for search engines..."
# Focus on keywords, concise format
```

#### Special Handling: IRB Stock

For `trigger_name = "score grade change"` and `stockid = 430474`:

```python
IRB_STOCK_ID = 430474
IRB_BOILERPLATE_TEXT = """
Note : Historical numbers are not comparable due to change in accounting treatment...
"""

# Append boilerplate to paid articles
if stockid == IRB_STOCK_ID and "score grade change" in trigger_name:
    article += IRB_BOILERPLATE_TEXT

# Special unpaid prompt
IRB_UNPAID_PROMPT_SCORE_CHANGE = """
Discuss a recent evaluation adjustment for a publicly traded company...
"""

# Special crawler prompt
IRB_CRAWLER_PROMPT_SCORE_CHANGE = """
Discuss a recent evaluation adjustment for a publicly traded company...
"""
```

### 3.2 Extraction from `generate_result_claude_news.py`

**Source**: Anthropic Claude Sonnet 4.5 based script
**Triggers**: 1 trigger only ("result")

#### Class-Based Architecture

```python
class StockNewsGeneratorV2:
    def __init__(self, api_key=None):
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"

    def get_system_prompt(self):
        """Returns the news article system prompt with structured design"""
        return """You are an expert financial journalist...

        CRITICAL REQUIREMENTS:
        1. ARTICLE LENGTH & FORMAT: 1200-1600 words
        2. EXACT HTML STRUCTURE TO FOLLOW: [detailed HTML template]
        ...
        """

    def get_user_prompt(self, stock_data):
        fiscal_context = self.get_fiscal_year_context()
        return f"""Generate a professional financial news article...

        {fiscal_context}

        STOCK DATA:
        {stock_data}

        SPECIAL INSTRUCTIONS:
        - Use fiscal year context for accurate quarter naming
        - Highlight key financial metrics
        ...
        """
```

#### Model Configuration

```python
model = "claude-sonnet-4-5-20250929"
max_tokens = 20000
temperature = 0.7
```

#### Paid/Unpaid/Crawler Variants

**Current State**: All three variants use the SAME prompt (system + user)

**Extraction Strategy**:
- Extract system prompt → Use for all three variants
- Extract user prompt template → Use for all three variants
- Mark in metadata that variants are identical
- **Future Enhancement**: CMS can allow users to customize each variant

---

## 4. Extraction Script Design

### Script: `extract_prompts_to_mongodb.py`

```python
#!/usr/bin/env python3
"""
Extract prompts and model configurations from existing news generation scripts
and populate the trigger_prompts collection in MongoDB.

Usage:
    python scripts/extract_prompts_to_mongodb.py

Requirements:
    - pymongo
    - Access to generate_news.py and generate_result_claude_news.py
    - MongoDB running at mongodb://localhost:27017
"""

import pymongo
from datetime import datetime
from typing import Dict, Any
import re

# Connection
client = pymongo.MongoClient('mongodb://localhost:27017')
db = client['mmfrontend']
collection = db['trigger_prompts']

# ALL 48 triggers to extract (comprehensive scope)
TRIGGERS_TO_EXTRACT = [
    "52_week_high_summary", "52wk_high", "52wk_high close",
    "52wk_low", "52wk_low close", "all_time_high", "all_time_low",
    "bulk_block_deal", "day high", "day low", "dealth_cross",
    "downgrade_summary", "fall_from_high", "fall_from_peak",
    "fintrend_dot", "gap_down", "gap_up", "going_down_daily",
    "going_up_daily", "golden_cross", "high_return_in_period",
    "index_summary", "ipo_listing", "market_summary",
    "most_active_equities_by_value", "most_active_equities_by_volume",
    "most_active_stocks_calls", "most_active_stocks_puts",
    "multibagger", "new_stock_added", "nifty_50_stock",
    "oi_spurts_by_underlying", "only_buyers", "only_sellers",
    "quality_dot", "result", "result_summary", "rise_from_low",
    "score grade change", "sector_summary", "smallcap_market_summary",
    "stocks_hitting_lower_circuit", "stocks_hitting_upper_circuit",
    "tech_dot_summary", "technical_dot", "turnaround_fall",
    "turnaround_gain", "valuation_dot"
]

# The 27 CMS-managed triggers (subset that will be editable in CMS)
CMS_MANAGED_TRIGGERS = [
    "52wk_high", "52wk_low", "all_time_high", "all_time_low",
    "day high", "day low", "dealth_cross", "fintrend_dot",
    "gap_down", "gap_up", "golden_cross",
    "most_active_equities_by_value", "most_active_equities_by_volume",
    "most_active_stocks_calls", "most_active_stocks_puts",
    "multibagger", "nifty_50_stock", "oi_spurts_by_underlying",
    "only_buyers", "only_sellers", "quality_dot", "result",
    "score grade change", "stocks_hitting_lower_circuit",
    "stocks_hitting_upper_circuit", "technical_dot", "valuation_dot"
]

def normalize_trigger_name(trigger: str) -> Dict[str, str]:
    """
    Convert trigger names to different formats needed for the schema.

    Returns:
        {
            "trigger_name": "day low",  # As stored in news_triggers
            "trigger_key": "day_low",   # Underscore format for code
            "trigger_display_name": "Day Low"  # Human-readable
        }
    """
    trigger_name = trigger.lower().strip()
    trigger_key = trigger_name.replace(" ", "_")
    trigger_display_name = trigger.title()

    return {
        "trigger_name": trigger_name,
        "trigger_key": trigger_key,
        "trigger_display_name": trigger_display_name
    }

def extract_from_generate_news():
    """
    Parse generate_news.py and extract prompts for 26 triggers.

    Returns:
        List of trigger_prompt documents
    """
    # TODO: Implement parsing logic
    # 1. Read generate_news.py file
    # 2. Parse STOCK_IN_ACTION_PROMPTS dictionary
    # 3. Parse if/elif conditional blocks
    # 4. Identify paid/unpaid/crawler variants
    # 5. Extract model configs
    # 6. Handle IRB special cases
    pass

def extract_from_generate_result_claude_news():
    """
    Parse generate_result_claude_news.py and extract prompt for result trigger.

    Returns:
        Single trigger_prompt document for "result"
    """
    # TODO: Implement parsing logic
    # 1. Read generate_result_claude_news.py file
    # 2. Extract StockNewsGeneratorV2.get_system_prompt() content
    # 3. Extract StockNewsGeneratorV2.get_user_prompt() template
    # 4. Extract model config (model, temperature, max_tokens)
    # 5. Use same prompt for paid/unpaid/crawler (mark in metadata)
    pass

def create_document(trigger_name: str, prompts: Dict, model_config: Dict,
                   special_handling: Dict = None, source_file: str = "") -> Dict[str, Any]:
    """
    Create a trigger_prompts document with proper schema.
    """
    names = normalize_trigger_name(trigger_name)

    return {
        "trigger_name": names["trigger_name"],
        "trigger_key": names["trigger_key"],
        "trigger_display_name": names["trigger_display_name"],

        "model_config": {
            "model_name": model_config.get("model_name"),
            "provider": model_config.get("provider"),
            "temperature": model_config.get("temperature"),
            "max_tokens": model_config.get("max_tokens"),
            "cost_per_1m_input_tokens": model_config.get("cost_per_1m_input_tokens"),
            "cost_per_1m_output_tokens": model_config.get("cost_per_1m_output_tokens")
        },

        "prompts": {
            "paid": {
                "article": prompts["paid"]["article"],
                "system": prompts["paid"].get("system")
            },
            "unpaid": {
                "article": prompts["unpaid"]["article"],
                "system": prompts["unpaid"].get("system")
            },
            "crawler": {
                "article": prompts["crawler"]["article"],
                "system": prompts["crawler"].get("system")
            }
        },

        "special_handling": special_handling or {
            "has_irb_boilerplate": False,
            "irb_stock_id": None,
            "irb_boilerplate_text": None,
            "irb_unpaid_override": None,
            "irb_crawler_override": None
        },

        "metadata": {
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "version": 1,
            "extracted_from": source_file,
            "extraction_date": datetime.utcnow(),
            "notes": "Initial extraction from existing scripts",
            "cms_managed": False
        },

        "stats": {
            "total_generations": 0,
            "last_used": None,
            "avg_generation_time_ms": None,
            "success_rate": None
        }
    }

def main():
    """Main extraction process."""
    print("=" * 70)
    print("PROMPT EXTRACTION TO MONGODB")
    print("=" * 70)

    # Drop existing collection for clean slate
    collection.drop()
    print("✓ Dropped existing trigger_prompts collection")

    # Extract from generate_news.py
    print("\n=== Extracting from generate_news.py ===")
    news_py_docs = extract_from_generate_news()

    # Extract from generate_result_claude_news.py
    print("\n=== Extracting from generate_result_claude_news.py ===")
    result_claude_doc = extract_from_generate_result_claude_news()

    # Combine all documents
    all_docs = news_py_docs + [result_claude_doc]

    # Insert into MongoDB
    print(f"\n=== Inserting {len(all_docs)} documents into MongoDB ===")
    result = collection.insert_many(all_docs)
    print(f"✓ Inserted {len(result.inserted_ids)} documents")

    # Create indexes
    print("\n=== Creating indexes ===")
    collection.create_index("trigger_name", unique=True)
    collection.create_index("trigger_key")
    collection.create_index("metadata.cms_managed")
    collection.create_index("model_config.provider")
    print("✓ Indexes created")

    # Validation
    print("\n=== Validation ===")
    count = collection.count_documents({})
    print(f"✓ Total documents in collection: {count}")

    if count == 27:
        print("✅ SUCCESS: All 27 triggers extracted and stored!")
    else:
        print(f"⚠️  WARNING: Expected 27 documents, found {count}")

    print("=" * 70)

if __name__ == "__main__":
    main()
```

---

## 5. Script Modification Strategy

### 5.1 Modify `generate_news.py`

**Changes Required:**

1. **Add MongoDB Connection** (at module level):
```python
import pymongo

# MongoDB connection
MONGO_CLIENT = pymongo.MongoClient('mongodb://localhost:27017')
MONGO_DB = MONGO_CLIENT['mmfrontend']
PROMPTS_COLLECTION = MONGO_DB['trigger_prompts']
```

2. **Add Prompt Retrieval Function**:
```python
def get_trigger_prompts(trigger_name: str) -> Dict[str, Any]:
    """
    Retrieve prompts and model config from MongoDB for a trigger.

    Args:
        trigger_name: Trigger name as it appears in news_triggers collection

    Returns:
        Document from trigger_prompts collection or None
    """
    # Normalize trigger name
    normalized_name = trigger_name[0] if isinstance(trigger_name, list) else trigger_name
    normalized_name = normalized_name.lower().strip()

    # Query MongoDB
    doc = PROMPTS_COLLECTION.find_one({"trigger_name": normalized_name})

    if not doc:
        print(f"WARNING: No prompt found for trigger '{normalized_name}', using fallback")
        return None

    return doc
```

3. **Replace Hardcoded Prompts** (in article generation logic):
```python
# OLD CODE (to be replaced):
if "result_summary" in m_l_trigger_name:
    news_prompt = "Craft a SEO friendly news article..."
elif "high_return_in_period" in m_l_trigger_name:
    news_prompt = "Craft a SEO friendly news article..."
# ... many more elif blocks

# NEW CODE:
trigger_config = get_trigger_prompts(m_l_trigger_name)

if trigger_config:
    # Use prompts from MongoDB
    paid_prompt = trigger_config["prompts"]["paid"]["article"]
    unpaid_prompt = trigger_config["prompts"]["unpaid"]["article"]
    crawler_prompt = trigger_config["prompts"]["crawler"]["article"]

    # Use model config from MongoDB
    model = trigger_config["model_config"]["model_name"]
    temperature = trigger_config["model_config"]["temperature"]
    max_tokens = trigger_config["model_config"]["max_tokens"]

    # Handle special cases (IRB boilerplate)
    if trigger_config["special_handling"]["has_irb_boilerplate"]:
        if stockid == trigger_config["special_handling"]["irb_stock_id"]:
            paid_prompt += "\n" + trigger_config["special_handling"]["irb_boilerplate_text"]
            unpaid_prompt = trigger_config["special_handling"]["irb_unpaid_override"]
            crawler_prompt = trigger_config["special_handling"]["irb_crawler_override"]
else:
    # Fallback to hardcoded logic (for triggers not in collection)
    news_prompt = f"Create a financial news article about {stock_name}..."
    paid_prompt = news_prompt
    unpaid_prompt = news_prompt
    crawler_prompt = news_prompt
    model = "gpt-4o-mini"
    temperature = 0.1
    max_tokens = 2000
```

4. **Keep Fallback Logic**: Maintain existing if/elif blocks commented out for emergency fallback

### 5.2 Modify `generate_result_claude_news.py`

**Changes Required:**

1. **Add MongoDB Connection** (in StockNewsGeneratorV2.__init__):
```python
class StockNewsGeneratorV2:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.client = Anthropic(api_key=self.api_key)

        # MongoDB connection
        self.mongo_client = pymongo.MongoClient('mongodb://localhost:27017')
        self.mongo_db = self.mongo_client['mmfrontend']
        self.prompts_collection = self.mongo_db['trigger_prompts']

        # Load result trigger config from MongoDB
        self.load_trigger_config()

    def load_trigger_config(self):
        """Load result trigger prompts and config from MongoDB."""
        doc = self.prompts_collection.find_one({"trigger_name": "result"})

        if doc:
            self.system_prompt = doc["prompts"]["paid"]["system"]
            self.user_prompt_template = doc["prompts"]["paid"]["article"]
            self.model = doc["model_config"]["model_name"]
            self.temperature = doc["model_config"]["temperature"]
            self.max_tokens = doc["model_config"]["max_tokens"]
            print("✓ Loaded result trigger config from MongoDB")
        else:
            # Fallback to hardcoded
            print("⚠️  WARNING: result trigger not found in MongoDB, using hardcoded prompts")
            self.system_prompt = self.get_system_prompt_fallback()
            self.user_prompt_template = self.get_user_prompt_fallback()
            self.model = "claude-sonnet-4-5-20250929"
            self.temperature = 0.7
            self.max_tokens = 20000
```

2. **Update Prompt Methods**:
```python
def get_system_prompt(self):
    """Returns system prompt (from MongoDB or fallback)."""
    return self.system_prompt

def get_user_prompt(self, stock_data):
    """Returns user prompt with stock data inserted."""
    fiscal_context = self.get_fiscal_year_context()
    return self.user_prompt_template.format(
        fiscal_context=fiscal_context,
        stock_data=stock_data
    )

def get_system_prompt_fallback(self):
    """Fallback hardcoded system prompt."""
    return """You are an expert financial journalist..."""

def get_user_prompt_fallback(self):
    """Fallback hardcoded user prompt template."""
    return """Generate a professional financial news article..."""
```

3. **Keep Fallback Methods**: Preserve original get_system_prompt() and get_user_prompt() as fallback methods

---

## 6. Testing and Validation

### 6.1 Extraction Validation

After running `extract_prompts_to_mongodb.py`:

```bash
# Verify collection exists
python -c "
import pymongo
client = pymongo.MongoClient('mongodb://localhost:27017')
db = client['mmfrontend']
print(f'Total documents: {db.trigger_prompts.count_documents({})}')
"

# Expected output: Total documents: 27
```

### 6.2 Prompt Retrieval Test

Create `scripts/test_prompt_retrieval.py`:

```python
import pymongo

client = pymongo.MongoClient('mongodb://localhost:27017')
db = client['mmfrontend']
collection = db['trigger_prompts']

# Test retrieval for a few triggers
test_triggers = ["day low", "result", "golden_cross", "score grade change"]

for trigger in test_triggers:
    doc = collection.find_one({"trigger_name": trigger})
    if doc:
        print(f"✓ {trigger}: Found")
        print(f"  Model: {doc['model_config']['model_name']}")
        print(f"  Temperature: {doc['model_config']['temperature']}")
        print(f"  Has paid prompt: {bool(doc['prompts']['paid']['article'])}")
        print(f"  Has unpaid prompt: {bool(doc['prompts']['unpaid']['article'])}")
        print(f"  Has crawler prompt: {bool(doc['prompts']['crawler']['article'])}")

        # Check IRB special handling for score grade change
        if trigger == "score grade change":
            if doc['special_handling']['has_irb_boilerplate']:
                print(f"  ✓ IRB boilerplate configured")
    else:
        print(f"✗ {trigger}: NOT FOUND")
```

### 6.3 Modified Script Testing

**Test Plan:**

1. **Backup Original Scripts**:
```bash
cp generate_news.py generate_news.py.backup
cp generate_result_claude_news.py generate_result_claude_news.py.backup
```

2. **Test Single Trigger** (use a trigger with low volume):
```bash
# Pick a test trigger with few documents
python generate_news.py --trigger "gap_up" --limit 1 --test-mode
```

3. **Validate Generated Article**:
- Article should match quality of original script
- Check that MongoDB prompt was used (add debug logging)
- Verify all three variants (paid, unpaid, crawler) generated correctly

4. **Test Result Trigger**:
```bash
python generate_result_claude_news.py --test-mode --limit 1
```

5. **Compare Outputs**:
- Generate 5 articles with OLD script
- Generate 5 articles with NEW script (using MongoDB prompts)
- Compare for consistency and quality

---

## 7. Rollout Plan

### Phase 1: Extraction (Week 1)
- [ ] Create `trigger_prompts` collection schema
- [ ] Write `extract_prompts_to_mongodb.py` script
- [ ] Run extraction for all 27 triggers
- [ ] Validate extraction with test script
- [ ] Review extracted prompts manually (spot check 5-10 triggers)

### Phase 2: Script Modification (Week 1-2)
- [ ] Backup original scripts
- [ ] Modify `generate_news.py` to use MongoDB prompts
- [ ] Modify `generate_result_claude_news.py` to use MongoDB prompts
- [ ] Add fallback logic to both scripts
- [ ] Add debug logging for MongoDB retrieval

### Phase 3: Testing (Week 2)
- [ ] Test modified scripts with single trigger
- [ ] Test all 27 triggers (1 article each)
- [ ] Compare outputs: old vs new scripts
- [ ] Validate IRB special handling works correctly
- [ ] Test fallback logic (temporarily remove a prompt from MongoDB)

### Phase 4: Production Deployment (Week 2)
- [ ] Deploy modified scripts to production
- [ ] Monitor first 100 generations for issues
- [ ] Document any edge cases or issues
- [ ] Update architecture.md with new flow

### Phase 5: CMS Integration (Epic 2+)
- [ ] CMS can read from `trigger_prompts` collection
- [ ] CMS can update prompts (set `metadata.cms_managed = true`)
- [ ] CMS provides version control for prompt changes
- [ ] CMS allows A/B testing different prompts

---

## 8. Risk Mitigation

### Risk 1: Extraction Errors
**Mitigation**: Manual review of extracted prompts, compare 5-10 samples against original scripts

### Risk 2: Script Modification Breaks Generation
**Mitigation**: Keep backups, add fallback logic, extensive testing before production

### Risk 3: MongoDB Connection Failures
**Mitigation**: Fallback to hardcoded prompts, add connection retry logic

### Risk 4: Prompt Quality Degradation
**Mitigation**: Compare outputs side-by-side, run quality metrics, user acceptance testing

### Risk 5: IRB Special Handling Breaks
**Mitigation**: Dedicated test cases for stockid 430474, manual verification

---

## 9. Success Criteria

The extraction and migration is successful when:

1. ✅ All 48 triggers have documents in `trigger_prompts` collection
2. ✅ Each trigger has 3 prompt variants (paid, unpaid, crawler)
3. ✅ Model configurations are correctly stored
4. ✅ 27 CMS-managed triggers marked with `cms_managed: true`
5. ✅ 21 non-CMS triggers marked with `cms_managed: false`
6. ✅ Modified scripts generate articles identical to originals
7. ✅ IRB special handling works correctly
8. ✅ Fallback logic activates when MongoDB unavailable
9. ✅ No production issues in first 1000 generations
10. ✅ CMS can read and display all prompts correctly

---

## 10. Future Enhancements

After successful extraction and script modification:

1. **CMS Prompt Editor** (Epic 2, Story 2.3):
   - Edit prompts via web UI
   - Version control for prompt changes
   - Preview prompt changes before publishing

2. **Prompt A/B Testing** (Epic 5):
   - Test different prompt variants
   - Measure engagement metrics
   - Automatically select best-performing prompts

3. **Multi-Model Support** (Epic 4):
   - Store multiple model configs per trigger
   - Allow CMS to switch between models
   - Compare output quality across models

4. **Prompt Templates** (Epic 3):
   - Create reusable prompt templates
   - Apply templates across similar triggers
   - Template variables for dynamic content

5. **Usage Analytics** (Epic 5):
   - Track `stats` fields in collection
   - Monitor generation success rates
   - Identify underperforming prompts

---

## 11. Related Documents

- [PRD](prd.md) - Full product requirements
- [Architecture](architecture.md) - System architecture (to be updated)
- [Front-End Spec](front-end-spec.md) - CMS UI specifications
- [Existing Scripts](../scripts/) - Original news generation scripts

---

## Approval Required

**Plan Author**: Winston (Architect)
**Date**: 2025-10-29
**Status**: Awaiting User Approval

**Questions for User:**

1. Does the collection schema cover all necessary fields?
2. Should we handle more than 3 prompt variants (paid/unpaid/crawler)?
3. Any other special cases like IRB that need handling?
4. Preferred timeline for rollout?

---

**END OF PLAN**
