#!/bin/bash

# Piper Morgan 1.0 - Documentation Generator Script
# Creates comprehensive documentation structure for AI PM Assistant project
# Date: June 6, 2025

set -e  # Exit on any error

# Configuration
PROJECT_NAME="piper-morgan-platform"
DOCS_DIR="docs"
DATE=$(date +"%Y-%m-%d")
VERSION="1.0.0"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to create directory structure
create_docs_structure() {
    print_status "Creating documentation directory structure..."
    
    # Main docs directory
    mkdir -p "$DOCS_DIR"
    
    # Subdirectories
    mkdir -p "$DOCS_DIR/architecture"
    mkdir -p "$DOCS_DIR/development"
    mkdir -p "$DOCS_DIR/operations"
    mkdir -p "$DOCS_DIR/user-guides"
    mkdir -p "$DOCS_DIR/api"
    mkdir -p "$DOCS_DIR/presentations"
    mkdir -p "$DOCS_DIR/assets"
    
    print_success "Directory structure created"
}

# Function to generate main README
generate_main_readme() {
    print_status "Generating main README.md..."
    
    cat > "$DOCS_DIR/README.md" << 'EOF'
# Piper Morgan 1.0 - Documentation

*AI-Powered Product Management Assistant - June 6, 2025*

## 📚 Documentation Overview

This documentation provides comprehensive information about the Piper Morgan AI PM Assistant platform, including architecture, development guides, and operational procedures.

## 🗂️ Document Structure

### Executive Documents
- **[One-Page Summary](one-pager.md)** - Executive overview of current state and capabilities
- **[Vision Statement](vision.md)** - Long-term product vision and strategic direction
- **[Project Report](project-report.md)** - Development journey and lessons learned

### Technical Documentation
- **[Architecture Overview](architecture/architecture.md)** - System design and component analysis
- **[Technical Specification](architecture/technical-spec.md)** - Detailed implementation specifications
- **[Requirements Document](architecture/requirements.md)** - Functional and non-functional requirements

### Development Resources
- **[Product Roadmap](development/roadmap.md)** - Feature timeline and development priorities
- **[Feature Backlog](development/backlog.md)** - Detailed feature requirements and story points
- **[Development Guide](development/dev-guide.md)** - Setup and contribution instructions

### Operations & Deployment
- **[Deployment Guide](operations/deployment.md)** - Infrastructure setup and configuration
- **[Monitoring Guide](operations/monitoring.md)** - System monitoring and troubleshooting
- **[Security Guide](operations/security.md)** - Security practices and procedures

### User Documentation
- **[User Guide](user-guides/user-guide.md)** - End-user instructions and workflows
- **[API Documentation](api/api-reference.md)** - REST API reference and examples
- **[Configuration Guide](user-guides/configuration.md)** - System configuration options

### Presentations & Assets
- **[Team Presentation](presentations/team-all-hands.html)** - Interactive presentation for stakeholders
- **[Demo Materials](presentations/)** - Demo scripts and presentation materials

## 🚀 Quick Start

### For Users
1. Review the [One-Page Summary](one-pager.md) for current capabilities
2. Follow the [User Guide](user-guides/user-guide.md) for setup instructions
3. Check [API Documentation](api/api-reference.md) for integration details

### For Developers
1. Read the [Architecture Overview](architecture/architecture.md)
2. Follow the [Development Guide](development/dev-guide.md)
3. Review the [Feature Backlog](development/backlog.md) for contribution opportunities

### For Operations
1. Use the [Deployment Guide](operations/deployment.md) for infrastructure setup
2. Implement [Monitoring Guide](operations/monitoring.md) procedures
3. Follow [Security Guide](operations/security.md) best practices

## 📊 Current Status

**Development Phase**: Foundation Complete, Implementation Gaps Remain
**User Readiness**: Not ready for production use
**Architecture Status**: Solid foundation, core functionality incomplete

See [One-Page Summary](one-pager.md) for detailed current state assessment.

## 🔄 Document Maintenance

This documentation is maintained alongside code development. Major updates occur:
- **Weekly**: Development progress and backlog updates
- **Monthly**: Architecture and roadmap reviews
- **Quarterly**: Strategic vision and requirements assessment

## 📞 Contact & Support

For questions about this documentation or the Piper Morgan platform:
- **Technical Questions**: Review architecture and development docs
- **User Support**: Check user guides and API documentation
- **Strategic Direction**: See vision and roadmap documents

---

*Last Updated: June 6, 2025 | Version: 1.0.0 | Status: Foundation Phase*
EOF

    print_success "Main README.md generated"
}

