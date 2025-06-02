# Piper Morgan Platform

An intelligent product management assistant that evolves from automating routine tasks to providing strategic insights and recommendations.

## 🎯 Vision

Piper Morgan aims to be more than a task automation tool. It's designed to grow from a helpful PM intern into a strategic thinking partner, handling everything from creating tickets to analyzing market trends and suggesting product strategies.

## 🏗️ Architecture Overview

This platform is built on a microservices architecture with the following core principles:

- **Domain-Driven Design**: PM concepts drive the architecture, not tool integrations
- **Event-Driven**: All services communicate through events for scalability and learning
- **Plugin Architecture**: Every external system (GitHub, Jira, Slack) is a plugin
- **AI-Native**: LLMs provide reasoning capabilities, not just text generation
- **Learning-Centric**: Every interaction teaches the system something new

### Core Services

1. **Intent & Goal Management Service**: Understands what users want to achieve
2. **Orchestration Engine**: Plans and coordinates complex workflows
3. **Reasoning Service**: Provides analysis, insights, and recommendations
4. **Knowledge Graph Service**: Maintains understanding of products, features, and relationships
5. **Integration Services**: Plugins for GitHub, Jira, Confluence, Analytics, etc.
6. **Learning Service**: Captures patterns and improves over time

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 14+
- Redis 7+
- Node.js 18+ (for frontend development)

### Local Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/piper-morgan-platform.git
cd piper-morgan-platform

# Set up Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Copy environment template
cp .env.example .env
# Edit .env with your API keys and configuration

# Start infrastructure services
docker-compose up -d postgres redis

# Run database migrations
python scripts/migrate.py

# Start the development server
python scripts/dev-server.py
Running Tests
bash# Run all tests
pytest

# Run specific service tests
pytest services/intent-service/tests/

# Run with coverage
pytest --cov=services --cov-report=html
📁 Project Structure
piper-morgan-platform/
├── services/                 # Microservices
│   ├── domain/              # Core domain models and logic
│   ├── intent-service/      # Intent recognition
│   ├── orchestration-engine/# Workflow planning and execution
│   ├── reasoning-service/   # AI-powered analysis
│   ├── knowledge-graph/     # Knowledge management
│   └── integrations/        # External system plugins
│       ├── github/
│       ├── jira/
│       └── slack/
├── infrastructure/          # Deployment and configuration
│   ├── docker/             # Dockerfiles
│   ├── k8s/                # Kubernetes manifests
│   └── terraform/          # Infrastructure as code
├── shared/                 # Shared libraries
│   ├── contracts/          # Service contracts/interfaces
│   ├── utils/             # Common utilities
│   └── events/             # Event definitions
├── frontend/               # User interfaces
│   ├── web-app/           # Main web application
│   └── cli/               # Command-line interface
├── docs/                   # Documentation
│   ├── architecture/       # Architecture decisions
│   ├── api/               # API documentation
│   └── poc-reference/     # Lessons from POC
└── scripts/               # Development and deployment scripts
🛠️ Development Workflow
Creating a New Service
bash# Use the service template
./scripts/create-service.sh my-new-service

# This creates:
# - services/my-new-service/
# - Basic service structure
# - Dockerfile
# - Tests
# - README
Adding a New Integration
bash# Use the integration template
./scripts/create-integration.sh asana

# This creates:
# - services/integrations/asana/
# - Plugin interface implementation
# - Authentication handling
# - Basic API client
📊 Current Status
Phase 1: Foundation (In Progress)

 Architecture design
 Domain model definition
 Core infrastructure setup
 Basic service scaffolding
 CI/CD pipeline

Phase 2: Core Capabilities (Upcoming)

 Intent recognition service
 GitHub integration
 Basic orchestration
 Simple web UI

Phase 3: Intelligence Layer (Future)

 Reasoning service
 Knowledge graph
 Learning mechanisms
 Analytics integration

🤝 Contributing
We're not yet accepting external contributions, but team members should:

Create feature branches from develop
Follow the coding standards in docs/coding-standards.md
Ensure all tests pass
Update documentation as needed
Create PR with clear description

📚 Documentation

Architecture Overview
Domain Model
API Documentation
Deployment Guide
POC Lessons Learned

🔒 Security

All API keys and secrets must be in environment variables
Never commit .env files
Use the provided pre-commit hooks
See Security Guidelines for more

📝 License
This project is proprietary and confidential. All rights reserved.
🙏 Acknowledgments

Original POC team for proving the concept
Claude (Anthropic) for development assistance
The broader PM community for inspiration


Note: This is v1.0 of a complete platform rebuild. For the original proof-of-concept, see the archived piper-morgan-poc repository.
