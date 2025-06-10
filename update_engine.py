import re

# Read the current file
with open('services/orchestration/engine.py', 'r') as f:
    content = f.read()

# Add imports after existing imports
import_pattern = r'(from services\.domain\.models import.*?\n)'
new_imports = r'\1from services.repositories import DatabasePool\nfrom services.repositories.workflow_repository import WorkflowRepository\n'
content = re.sub(import_pattern, new_imports, content)

# Replace the method
method_pattern = r'async def create_workflow_from_intent\(self.*?return workflow'
new_method = '''async def create_workflow_from_intent(self, intent: Intent) -> Optional[Workflow]:
    """Create appropriate workflow based on intent with database persistence"""
    # ... new implementation ...
    return workflow'''
content = re.sub(method_pattern, new_method, content, flags=re.DOTALL)

# Write back
with open('services/orchestration/engine.py', 'w') as f:
    f.write(content)
print("✅ Updated engine.py")