# Function to copy documents to appropriate directories
organize_documents() {
    print_status "Organizing documents into directory structure..."
    
    # Check if source documents exist (would be provided separately)
    print_warning "Note: Document content should be copied from source files:"
    
    # Executive documents (root level)
    echo "  - one-pager.md → docs/"
    echo "  - vision.md → docs/"
    echo "  - project-report.md → docs/"
    
    # Architecture documents
    echo "  - architecture.md → docs/architecture/"
    echo "  - technical-spec.md → docs/architecture/"
    echo "  - requirements.md → docs/architecture/"
    
    # Development documents
    echo "  - roadmap.md → docs/development/"
    echo "  - backlog.md → docs/development/"
    
    # Presentations
    echo "  - team-all-hands.html → docs/presentations/"
    
    print_warning "Manual copy required - script cannot access document content directly"
}

# Function to generate development guide
generate_dev_guide() {
    print_status "Generating development guide..."
    
    cat > "$DOCS_DIR/development/dev-guide.md" << 'EOF'
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
EOF

    print_success "Development guide generated"
}

# Function to generate deployment guide
generate_deployment_guide() {
    print_status "Generating deployment guide..."
    
    cat > "$DOCS_DIR/operations/deployment.md" << 'EOF'
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
EOF

    print_success "Deployment guide generated"
}

# Function to generate API documentation
generate_api_docs() {
    print_status "Generating API documentation..."
    
    cat > "$DOCS_DIR/api/api-reference.md" << 'EOF'
# Piper Morgan 1.0 - API Reference

## Base URL
```
http://localhost:8001
```

## Authentication
Currently no authentication required (development mode).
Production deployment will require API key or OAuth authentication.

## Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
    "status": "healthy",
    "services": {
        "postgres": "connected",
        "redis": "connected",
        "chromadb": "connected",
        "temporal": "connected",
        "llm": "ready"
    }
}
```

### Process Intent
```http
POST /api/v1/intent
Content-Type: application/json

{
    "message": "Create a ticket for the login bug affecting mobile users"
}
```

**Response:**
```json
{
    "intent": {
        "category": "execution",
        "action": "create_github_issue",
        "confidence": 0.95,
        "context": {...}
    },
    "response": "I'll create a GitHub issue for the mobile login bug...",
    "workflow_id": "uuid-here"
}
```

### Get Workflow Status
```http
GET /api/v1/workflows/{workflow_id}
```

**Response:**
```json
{
    "workflow_id": "uuid",
    "status": "completed",
    "type": "create_ticket",
    "result": {...},
    "message": "GitHub issue created successfully"
}
```

### List Workflows
```http
GET /api/v1/workflows
```

**Response:**
```json
{
    "workflows": [
        {
            "id": "uuid",
            "type": "create_ticket",
            "status": "completed",
            "created_at": "2025-06-06T10:00:00Z"
        }
    ]
}
```

### Knowledge Base Search
```http
GET /api/v1/knowledge/search?q=mobile+login&k=5
```

**Response:**
```json
{
    "results": [
        {
            "content": "...",
            "metadata": {...},
            "score": 0.85
        }
    ]
}
```

## Error Responses

### Standard Error Format
```json
{
    "error": "error_code",
    "message": "Human readable error message",
    "details": {...}
}
```

### Common Error Codes
- `400`: Bad Request - Invalid input
- `404`: Not Found - Resource doesn't exist
- `500`: Internal Server Error - System error
- `502`: Bad Gateway - External service unavailable

## Usage Examples

### Python
```python
import requests

