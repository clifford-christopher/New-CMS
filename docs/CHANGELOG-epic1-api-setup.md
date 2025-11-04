# Epic 1 Enhancement: Third-Party API Setup Story

**Date**: 2025-10-24
**Author**: Sarah (Product Owner)
**Type**: Story Addition - Critical Gap Resolution

---

## Summary

Added **Story 1.5a: Third-Party API Setup and Key Acquisition** to Epic 1 to address a critical gap in the PRD: the API key acquisition process was not documented, which would have blocked LLM integration in Epic 4.

---

## Changes Made

### 1. New Story Created

**Location**: `docs/stories/story-1.5a-third-party-api-setup.md`

**Purpose**: Establish all third-party service accounts, obtain API keys, and configure secure storage before development of integration code begins.

**Key Coverage**:
- OpenAI, Anthropic, and Google AI account creation
- Financial data API provider account setup
- API key acquisition and secure storage in AWS Secrets Manager
- Billing alerts and cost monitoring
- Rate limit documentation
- Testing and validation scripts

### 2. Epic 1 Document Updated

**Location**: `docs/prd/epic-1-foundation-core-infrastructure.md`

**Changes**:
- Added Story 1.5a between Story 1.5 (Trigger Management Dashboard) and Story 1.6 (AWS Deployment)
- Enhanced Story 1.6 acceptance criteria:
  - Added explicit dependency on Story 1.5a
  - Added DNS configuration requirement (AC #8)
  - Made frontend deployment strategy decision explicit (AC #5)
  - Added validation that backend can retrieve secrets (AC #10)

### 3. Documentation Created

**New File**: `docs/third-party-setup.md` (to be created as part of Story 1.5a)

Will contain step-by-step instructions for:
- Account creation for each LLM provider
- API key generation process
- Secrets Manager storage procedure
- Billing and cost monitoring setup

---

## Rationale

### Problem Identified
During PO Master Checklist validation, Section 3 (External Dependencies & Integrations) revealed:

1. **High Priority Gap**: No documented process for obtaining API keys from OpenAI, Anthropic, Google AI, or financial data providers
2. **Impact**: Would block Epic 4 (LLM integration) when developers need credentials
3. **Risk**: Unclear ownership of account creation, billing setup, and key management

### Solution Approach

Created a dedicated story that:
- **Executes early** (Epic 1, before deployment) to unblock future work
- **Addresses procurement** with specific account tiers and spending limits
- **Handles security** via AWS Secrets Manager with IAM policies
- **Includes validation** through test scripts
- **Documents process** for repeatability and knowledge transfer

### Key Decisions Made

| Decision | Rationale |
|----------|-----------|
| OpenAI Team tier ($20/month + usage) | Higher rate limits (3,500 RPM vs 500), needed for parallel testing |
| $500 total LLM budget split: $200 OpenAI, $150 Anthropic, $150 Google | Based on expected usage patterns (OpenAI primary, others for comparison) |
| Start Anthropic application in Week 1 | 1-2 day approval time could block Epic 4 if delayed |
| AWS Secrets Manager for all credentials | Centralized, encrypted, auditable, integrates with EC2 IAM |
| Mock mode for development | Unblocks development before all API keys available |

---

## Story Sequencing

### Original Epic 1 Flow
```
1.1 → 1.2 → 1.3 → 1.4 → 1.5 → 1.6
```

### Updated Epic 1 Flow
```
1.1 → 1.2 → 1.3 → 1.4 → 1.5 → 1.5a → 1.6
                                  ↓
                            [Blocks 4.1]
                            [Blocks 2.2]
```

### Parallel Execution Opportunity
Story 1.5a can be **started in parallel** with Stories 1.1-1.4 (especially Anthropic account application) to minimize schedule impact.

---

## Impact Assessment

### Schedule Impact
- **Story Points**: +3 points to Epic 1 (was ~21 points, now ~24 points)
- **Time Impact**: +1-2 days (mostly waiting for Anthropic approval)
- **Mitigation**: Start Anthropic application immediately, parallelize account creation with other Epic 1 work

### Benefits
- ✅ Eliminates blocker for Epic 4 (Multi-Model Generation)
- ✅ Eliminates blocker for Epic 2 (Data API Integration)
- ✅ Establishes cost control early (budget alerts, spending limits)
- ✅ Improves security (secrets never in code or env files)
- ✅ Provides clear ownership and process documentation

### Risks Mitigated
| Risk | Before | After |
|------|--------|-------|
| Epic 4 blocked waiting for API keys | High | Low (keys ready in Epic 1) |
| Budget overrun during testing | Medium | Low (spending limits set) |
| Secrets committed to git | Medium | Low (Secrets Manager + validation) |
| Unclear account ownership | High | Low (documented in setup guide) |

---

## Developer Impact

### What Developers Need to Know

1. **Story 1.5a Prerequisites**:
   - AWS account access to Secrets Manager
   - Authorization to create accounts on behalf of organization
   - Credit card or billing account for paid tiers

2. **Story 1.5a Deliverables**:
   - All API keys in Secrets Manager (retrievable by backend)
   - `docs/third-party-setup.md` with complete instructions
   - `scripts/test-api-keys.py` validation script
   - Billing alerts configured

3. **Local Development**:
   - Developers can use `USE_MOCK_DATA=true` to bypass API calls during development
   - Or request read access to Secrets Manager for development secrets
   - See backend/.env.example for required environment variables

---

## Validation Checklist

Before marking Epic 1 complete, verify Story 1.5a outcomes:

- [ ] All LLM provider accounts created (OpenAI, Anthropic, Google AI)
- [ ] All financial data API provider accounts created
- [ ] All secrets stored in AWS Secrets Manager with correct naming
- [ ] IAM policy grants EC2 instance role access to secrets
- [ ] Billing alerts configured for all LLM providers
- [ ] `docs/third-party-setup.md` created and reviewed
- [ ] `scripts/test-api-keys.py` runs successfully
- [ ] Backend can retrieve secrets on startup (verified in Story 1.6 deployment)
- [ ] No secrets in git history (verified with git log scan)

---

## Questions for Product Team

The following decisions may require product team input:

1. **Financial Data API Providers**: Which specific providers should we use?
   - Earnings data: [Provider name needed]
   - Price/market data: [Provider name needed]
   - Analyst ratings: [Provider name needed]

2. **Google AI Authentication**: API key or service account for production?
   - **Recommendation**: Service account for better security
   - **Decision needed by**: End of Week 1

3. **Budget Allocation**: Confirm $500/month total LLM budget is acceptable
   - OpenAI: $200, Anthropic: $150, Google: $150
   - Alert threshold: $400 (80%)

---

## Next Steps

1. **Immediate** (Week 1, Day 1):
   - Start Anthropic API access application (1-2 day approval time)
   - Identify financial data API providers with product team

2. **Epic 1 Execution**:
   - Complete Story 1.5a before Story 1.6 (deployment)
   - Validate secrets retrieval in Story 1.6 acceptance testing

3. **Epic 2 & 4 Readiness**:
   - API keys available for Data API Integration (Story 2.2)
   - API keys available for LLM Provider Integration (Story 4.1)

---

## Approval Required

**Reviewed by**: [Product Owner, Tech Lead]
**Approved by**: [Project Stakeholders]
**Date**: [Approval date]

---

## Related Documents

- Full Story Details: [docs/stories/story-1.5a-third-party-api-setup.md](stories/story-1.5a-third-party-api-setup.md)
- Epic 1 Updated: [docs/prd/epic-1-foundation-core-infrastructure.md](prd/epic-1-foundation-core-infrastructure.md)
- PO Checklist Results: [Section 3 findings]
