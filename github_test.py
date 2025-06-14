#!/usr/bin/env python3
"""
Test PM-008 Integration with Main Chat Interface
"""
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_issue_analysis_intent():
    """Test that issue analysis requests get classified and routed correctly"""
    print("🧪 Testing PM-008 Chat Integration")
    print("=" * 50)
    
    try:
        from services.intent_service import classifier
        from services.orchestration import engine
        
        # Test messages that should trigger GitHub issue analysis
        test_messages = [
            "analyze this issue: https://github.com/microsoft/vscode/issues/196590",
            "review this GitHub issue: https://github.com/microsoft/vscode/issues/1", 
            "check this issue https://github.com/microsoft/vscode/issues/196590",
            "can you analyze https://github.com/microsoft/vscode/issues/1"
        ]
        
        for message in test_messages:
            print(f"\n📝 Testing: {message[:60]}...")
            
            # Step 1: Classify intent
            intent = await classifier.classify(message)
            print(f"   Intent: {intent.category.value} | {intent.action}")
            print(f"   Confidence: {intent.confidence:.2f}")
            
            # Step 2: Create workflow
            workflow = await engine.create_workflow_from_intent(intent)
            
            if workflow:
                print(f"   ✅ Workflow created: {workflow.type.value}")
                print(f"   Tasks: {[task.name for task in workflow.tasks]}")
                
                # Check if it would route to GitHub analysis
                if workflow.type.value == "review_issue" and workflow.tasks:
                    print(f"   🎯 Would route to GitHub issue analysis!")
                else:
                    print(f"   ⚠️  Unexpected routing: {workflow.type.value}")
            else:
                print(f"   ❌ No workflow created")
        
        print("\n" + "=" * 50)
        print("🎯 Integration Test Complete!")
        print("\nNext: Test full execution through main.py API")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_issue_analysis_intent())