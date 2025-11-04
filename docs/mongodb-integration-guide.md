# MongoDB Prompt Integration Guide

## Overview

This guide explains how to modify the news generation scripts to fetch prompts from the `trigger_prompts` MongoDB collection instead of using hardcoded prompts.

## Current Status

### Completed
- ✅ Extracted all 54 triggers' prompts to MongoDB (`mmfrontend.trigger_prompts`)
- ✅ Verified 100% accuracy of extracted prompts
- ✅ Added MongoDB collection reference to `generate_news.py` (line 55)
- ✅ Added prompt cache dictionary (line 58)
- ✅ Created `load_prompt_from_mongodb()` helper function (lines 115-160)
- ✅ Modified several PAID prompts to use MongoDB (result_summary, high_return_in_period, market_summary, sector_summary, 52_week_high_summary, downgrade_summary, tech_dot_summary, new_stock_added, index_summary)

### Remaining Work
- ⏳ Modify remaining PAID prompts (14 triggers)
- ⏳ Modify UNPAID prompts (all stock_in_action_triggers + score grade change + result)
- ⏳ Modify CRAWLER prompts (same as UNPAID)
- ⏳ Modify `generate_result_claude_news.py` (1 trigger: "result")

## MongoDB Schema

Each trigger document in `mmfrontend.trigger_prompts` has this structure:

```javascript
{
  "trigger_name": "stocks_hitting_lower_circuit",
  "trigger_key": "stocks_hitting_lower_circuit",
  "trigger_display_name": "Stocks Hitting Lower Circuit",

  "model_config": {
    "model_name": "gpt-4o-mini",
    "provider": "openai",
    "temperature": 0.1,
    "max_tokens": 2000
  },

  "prompts": {
    "paid": {
      "article": "Do not generate the response in markdown format. Craft a SEO-friendly news article...",
      "system": null
    },
    "unpaid": {
      "article": "A stock has demonstrated notable activity today...",
      "system": null
    },
    "crawler": {
      "article": "A stock has demonstrated notable activity today...",
      "system": null
    }
  },

  "special_handling": {...},
  "metadata": {...}
}
```

## Helper Function Usage

The `load_prompt_from_mongodb()` function is already added to `generate_news.py` (lines 115-160):

```python
load_prompt_from_mongodb(trigger_name, prompt_type='paid', variant='article', fallback_prompt=None)
```

**Parameters:**
- `trigger_name`: Name of the trigger (e.g., 'day high', 'stocks_hitting_lower_circuit')
- `prompt_type`: Type of prompt - 'paid', 'unpaid', or 'crawler' (default: 'paid')
- `variant`: Prompt variant - 'article', 'headline', or 'system' (default: 'article')
- `fallback_prompt`: Prompt to use if MongoDB lookup fails (default: None)

**Returns:** Prompt string from MongoDB or fallback_prompt if not found

## Modification Pattern

### Pattern for PAID Prompts

**BEFORE:**
```python
elif "stocks_hitting_lower_circuit" in m_l_trigger_name:
    m_data = "\nCompany: " + m_comp_name + ", Industry: " + m_industry + ", Size: " + m_d_mcap_grade[m_mcap_grade] + "\\n" + m_data
    news_prompt = " Do not generate the response in markdown format. " + \
    "Craft a SEO-friendly news article with 150 to 200 words in an informative and neutral tone..." + m_data.replace("\\n", "\n").replace("\\t", "\t").replace('"', "'")
```

**AFTER:**
```python
elif "stocks_hitting_lower_circuit" in m_l_trigger_name:
    m_data = "\nCompany: " + m_comp_name + ", Industry: " + m_industry + ", Size: " + m_d_mcap_grade[m_mcap_grade] + "\\n" + m_data
    fallback_prompt = " Do not generate the response in markdown format. " + \
    "Craft a SEO-friendly news article with 150 to 200 words in an informative and neutral tone..." + m_data.replace("\\n", "\n").replace("\\t", "\t").replace('"', "'")
    db_prompt = load_prompt_from_mongodb("stocks_hitting_lower_circuit", prompt_type='paid', variant='article', fallback_prompt=None)
    if db_prompt:
        news_prompt = db_prompt + " " + m_data.replace("\\n", "\n").replace("\\t", "\t").replace('"', "'")
    else:
        news_prompt = fallback_prompt
```

### Pattern for UNPAID Prompts

**BEFORE:**
```python
elif 'valuation_dot' in m_l_trigger_name:
    m_unpaid_user_prompt = "Important: If the context mentions a change from one specific grade to another..."
    m_google_crawler_prompt = "Important: If the context mentions a change from one specific grade to another..."
```

