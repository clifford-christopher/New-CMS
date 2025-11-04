# Appendix - Useful Commands and Workflows

## Development Commands (To Be Documented in README)

**Backend**:
```bash
# Start development server
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest tests/ -v

# Lint
flake8 app/

# Seed database
python scripts/seed_data.py

# Validate API keys
python scripts/test-api-keys.py
```

**Frontend**:
```bash
# Start development server
cd frontend
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Lint
npm run lint
```

**Full Stack**:
```bash
# Run both backend and frontend concurrently (using npm-run-all or similar)
npm run dev:all
```

## Deployment Commands (Story 1.6)

**Staging Deployment** (via CI/CD):
```bash
git push origin develop  # Triggers GitHub Actions → deploys to staging
```

**Production Deployment** (via CI/CD with manual approval):
```bash
git push origin main  # Triggers GitHub Actions → manual approval → deploys to production
```

**Manual Deployment** (if needed):
```bash
# SSH into EC2
ssh ec2-user@staging.news-cms.example.com

# Backend deployment
cd /var/www/news-cms/backend
git pull origin develop
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart news-cms-backend

# Frontend deployment (if SSR)
cd /var/www/news-cms/frontend
git pull origin develop
npm install
npm run build
sudo systemctl restart news-cms-frontend

# Check status
sudo systemctl status news-cms-backend
sudo systemctl status news-cms-frontend
```

## Debugging and Troubleshooting (Planned)

**Backend Logs**:
```bash
# Local
tail -f logs/app.log

# Production (CloudWatch)
aws logs tail /aws/news-cms/backend --follow
```

**Frontend Logs**:
```bash
# Local
npm run dev  # Logs to console

# Production
aws logs tail /aws/news-cms/frontend --follow
```

**MongoDB**:
```bash
# Connect to MongoDB
mongo mongodb://localhost:27017/news_cms_dev

# List collections
show collections

# Query triggers
db.triggers.find().pretty()

# Query active configurations
db.configurations.find({ is_active: true }).pretty()
```

**Common Issues** (To be documented as they arise):
- MongoDB connection timeout → Check AWS Security Group allows port 27017
- API key validation fails → Verify keys in Secrets Manager
- Frontend can't reach backend → Check Nginx config, CORS settings
- Generation timeout → Increase model timeout in config, check LLM API status
