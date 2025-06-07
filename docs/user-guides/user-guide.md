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