**AFTER:**
```python
elif 'valuation_dot' in m_l_trigger_name:
    fallback_unpaid = "Important: If the context mentions a change from one specific grade to another..."
    fallback_crawler = "Important: If the context mentions a change from one specific grade to another..."

    db_unpaid = load_prompt_from_mongodb("valuation_dot", prompt_type='unpaid', variant='article', fallback_prompt=None)
    db_crawler = load_prompt_from_mongodb("valuation_dot", prompt_type='crawler', variant='article', fallback_prompt=None)

    m_unpaid_user_prompt = db_unpaid if db_unpaid else fallback_unpaid
    m_google_crawler_prompt = db_crawler if db_crawler else fallback_crawler
```

## Triggers Requiring Modification

### PAID Prompts (Lines 421-468)
Remaining triggers to modify:
1. ✅ multibagger (line 421-424)
2. ✅ only_buyers (line 425-427)
3. ✅ only_sellers (line 428-430)
4. ✅ ipo_listing (line 431-433)
5. ✅ valuation_dot (line 434-436)
6. ✅ quality_dot (line 437-439)
7. ✅ fintrend_dot (line 440-442)
8. ✅ technical_dot (line 443-445)
9. ✅ stocks_hitting_upper_circuit (line 446-449)
10. ✅ stocks_hitting_lower_circuit (line 450-453)
11. ✅ most_active_equities_by_volume/value (line 454-456)
12. ✅ most_active_stocks_calls (line 457-460)
13. ✅ most_active_stocks_puts (line 461-464)
14. ✅ oi_spurts_by_underlying (line 465-468)

### UNPAID/CRAWLER Prompts (Lines 610-647)
Triggers to modify:
1. only_buyers (line 611-613)
2. only_sellers (line 614-616)
3. valuation_dot (line 617-619)
4. quality_dot (line 620-622)
5. fintrend_dot (line 623-625)
6. technical_dot (line 626-628)
7. stock_in_action_triggers default (line 629-631)
8. score grade change (line 632-642) - **Note: IRB special handling!**
9. result (line 643-647) - **Note: IRB special handling!**

### IRB Special Handling

For `stockid == 430474` (IRB):
- score grade change: Uses `IRB_UNPAID_PROMPT_SCORE_CHANGE` and `IRB_CRAWLER_PROMPT_SCORE_CHANGE`
- result: Uses `IRB_UNPAID_PROMPT_RESULT` and `IRB_CRAWLER_PROMPT_RESULT`

These are defined at lines 159-211. Keep this logic intact!

## Fallback Strategy

The modification includes fallbacks to ensure the system works even if MongoDB is unavailable:

1. **Primary**: Load from MongoDB
2. **Fallback**: Use hardcoded prompt (original logic)
3. **Cache**: Prompts are cached in `_prompt_cache` dictionary to avoid repeated database queries

## Testing Strategy

After modifications, test with:

```python
# Test 1: Verify MongoDB prompts are loaded
python scripts/test_mongodb_prompts.py

# Test 2: Generate news for a test trigger
python scripts/test_generate_one_trigger.py --trigger "day high" --stockid 500325

# Test 3: Check fallback works when MongoDB is unavailable
# (Stop MongoDB, run generation, verify it uses hardcoded prompts)
```

## Implementation Status

### generate_news.py
- **Modified**: 9 PAID prompts
- **Remaining**: 14 PAID prompts, all UNPAID/CRAWLER prompts
- **Estimated effort**: 1-2 hours for systematic modification

### generate_result_claude_news.py
- **Modified**: None
- **Remaining**: Modify `StockNewsGeneratorV2.__init__()` to load prompts from MongoDB
- **Estimated effort**: 30 minutes

## Next Steps

1. Complete remaining PAID prompt modifications in `generate_news.py` (lines 421-468)
2. Modify UNPAID/CRAWLER prompts in `generate_news.py` (lines 610-647)
3. Modify `generate_result_claude_news.py` to load from MongoDB
4. Test thoroughly with sample triggers
5. Deploy to production after successful testing

## Notes

- **IMPORTANT**: Never remove fallback prompts! They ensure system resilience.
- **IMPORTANT**: Keep all IRB special handling logic intact.
- **IMPORTANT**: Don't modify temperature/max_tokens logic - these come from model_config in MongoDB but should stay in code for now.
- The modification only changes HOW prompts are fetched, not WHAT logic runs or WHEN it runs.
