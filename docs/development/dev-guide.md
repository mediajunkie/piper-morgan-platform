# Piper Morgan 1.0 - Development Guide

## Getting Started

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Git
- VS Code (recommended)

### Local Setup
```bash
# Clone repository
git clone <repository-url>
cd piper-morgan-platform

# Start infrastructure services
docker-compose up -d

# Set up Python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Development Workflow
1. Create feature branch from main
2. Implement changes following architecture patterns
3. Test locally with Docker Compose
4. Update documentation as needed
5. Submit pull request

### Code Structure
```
services/
├── domain/          # Core business logic
├── intent_service/  # Natural language processing
├── orchestration/   # Workflow management
├── knowledge/       # Knowledge base management
├── integrations/    # External system plugins
└── api/            # Web API endpoints
```

### Testing
```bash
# Run all tests
pytest

# Run specific service tests
pytest services/intent_service/tests/

# Run with coverage
pytest --cov=services
```

### Common Tasks
- **Add new workflow**: Implement in `services/orchestration/workflows/`
- **Add external integration**: Create plugin in `services/integrations/`
- **Update domain model**: Modify `services/domain/models.py`
- **Add API endpoint**: Update `services/api/routes/`

For detailed technical information, see [Technical Specification](../architecture/technical-spec.md).

## Environment Variables Checklist

When creating new services that need API keys or config:

✅ **Always add `load_dotenv()` at the top of modules that use `os.getenv()`**
✅ **Import pattern**: `from dotenv import load_dotenv; load_dotenv()`
✅ **Place before any `os.getenv()` calls**
✅ **Test with fresh terminal/environment to catch missing env loading**

### Common Modules That Need This:
- LLM clients (Claude, OpenAI)
- Database connections
- External API integrations
- Knowledge/embedding services

