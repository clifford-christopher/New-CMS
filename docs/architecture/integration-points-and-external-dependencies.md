# Integration Points and External Dependencies

## External Services (Planned)

| Service          | Purpose              | Integration Type | Status              | Key Files (Future)                          |
|------------------|----------------------|------------------|---------------------|---------------------------------------------|
| OpenAI           | LLM (GPT-4, GPT-3.5) | REST API         | ⚠️ API key setup (1.5a) | backend/app/llm_providers/openai_provider.py |
| Anthropic        | LLM (Claude 3)       | REST API         | ⚠️ API key setup (1.5a) | backend/app/llm_providers/anthropic_provider.py |
| Google AI        | LLM (Gemini Pro)     | REST API         | ⚠️ API key setup (1.5a) | backend/app/llm_providers/google_provider.py |
| AWS Secrets Manager | Secure key storage | AWS SDK (boto3) | ⚠️ Story 1.5a in progress | backend/app/config.py |
| MongoDB Atlas (or EC2) | Database         | MongoDB driver  | ❌ Not setup (Story 1.2) | backend/app/database.py |
| Financial Data APIs | Market data       | REST API (TBD)  | ❌ Not identified yet | backend/app/data_adapters/ |

**Note**: Specific financial data API providers not yet identified. This is flagged in CHANGELOG-epic1-api-setup.md as requiring product team input.

## Internal Integration Points (Existing Systems)

**Authentication System**:
- **Integration Type**: Cookie-based authentication
- **Status**: ❌ Not yet designed
- **Epic**: Epic 1 (Story 1.1 - to be determined)
- **Assumption**: Existing equity research platform has authentication system that can issue cookies
- **Risk**: Integration details unknown; may require investigation spike

**Parser Scripts**:
- **Location**: Unknown (assumed to exist in main platform codebase)
- **Integration Approach**: Direct Python module import OR subprocess calls
- **Status**: ❌ Not investigated yet
- **Epic**: Epic 2 (Story 2.4)
- **Risk**: HIGH - Parser integration feasibility unknown (flagged in PRD as technical risk)
- **Next Step**: Identify parser locations and interfaces before Epic 2

**Production News Generation Pipeline**:
- **Integration Type**: Shared MongoDB database OR REST API
- **Status**: ❌ Not designed yet
- **Epic**: Epic 5 (Story 5.5)
- **Approach**: CMS publishes configurations to MongoDB; existing system reads active configurations
- **Alternative**: Expose GET /api/triggers/:id/active-config for existing system to poll

## Data Flow Between Systems

**Planned Integration Flow** (Epic 5):
```
[News CMS - Configuration Published]
         ↓
[MongoDB - configurations collection, is_active = true]
         ↓
[Existing Production News System - Reads Active Config]
         ↓
[Calls Data APIs + Parsers + LLM based on CMS config]
         ↓
[Publishes News to End Users]
```

**Key Integration Questions** (Require Investigation):
1. **Parser Integration**: Where are parser scripts located? Python modules or standalone scripts?
2. **Authentication**: Cookie format? Session validation endpoint? JWT tokens?
3. **Financial Data APIs**: Which providers? API keys already exist or need procurement?
4. **Production Pipeline**: MongoDB read pattern or REST API polling?