# Process intent
response = requests.post(
    "http://localhost:8001/api/v1/intent",
    json={"message": "Create issue for mobile bug"}
)
result = response.json()
workflow_id = result.get("workflow_id")

# Check workflow status
status = requests.get(f"http://localhost:8001/api/v1/workflows/{workflow_id}")
print(status.json())
```

### curl
```bash
# Process intent
curl -X POST http://localhost:8001/api/v1/intent \
  -H "Content-Type: application/json" \
  -d '{"message":"Create issue for mobile bug"}'

# Check workflow status
curl http://localhost:8001/api/v1/workflows/{workflow_id}
```

## WebSocket Events (Future)
Real-time workflow updates will be available via WebSocket:
```
ws://localhost:8001/ws/workflows/{workflow_id}
```

Event types:
- `workflow.status_changed`
- `workflow.completed`
- `workflow.failed`

For integration patterns, see [User Guide](../user-guides/user-guide.md).
EOF

    print_success "API documentation generated"
}

# Function to generate user guide
generate_user_guide() {
    print_status "Generating user guide..."
    
    cat > "$DOCS_DIR/user-guides/user-guide.md" << 'EOF'
# Piper Morgan 1.0 - User Guide

## Getting Started

### System Requirements
- Web browser (Chrome, Firefox, Safari, Edge)
- Internet connection for AI services
- GitHub account for issue creation

### Current Limitations
⚠️ **Important**: Piper Morgan is currently in development phase with significant limitations:
- No web UI (API-only interaction)
- Database persistence issues (workflows lost on restart)
- GitHub integration not implemented
- Single-user system only

### Access Methods

#### API Access (Current)
The system currently requires API calls for all interactions:

```bash
# Test system health
curl http://localhost:8001/health

# Submit a request
curl -X POST http://localhost:8001/api/v1/intent \
  -H "Content-Type: application/json" \
  -d '{"message":"Create a GitHub issue for mobile app login problems"}'
```

#### Web Interface (Planned)
Future versions will include:
- Chat-based web interface
- File upload for documents
- Real-time workflow status
- User authentication and preferences

## Core Capabilities

### 1. Natural Language Intent Understanding
Piper Morgan can interpret PM requests like:
- "Create a ticket for the login bug affecting mobile users"
- "Review the requirements document and summarize key points"
- "What were the main decisions from the Q3 retrospective?"

**Quality Note**: Intent classification accuracy varies 60-85% depending on request clarity.

### 2. Knowledge Base Integration
The system can:
- Ingest documents (PDF, DOCX, TXT, MD)
- Search organizational knowledge for context
- Reference historical decisions and documentation

**Quality Note**: Search relevance inconsistent and requires tuning.

### 3. Workflow Orchestration (Planned)
When complete, the system will:
- Create GitHub issues from natural language
- Execute multi-step PM workflows
- Coordinate across multiple external systems

**Status**: Framework exists but execution loop incomplete.

## Usage Patterns

### Document Upload and Knowledge Building
```bash
# Upload document (when web UI available)
# Currently requires manual file placement in knowledge base directory
```

### GitHub Issue Creation
```bash
# Request issue creation
curl -X POST http://localhost:8001/api/v1/intent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Users report that the mobile app crashes when uploading photos larger than 10MB. This affects iOS and Android. Priority should be high since it blocks core functionality."
  }'
