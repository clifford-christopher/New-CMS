# Quick Reference - Key Files and Entry Points

## Current Project Structure

```
news/
├── .bmad-core/              # BMAD™ Core agent framework
├── .claude/                 # Claude Code slash commands
├── docs/                    # Project documentation
│   ├── prd.md               # **PRIMARY**: Product Requirements Document
│   ├── front-end-spec.md    # UI/UX Specification (v2.2)
│   ├── CHANGELOG-epic1-api-setup.md  # Epic 1 Story 1.5a addition
│   └── figma-ai-complete-prompts-v2.md  # Design prompts
├── scripts/                 # Utility scripts
│   └── test-api-keys.py     # API key validation script (Story 1.5a)
└── README.md                # (To be created)
```

## Critical Files for Understanding the System

- **Requirements**: [docs/prd.md](docs/prd.md) - Complete product requirements and epic breakdown
- **UI/UX Specification**: [docs/front-end-spec.md](docs/front-end-spec.md) - Detailed user interface design
- **API Key Setup**: [scripts/test-api-keys.py](scripts/test-api-keys.py) - Third-party API validation
- **Epic 1 Changes**: [docs/CHANGELOG-epic1-api-setup.md](docs/CHANGELOG-epic1-api-setup.md) - Story 1.5a details

## What Does NOT Exist Yet

**Backend**: No Python/FastAPI backend code exists. Backend will be created in Epic 1 (Stories 1.1-1.6).

**Frontend**: No Next.js/React frontend code exists. Frontend will be created in Epic 1 (Stories 1.1, 1.3, 1.4).

**Database**: MongoDB is not yet set up. Database setup is Story 1.2 of Epic 1.

**Infrastructure**: AWS deployment infrastructure does not exist. Infrastructure setup is Story 1.6 of Epic 1.

**Parsers**: Existing parser scripts are assumed to exist in the main equity research platform but are NOT yet integrated or documented.

**Data APIs**: External financial data API integrations do not exist yet. These will be built in Epic 2.
