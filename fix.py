python3 -c "
import os
import re

# Fix the Intent dataclass parameter order issue
file_path = 'services/domain/models.py'

with open(file_path, 'r') as f:
    content = f.read()

# Find and fix the Intent class
# The issue is that id has a default factory but category doesn't have a default
# In dataclasses, all fields with defaults must come after fields without defaults

old_intent = '''@dataclass
class Intent:
    \"\"\"User intent parsed from natural language\"\"\"
    id: str = field(default_factory=lambda: str(uuid4()))
    category: IntentCategory
    action: str
    context: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)'''

new_intent = '''@dataclass
class Intent:
    \"\"\"User intent parsed from natural language\"\"\"
    category: IntentCategory
    action: str
    id: str = field(default_factory=lambda: str(uuid4()))
    context: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)'''

# Replace the problematic Intent class
if 'category: IntentCategory' in content and 'id: str = field(default_factory=lambda: str(uuid4()))' in content:
    # Find the Intent class and fix the field order
    lines = content.split('\n')
    in_intent_class = False
    intent_start = -1
    intent_end = -1
    
    for i, line in enumerate(lines):
        if 'class Intent:' in line:
            in_intent_class = True
            intent_start = i
        elif in_intent_class and line and not line.startswith(' ') and not line.startswith('\t'):
            intent_end = i
            break
    
    if intent_start >= 0:
        if intent_end == -1:
            intent_end = len(lines)
        
        # Replace the Intent class definition
        intent_lines = [
            '@dataclass',
            'class Intent:',
            '    \"\"\"User intent parsed from natural language\"\"\"',
            '    category: IntentCategory',
            '    action: str',
            '    id: str = field(default_factory=lambda: str(uuid4()))',
            '    context: Dict[str, Any] = field(default_factory=dict)',
            '    confidence: float = 0.0',
            '    created_at: datetime = field(default_factory=datetime.now)'
        ]
        
        # Find the actual start of the Intent class (skip @dataclass line)
        actual_start = intent_start
        if lines[intent_start-1].strip() == '@dataclass':
            actual_start = intent_start - 1
            
        # Replace the lines
        lines[actual_start:intent_end] = intent_lines
        
        # Write back
        fixed_content = '\n'.join(lines)
        with open(file_path, 'w') as f:
            f.write(fixed_content)
            
        print('✅ Fixed Intent class parameter order')
    else:
        print('❌ Could not find Intent class to fix')
else:
    print('❌ Intent class structure not as expected')

# Test the fix
try:
    import sys
    sys.path.insert(0, 'services')
    from domain.models import Intent, IntentCategory
    
    # Test creating an Intent
    intent = Intent(category=IntentCategory.EXECUTION, action='test')
    print(f'✅ Intent creation successful: {intent.id[:8]}')
    
    # Test all other imports
    from domain.models import Workflow, WorkflowType, WorkflowStatus
    workflow = Workflow(type=WorkflowType.CREATE_TICKET)
    print(f'✅ All model imports successful')
    
except Exception as e:
    print(f'❌ Import test failed: {e}')
"