```

Expected output (when GitHub integration complete):
- Professional GitHub issue title
- Structured description with acceptance criteria
- Appropriate labels and priority assignment
- Technical implementation guidance

### Knowledge Queries
```bash
# Query organizational knowledge
curl "http://localhost:8001/api/v1/knowledge/search?q=mobile+login+architecture&k=3"
```

## Best Practices

### Writing Effective Requests
**Good Examples:**
- "Create a bug report for mobile app crashes during photo upload on iOS, affecting 15% of users"
- "Review the API documentation and identify missing authentication requirements"

**Poor Examples:**
- "Fix the app" (too vague)
- "Create ticket" (missing context)

### Knowledge Base Management
1. **Document Quality**: Upload well-structured documents with clear headings
2. **Metadata**: Include project, date, and document type information
3. **Regular Updates**: Keep knowledge base current with recent decisions
4. **Curation**: Remove outdated or contradictory information

### Workflow Optimization
1. **Context Provision**: Include relevant background in requests
2. **Specificity**: Be specific about requirements and constraints
3. **Verification**: Always review AI-generated content before use
4. **Feedback**: Provide corrections to improve future suggestions

## Troubleshooting

### Common Issues
1. **System Unavailable**: Check if Docker services are running
2. **Slow Responses**: AI processing can take 3-6 seconds
3. **Irrelevant Results**: Knowledge base search quality varies
4. **Failed Workflows**: Workflow persistence currently broken

### Getting Help
1. Check system health: `curl http://localhost:8001/health`
2. Review Docker logs: `docker-compose logs`
3. Verify API keys in environment configuration
4. See [Deployment Guide](../operations/deployment.md) for setup issues

## Future Capabilities

### Planned Features
- **Web User Interface**: Chat-based interaction
- **Learning Mechanisms**: Improvement through user feedback
- **Multi-System Integration**: Jira, Slack, analytics platforms
- **Advanced Workflows**: Complex multi-step automation

### Long-term Vision
- **Strategic Insights**: AI-powered product recommendations
- **Predictive Analytics**: Timeline and risk prediction
- **Autonomous Operation**: Self-improving workflow execution
- **Organizational Learning**: Cross-team knowledge sharing

## Feedback and Support

### Providing Feedback
Current system limitations make user feedback collection manual:
1. Document specific issues encountered
2. Note accuracy of AI responses
3. Record time saved or lost using the system
4. Suggest specific improvements needed

### System Status
For current development status, see:
- [One-Page Summary](../one-pager.md) - Current capabilities and gaps
- [Roadmap](../development/roadmap.md) - Development timeline
- [Backlog](../development/backlog.md) - Detailed feature status

This user guide will be updated as system capabilities evolve and mature.
EOF

    print_success "User guide generated"
}

# Function to create placeholder files
create_placeholder_files() {
    print_status "Creating placeholder files..."
    
    # Architecture placeholders
    echo "# Monitoring Guide - To Be Developed" > "$DOCS_DIR/operations/monitoring.md"
    echo "# Security Guide - To Be Developed" > "$DOCS_DIR/operations/security.md"
    echo "# Configuration Guide - To Be Developed" > "$DOCS_DIR/user-guides/configuration.md"
    
    # Assets directory with README
    cat > "$DOCS_DIR/assets/README.md" << 'EOF'
# Assets Directory

This directory contains supporting assets for documentation:

- Images and diagrams
- Presentation materials
- Demo videos
- Template files
- Configuration examples

## File Organization
- `images/` - Screenshots, diagrams, and visual assets
- `templates/` - Document and configuration templates
- `demos/` - Demo scripts and materials
- `presentations/` - Slide decks and presentation materials
EOF

    print_success "Placeholder files created"
}

