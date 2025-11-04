# Epic 5: Configuration Publishing & Production Integration

**Goal**: Enable content managers to confidently publish tested configurations to production with validation safeguards, versioning, comprehensive audit trails, and integration with the existing news generation system. This epic closes the loop from testing to production deployment, delivering the key business value of eliminating developer dependency.

### Story 5.1: Pre-Publish Validation (All Prompt Types)

**As a** content manager,
**I want** the system to validate all prompt type configurations before publishing,
**so that** I don't accidentally deploy incomplete or untested configurations for any audience type.

**Acceptance Criteria**:
1. "Publish" button triggers validation checks for all three prompt types before allowing publication
2. Validation rules implemented per prompt type: prompt not empty, at least one successful test generation exists for each type
3. Shared validation: at least one API configured (FR5), section order defined, model selected
4. Validation failure displays modal with checklist of issues grouped by prompt type and prevents publishing
5. Validation success enables "Confirm Publish" button
6. Meets FR26 and FR31: validation of complete and tested configurations for all prompt types before publish
7. Visual checklist shows:
   - ✓ APIs configured (shared)
   - ✓ Section order defined (shared)
   - ✓ Model selected (shared)
   - Per prompt type:
     - ✓ Paid prompt created and tested
     - ✓ Unpaid prompt created and tested
     - ✓ Crawler prompt created and tested
8. Warning if any prompt type configuration differs from last successful test (prompt changed without re-testing)
9. Optional: Suggest minimum testing threshold (e.g., "Test all prompt types with at least 2 models before publishing")
10. Validation errors include actionable guidance per prompt type (e.g., "Paid prompt is empty - add prompt content to continue")

### Story 5.2: Configuration Publishing with Confirmation (All Prompt Types)

**As a** content manager,
**I want** to review and confirm exactly what will be published for all prompt types,
**so that** I understand what changes are going live in production for each audience type.

**Acceptance Criteria**:
1. After validation, "Confirm Publish" button opens confirmation modal showing what will be saved for all three prompt types
2. Confirmation modal displays:
   - Trigger name
   - Configured APIs (list) - shared
   - Section order - shared
   - Selected model and settings - shared
   - Per prompt type:
     - 💰 Paid prompt (truncated preview with character count)
     - 🆓 Unpaid prompt (truncated preview with character count)
     - 🕷️ Crawler prompt (truncated preview with character count)
3. Diff view if updating existing configuration (shows what changed from current production version for each prompt type)
4. Expandable sections per prompt type to view full prompt in modal
5. "Publish to Production" final button in modal triggers backend `POST /api/triggers/:id/publish` with all three prompt types
6. Backend saves configuration to MongoDB with version number (auto-incrementing) including all prompt types
7. Published configuration marked as "active" for the trigger (only one active config per trigger, contains all three prompt types)
8. Meets FR25, FR27, FR28: publish function with confirmation, versioning, and activation for all prompt types
9. Success notification displays version number, timestamp, and summary: "Published configuration with 3 prompt types"
10. Published configuration immediately available for use by automated news generation system for all prompt types
11. "View Published Configuration" link navigates to read-only view of active production config showing all three prompt types

### Story 5.3: Audit Logging and Change Tracking

**As a** compliance officer or system administrator,
**I want** comprehensive audit logs of all configuration changes,
**so that** we can track who made changes, when, and what was changed.

**Acceptance Criteria**:
1. All configuration changes logged to MongoDB `audit_log` collection with: user_id, action, timestamp, trigger_id, details (JSON diff)
2. Logged actions include: configuration created, updated, published, API added/removed, prompt edited, model changed
3. Backend middleware automatically logs all write operations to configurations
4. Meets FR32, FR33, FR34: logging of changes, tracking production configs, maintaining history
5. Audit log UI accessible from navigation (admin/audit page)
6. Audit log table displays: timestamp, user, trigger, action, details (expandable)
7. Filtering by trigger, user, date range, action type
8. Export audit log to CSV or JSON for compliance reporting
9. Audit logs immutable (no deletion or editing allowed via UI)
10. Meets NFR15: comprehensive audit logs for compliance

### Story 5.4: Configuration Version History and Rollback

**As a** content manager,
**I want** to view previous configuration versions and rollback if needed,
**so that** I can recover from mistakes or compare historical approaches.

**Acceptance Criteria**:
1. "Configuration History" screen accessible from Configuration Workspace
2. History displays all published versions for selected trigger with version number, timestamp, published by (user)
3. Clicking a historical version shows read-only view of that configuration (APIs, prompt, model, section order)
4. Diff view compares any two versions (highlighting added/removed/changed elements)
5. "Rollback to This Version" button allows restoring a previous configuration as current active version
6. Rollback creates new version (not true revert) and logs as audit event
7. Confirmation modal before rollback warns that current production config will be replaced
8. Version history infinite retention as per data retention policy (NFR15)
9. Meets requirement for configuration versioning and history maintenance
10. Version metadata includes: which model was used for testing, cost of test generations, number of test iterations

### Story 5.5: Production Integration and Active Configuration API

**As a** backend developer (of existing news generation system),
**I want** a stable API to fetch active configurations for triggers,
**so that** automated news generation can use CMS-published configurations.

**Acceptance Criteria**:
1. Backend endpoint `GET /api/triggers/:id/active-config` returns currently active published configuration
2. Response includes all necessary data: APIs to call, parser settings, section order, prompt template, selected LLM model, model settings
3. API versioned (e.g., `/api/v1/`) to support future changes without breaking existing integrations
4. Authentication required using cookies (compatible with existing authentication system)
5. Response cached (short TTL, e.g., 5 minutes) to reduce database load from automated polling
6. 404 returned if no active configuration exists for trigger (with clear error message)
7. Documentation (OpenAPI/Swagger) auto-generated by FastAPI describes endpoint
8. Integration test validates that published configuration is immediately accessible via this endpoint
9. Backward compatibility maintained with existing news generation system expectations
10. Logging of all API calls for monitoring integration health
