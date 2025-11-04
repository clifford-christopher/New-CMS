# Development and Deployment

## Local Development Setup (Planned)

**Status**: ❌ Not yet documented. Will be created in Story 1.1 README.md.

**Planned Setup Steps**:
1. Install Python 3.11+ and Node.js 18.x
2. Clone repository
3. Backend setup:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp ../.env.example .env   # Configure local MongoDB, API keys
   uvicorn app.main:app --reload  # Runs on http://localhost:8000
   ```
4. Frontend setup:
   ```bash
   cd frontend
   npm install
   npm run dev  # Runs on http://localhost:3000
   ```
5. MongoDB setup:
   - Option 1: Install MongoDB Community Edition locally
   - Option 2: Use MongoDB Atlas free tier for development
   - Run seed script: `python scripts/seed_data.py`

**Environment Variables** (from .env.example, to be created):
```
# Backend (.env)
MONGODB_URI=mongodb://localhost:27017/news_cms_dev
AWS_REGION=us-east-1
AWS_SECRETS_MANAGER_PREFIX=news-cms/
OPENAI_API_KEY=<from Secrets Manager or local for dev>
ANTHROPIC_API_KEY=<from Secrets Manager or local for dev>
GOOGLE_API_KEY=<from Secrets Manager or local for dev>
USE_MOCK_DATA=false  # Set to true to bypass real API calls
```

## Build and Deployment Process (Planned - Story 1.6)

**Status**: ❌ Not implemented yet. Epic 1, Story 1.6.

**Deployment Architecture** (AWS EC2, No Containerization):
```
[User Browser]
     ↓ HTTPS (443)
[CloudFront or ALB - SSL Termination]
     ↓
[EC2 Instance - t3.medium]
  ├── Nginx (Reverse Proxy)
  │    ├── /api → localhost:8000 (FastAPI backend)
  │    └── /    → localhost:3000 (Next.js frontend OR static files)
  ├── FastAPI (uvicorn) - systemd service
  └── Next.js (if SSR) OR S3+CloudFront (if static export)
     ↓
[MongoDB - Dedicated EC2 OR MongoDB Atlas]
```

**Deployment Options** (Decision needed in Story 1.6):
1. **Option A**: Next.js SSR on same EC2, Nginx proxies to Node.js
2. **Option B**: Next.js static export → S3 + CloudFront, API on EC2

**CI/CD Pipeline** (Planned - GitHub Actions):
```
[Push to develop branch]
     ↓
[GitHub Actions Workflow]
  ├── Lint (flake8, eslint)
  ├── Test (pytest, jest)
  ├── Build (pip install, npm build)
  └── Deploy to Staging EC2
     ↓
[Manual Approval]
     ↓
[Deploy to Production EC2]
```

**Environments**:
- **Development**: Local (developer machines)
- **Staging**: AWS EC2 (staging environment for QA)
- **Production**: AWS EC2 (production environment)

## AWS Infrastructure Requirements (Story 1.6)

**Resources to Provision**:
- EC2 instance (t3.medium) for staging
- EC2 instance (t3.medium) for production
- MongoDB EC2 instance OR MongoDB Atlas cluster
- S3 bucket for logs, backups, static assets (if using static export)
- CloudWatch Logs for application logs
- AWS Secrets Manager secrets:
  - `news-cms/llm/openai/api-key`
  - `news-cms/llm/anthropic/api-key`
  - `news-cms/llm/google/api-key`
  - `news-cms/db/mongodb-uri`
  - `news-cms/auth/jwt-secret` (if applicable)
- IAM role for EC2 instance with Secrets Manager read access
- SSL certificate via AWS Certificate Manager
- Security groups: Allow 80, 443 inbound; 8000, 3000 internal only