# Function to generate documentation index
generate_doc_index() {
    print_status "Generating documentation index..."
    
    cat > "$DOCS_DIR/doc-index.md" << 'EOF'
# Piper Morgan 1.0 - Documentation Index

## 📋 Quick Reference

| Document | Purpose | Audience | Status |
|----------|---------|----------|--------|
| [One-Pager](one-pager.md) | Executive summary | Leadership, Stakeholders | ✅ Complete |
| [Vision](vision.md) | Strategic direction | All teams | ✅ Complete |
| [Architecture](architecture/architecture.md) | System design | Technical teams | ✅ Complete |
| [Requirements](architecture/requirements.md) | Functional specs | Development, QA | ✅ Complete |
| [Technical Spec](architecture/technical-spec.md) | Implementation details | Developers | ✅ Complete |
| [Roadmap](development/roadmap.md) | Feature timeline | Product, Engineering | ✅ Complete |
| [Backlog](development/backlog.md) | Detailed features | Development team | ✅ Complete |
| [Project Report](project-report.md) | Development journey | All stakeholders | ✅ Complete |

## 🎯 By Use Case

### New to Piper Morgan?
1. Read [One-Pager](one-pager.md) for current state
2. Review [Vision](vision.md) for long-term direction
3. Check [User Guide](user-guides/user-guide.md) for usage

### Technical Implementation?
1. Study [Architecture Overview](architecture/architecture.md)
2. Review [Technical Specification](architecture/technical-spec.md)
3. Follow [Development Guide](development/dev-guide.md)

### Deployment & Operations?
1. Use [Deployment Guide](operations/deployment.md)
2. Implement [Monitoring Guide](operations/monitoring.md)
3. Follow [Security Guide](operations/security.md)

### Product Planning?
1. Review [Roadmap](development/roadmap.md)
2. Analyze [Feature Backlog](development/backlog.md)
3. Reference [Requirements Document](architecture/requirements.md)

## 📊 Documentation Health

### Completion Status
- **Executive Documents**: 100% complete
- **Technical Architecture**: 100% complete  
- **Development Guides**: 80% complete
- **Operations Guides**: 40% complete
- **User Documentation**: 60% complete

### Next Priorities
1. Complete monitoring and security operational guides
2. Develop comprehensive user onboarding materials
3. Create troubleshooting and FAQ documentation
4. Add video demos and tutorials

### Maintenance Schedule
- **Weekly**: Development progress updates
- **Monthly**: Architecture and roadmap review
- **Quarterly**: Strategic vision alignment

## 🔍 Search Guide

### Finding Information
- **Current Capabilities**: One-pager, user guide
- **Technical Details**: Architecture, technical spec
- **Implementation Status**: Project report, backlog
- **Future Plans**: Vision, roadmap
- **Getting Started**: User guide, deployment guide

### Document Relationships
```
Vision ─┬─> Roadmap ─┬─> Backlog ─┬─> Technical Spec
        │            │            │
        └─> Architecture ─────────┘
              │
              └─> Requirements ─┬─> Development Guide
                                │
                                └─> Deployment Guide
```

Last Updated: June 6, 2025
EOF

    print_success "Documentation index generated"
}

# Main execution function
main() {
    print_status "Starting Piper Morgan documentation generation..."
    print_status "Project: $PROJECT_NAME"
    print_status "Date: $DATE"
    print_status "Version: $VERSION"
    echo
    
    # Create directory structure
    create_docs_structure
    
    # Generate main documentation files
    generate_main_readme
    generate_dev_guide
    generate_deployment_guide
    generate_api_docs
    generate_user_guide
    generate_doc_index
    
    # Create supporting files
    create_placeholder_files
    
    # Show organization instructions
    organize_documents
    
    echo
    print_success "Documentation generation complete!"
    print_status "Directory structure created in: $DOCS_DIR/"
    echo
    print_warning "NEXT STEPS:"
    echo "1. Copy source documents to appropriate directories:"
    echo "   - one-pager.md, vision.md, project-report.md → docs/"
    echo "   - architecture.md, technical-spec.md, requirements.md → docs/architecture/"
    echo "   - roadmap.md, backlog.md → docs/development/"
    echo "   - team-all-hands.html → docs/presentations/"
    echo
    echo "2. Update README.md in project root to reference docs/"
    echo "3. Consider adding docs/ to version control"
    echo "4. Set up documentation hosting (GitHub Pages, etc.)"
    echo
    print_status "Documentation structure ready for content population!"
}

# Help function
show_help() {
    echo "Piper Morgan Documentation Generator"
    echo
    echo "Usage: $0 [options]"
    echo
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -d, --dir DIR  Specify docs directory (default: docs)"
    echo "  -v, --verbose  Verbose output"
    echo
    echo "This script creates a comprehensive documentation structure"
    echo "for the Piper Morgan AI PM Assistant project."
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -d|--dir)
            DOCS_DIR="$2"
            shift 2
            ;;
        -v|--verbose)
            set -x
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Execute main function
main
