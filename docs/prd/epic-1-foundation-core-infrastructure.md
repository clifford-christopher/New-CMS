# Epic 1: Foundation & Core Infrastructure

**Goal**: Establish the technical foundation for the News CMS including project structure, core infrastructure (FastAPI backend, Next.js frontend, MongoDB database), basic UI shell, and trigger management. This epic delivers a deployable "walking skeleton" that allows users to view and select news triggers—providing immediate value while establishing the architecture for all subsequent features. Authentication is handled via cookies from the existing authentication system.

### Story 1.1: Project Setup and Monorepo Structure

**As a** developer,
**I want** a properly configured monorepo with frontend and backend projects,
**so that** the team can develop both applications with consistent tooling and shared dependencies.

**Acceptance Criteria**:
1. Monorepo created with `frontend/` (Next.js + TypeScript) and `backend/` (Python/FastAPI) directories
2. Frontend package.json configured with Next.js 14+, TypeScript, React-Bootstrap, and Monaco Editor dependencies
3. Backend pyproject.toml or requirements.txt configured with FastAPI, Pydantic v2, Motor (MongoDB async driver), and pytest
4. Shared schemas directory created with example Pydantic model exported for use by both frontend and backend
5. Root-level README.md documents project structure, local development setup instructions, and technology stack
6. Git repository initialized with appropriate .gitignore files for Node.js and Python
7. Both frontend and backend applications start successfully in local development mode (npm run dev, uvicorn)

### Story 1.2: MongoDB Database Setup and Connection

**As a** developer,
**I want** MongoDB database connectivity configured with initial collections,
**so that** the application can persist triggers, configurations, and audit data.

**Acceptance Criteria**:
1. MongoDB Community Edition installed locally or MongoDB Atlas connection configured
2. Pydantic models created for core collections: Trigger, Configuration, User, AuditLog
3. FastAPI backend establishes async connection to MongoDB using Motor driver on startup
4. Database connection health check endpoint `/api/health` returns MongoDB connection status
5. Migration script (or documentation) creates initial collections with appropriate indexes (e.g., trigger_id, user_id, created_at)
6. Sample seed data script populates database with 3-5 example triggers for development testing
7. Environment variable configuration for MongoDB connection string (supports local and cloud deployments)
8. Graceful error handling and logging if MongoDB connection fails

### Story 1.3: Basic UI Shell and Navigation

**As a** content manager,
**I want** a professional, navigable UI shell with Bootstrap styling,
**so that** I can access different areas of the CMS intuitively.

**Acceptance Criteria**:
1. Next.js App Router layout created with Bootstrap 5 CSS imported globally
2. Responsive navigation bar using React-Bootstrap Navbar component with logo placeholder
3. Navigation includes links to: Dashboard (Triggers), Configuration Workspace (disabled until trigger selected), Settings (placeholder)
4. Footer displays application name and version
5. Application meets NFR6: Responsive design with 1200px+ desktop layout and 768px+ tablet layout
6. All pages use consistent Bootstrap grid system and spacing utilities
7. Basic loading spinner component created for future async operations

### Story 1.4: Trigger Management Dashboard

**As a** content manager,
**I want** to view a list of available news triggers with status information,
**so that** I can select a trigger to configure.

**Acceptance Criteria**:
1. FastAPI endpoint `GET /api/triggers` returns list of all triggers from MongoDB (name, description, status, last_updated)
2. Frontend Dashboard page fetches and displays triggers in Bootstrap Table or Card grid
3. Each trigger shows: name, description, configuration status (Configured/Unconfigured), last updated timestamp
4. Visual status indicator (badge or icon) distinguishes configured vs. unconfigured triggers
5. Clicking a trigger navigates to Configuration Workspace with trigger ID in URL (`/config/:triggerId`)
6. Empty state displayed if no triggers exist (with message suggesting database seeding)
7. Loading state displayed while fetching triggers from API
8. Error handling displays user-friendly message if API call fails
9. Meets NFR1: Page loads in under 2 seconds with 10+ triggers

### Story 1.5: AWS Deployment Setup for Staging Environment

**As a** developer,
**I want** the application deployed to AWS EC2 staging environment,
**so that** stakeholders can test the foundation in a production-like setting.

**Acceptance Criteria**:
1. AWS EC2 instance (t3.medium) provisioned for staging environment
2. MongoDB installed and running on dedicated EC2 instance or MongoDB Atlas configured
3. Python 3.11+ installed with FastAPI backend deployed using virtual environment
4. FastAPI backend runs as systemd service using uvicorn (auto-restart on failure)
5. Next.js frontend build deployed (either static export to S3+CloudFront or running on same EC2 with Node.js)
6. Nginx configured as reverse proxy for SSL termination and routing (frontend, backend API)
7. SSL certificate configured using AWS Certificate Manager (HTTPS enabled)
8. AWS Secrets Manager stores MongoDB credentials and LLM API keys
9. Basic CI/CD pipeline (GitHub Actions) deploys to staging on push to `develop` branch
10. Staging environment accessible via public URL (e.g., https://staging.news-cms.example.com)
11. CloudWatch Logs configured to capture application logs (FastAPI and Next.js)
12. Health check endpoint `/api/health` accessible and returns 200 status
