# Piper Morgan 1.0 - Deployment Guide

## Infrastructure Requirements

### System Requirements
- **CPU**: 2+ cores
- **Memory**: 4GB+ RAM
- **Storage**: 20GB+ available space
- **Network**: Internet access for AI APIs

### Software Dependencies
- Docker 20.10+
- Docker Compose 2.0+
- Git

## Local Deployment

### Quick Start
```bash
# Clone repository
git clone <repository-url>
cd piper-morgan-platform

# Configure environment
cp .env.example .env
# Edit .env with required API keys:
# - ANTHROPIC_API_KEY
# - OPENAI_API_KEY
# - GITHUB_TOKEN

# Deploy infrastructure
docker-compose up -d

# Initialize database (CRITICAL - currently required)
# Note: Database initialization script needed
python scripts/init_db.py

# Verify deployment
curl http://localhost:8001/health
```

### Service Configuration

#### Environment Variables
```bash
# AI Services
ANTHROPIC_API_KEY=your_claude_key
OPENAI_API_KEY=your_openai_key

# External Integrations
GITHUB_TOKEN=your_github_token

# Database Configuration
POSTGRES_USER=piper
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=piper_morgan

# Application Settings
LOG_LEVEL=INFO
DEBUG=false
```

#### Docker Compose Services
- **postgres**: Primary database
- **redis**: Event queue and caching
- **chromadb**: Vector database for knowledge
- **temporal**: Workflow orchestration
- **traefik**: API gateway

### Verification Steps
1. Check service health: `docker-compose ps`
2. Verify API endpoint: `curl http://localhost:8001/health`
3. Test intent processing: `curl -X POST http://localhost:8001/api/v1/intent -d '{"message":"test"}'`
4. Check database connectivity: `docker-compose exec postgres psql -U piper -d piper_morgan`

## Production Considerations

### Security
- Change default passwords
- Configure SSL/TLS termination
- Implement proper access controls
- Set up API rate limiting

### Monitoring
- Application performance monitoring
- Database monitoring
- Log aggregation and analysis
- Health check endpoints

### Backup
- Database backup procedures
- Knowledge base backup
- Configuration backup
- Disaster recovery planning

### Scaling
- Horizontal scaling considerations
- Load balancing configuration
- Database connection pooling
- Resource monitoring and alerting

## Troubleshooting

### Common Issues
1. **Database not initialized**: Run `python scripts/init_db.py`
2. **API keys missing**: Check `.env` configuration
3. **Service startup failures**: Check `docker-compose logs <service>`
4. **Port conflicts**: Ensure ports 8001, 5432, 6379, 8000 available

### Debug Commands
```bash
# Check service logs
docker-compose logs -f app

# Access database
docker-compose exec postgres psql -U piper -d piper_morgan

# Check Redis
docker-compose exec redis redis-cli ping

# View ChromaDB
curl http://localhost:8000/api/v1/collections
```

For operational monitoring, see [Monitoring Guide](monitoring.md).
