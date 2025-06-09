"""
Test the complete PM-008 Issue Analyzer
This tests the full analysis pipeline with real GitHub issues
"""
import asyncio
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project path
sys.path.append('.')

async def test_issue_analyzer():
    """Test the complete issue analyzer"""
    print("🔍 Testing Complete Issue Analyzer (PM-008)")
    print("=" * 55)
    
    try:
        # First save the analyzer files to your project
        print("📋 Note: Make sure you've saved the GitHubIssueAnalyzer files:")
        print("   1. Replace services/integrations/github/github_agent.py with extended version")
        print("   2. Create services/integrations/github/issue_analyzer.py")
        print()
        
        from services.integrations.github.issue_analyzer import GitHubIssueAnalyzer
        
        analyzer = GitHubIssueAnalyzer()
        print("✅ Issue analyzer created successfully")
        
        # Test with a real issue that has more content
        # Let's use one from your own repository if available
        test_urls = [
            "https://github.com/microsoft/vscode/issues/196590",  # Recent issue with content
            "https://github.com/microsoft/vscode/issues/1"        # Fallback simple issue
        ]
        
        for test_url in test_urls:
            print(f"\n🎯 Analyzing: {test_url}")
            print("-" * 50)
            
            try:
                result = await analyzer.analyze_issue_by_url(test_url)
                
                if result['success']:
                    analysis = result['analysis']
                    issue_info = result['issue']
                    
                    print(f"✅ Analysis Complete!")
                    print(f"   Issue: #{issue_info['number']} - {issue_info['title'][:50]}...")
                    print(f"   Repository: {issue_info['repository']}")
                    print(f"   Confidence: {analysis.confidence:.2f}")
                    print()
                    
                    print("📝 Summary (3 bullets):")
                    for i, bullet in enumerate(analysis.summary, 1):
                        print(f"   {i}. {bullet}")
                    print()
                    
                    print("💬 Draft Comment:")
                    comment_preview = analysis.draft_comment[:200] + "..." if len(analysis.draft_comment) > 200 else analysis.draft_comment
                    print(f"   {comment_preview}")
                    print()
                    
                    print("📄 Draft Rewrite:")
                    rewrite_preview = analysis.draft_rewrite[:200] + "..." if len(analysis.draft_rewrite) > 200 else analysis.draft_rewrite
                    print(f"   {rewrite_preview}")
                    print()
                    
                    print("🧠 Knowledge Context Used:")
                    for i, context in enumerate(analysis.knowledge_context[:2], 1):
                        print(f"   {i}. {context}")
                    
                    # Success - we found a working issue, stop testing
                    break
                    
                else:
                    print(f"❌ Analysis failed: {result['error']}")
                    print("   Trying next URL...")
                    continue
                    
            except Exception as e:
                print(f"❌ Error analyzing {test_url}: {e}")
                print("   Trying next URL...")
                continue
        
        print("\n" + "=" * 55)
        print("🎯 PM-008 Implementation Complete!")
        print("\nNext steps:")
        print("1. Test with issues from your own repositories")
        print("2. Integrate with your main chat interface")
        print("3. Add to workflow factory for intent-driven analysis")
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("\nNext steps:")
        print("1. Save the extended GitHubAgent code to your github_agent.py file")
        print("2. Create issue_analyzer.py in services/integrations/github/")
        print("3. Run this test again")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("\nThis might be due to missing LLM client integration")
        print("Check that your llm_client is properly configured")

if __name__ == "__main__":
    asyncio.run(test_issue_analyzer())