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
