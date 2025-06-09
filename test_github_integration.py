"""
Test GitHub integration for PM-008
Run this to verify GitHub API connectivity and issue fetching
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project path (adjust if needed)
sys.path.append('.')

async def test_github_connection():
    """Test basic GitHub API connection"""
    print("🐙 Testing GitHub API connection...")
    
    try:
        # Import your existing GitHubAgent
        # First, let's try to import and use your current agent
        from services.integrations.github.github_agent import GitHubAgent
        
        agent = GitHubAgent()
        
        # Test connection
        conn_result = agent.test_connection()
        if conn_result['success']:
            print(f"  ✅ Connected as: {conn_result['user']} ({conn_result['name']})")
            print(f"     Public repos: {conn_result['repos_count']}")
        else:
            print(f"  ❌ Connection failed: {conn_result['error']}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        print("     Make sure you're running from the project root directory")
        return False
    except Exception as e:
        print(f"  ❌ GitHub connection failed: {e}")
        return False

async def test_issue_fetching():
    """Test fetching a public GitHub issue"""
    print("\n📥 Testing issue fetching...")
    
    try:
        from services.integrations.github.github_agent import GitHubAgent
        
        agent = GitHubAgent()
        
        # Test with a well-known public issue
        test_url = "https://github.com/microsoft/vscode/issues/1"
        print(f"  Fetching: {test_url}")
        
        # Check if your agent has the new get_issue_by_url method
        if hasattr(agent, 'get_issue_by_url'):
            result = await agent.get_issue_by_url(test_url)
        else:
            print("  ⚠️  get_issue_by_url method not found - using fallback")
            # Parse URL manually and use existing methods if available
            parsed = agent.parse_github_url(test_url) if hasattr(agent, 'parse_github_url') else None
            if parsed:
                owner, repo, issue_num = parsed
                result = await agent.get_issue(f"{owner}/{repo}", issue_num) if hasattr(agent, 'get_issue') else {"success": False, "error": "get_issue method not found"}
            else:
                result = {"success": False, "error": "URL parsing failed"}
        
        if result['success']:
            issue = result['issue']
            print(f"  ✅ Success! Issue #{issue['number']}: {issue['title'][:60]}...")
            print(f"     State: {issue['state']} | Labels: {len(issue.get('labels', []))}")
            print(f"     Body length: {len(issue.get('body', ''))} chars")
            return True
        else:
            print(f"  ❌ Failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"  ❌ Issue fetching failed: {e}")
        return False

async def test_knowledge_search():
    """Test knowledge base search functionality"""
    print("\n🧠 Testing knowledge base search...")
    
    try:
        from services.knowledge_graph.ingestion import get_ingester
        
        knowledge = get_ingester()
        
        # Test search for PM-related content
        results = await knowledge.search_with_context(
            query="GitHub issue best practices user story acceptance criteria",
            n_results=3
        )
        
        print(f"  ✅ Knowledge search returned {len(results)} results")
        
        for i, result in enumerate(results[:2]):  # Show first 2
            print(f"     {i+1}. Score: {result.get('combined_score', 'N/A'):.2f}")
            print(f"        Content: {result['content'][:80]}...")
            print(f"        Metadata: {result['metadata'].get('document_type', 'unknown')}")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"  ❌ Knowledge search failed: {e}")
        print(f"     This might be OK if PM-007 knowledge base isn't set up yet")
        return False

async def main():
    """Run GitHub integration tests"""
    print("🧪 PM-008 GitHub Integration Tests")
    print("=" * 50)
    
    github_ok = await test_github_connection()
    issue_ok = await test_issue_fetching() if github_ok else False
    knowledge_ok = await test_knowledge_search()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"  GitHub API: {'✅ Ready' if github_ok else '❌ Issues'}")
    print(f"  Issue fetching: {'✅ Ready' if issue_ok else '❌ Issues'}")
    print(f"  Knowledge search: {'✅ Ready' if knowledge_ok else '⚠️ Not ready'}")
    
    if github_ok and issue_ok:
        print("\n🎯 Ready for full PM-008 testing!")
        print("   Next: Test the complete issue analyzer")
    else:
        print("\n🔧 Fix the above issues before proceeding")

if __name__ == "__main__":
    asyncio.run(main())