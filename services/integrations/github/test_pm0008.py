"""
Simple test for PM-008 components
Run this in your working environment with: python simple_test.py
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_url_parsing():
    """Test URL parsing without GitHub API calls"""
    print("🔧 Testing URL parsing...")
    
    # Simple regex test without importing the full class
    import re
    
    def parse_github_url(url):
        clean_url = url.strip().lower()
        clean_url = re.sub(r'^https?://', '', clean_url)
        clean_url = re.sub(r'^www\.', '', clean_url)
        
        pattern = r'github\.com/([^/]+)/([^/]+)/(?:issues|pull)/(\d+)'
        match = re.match(pattern, clean_url)
        
        if match:
            owner, repo, issue_num = match.groups()
            return (owner, repo, int(issue_num))
        return None
    
    test_urls = [
        "https://github.com/microsoft/vscode/issues/12345",
        "github.com/microsoft/vscode/issues/67890", 
        "https://github.com/microsoft/vscode/pull/11111",
        "invalid-url"
    ]
    
    for url in test_urls:
        result = parse_github_url(url)
        status = "✅" if result else "❌"
        print(f"  {status} {url} -> {result}")

def check_environment():
    """Check if required environment variables are set"""
    print("\n🔑 Checking environment variables...")
    
    required_vars = ['GITHUB_TOKEN', 'ANTHROPIC_API_KEY', 'OPENAI_API_KEY']
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {'*' * min(len(value), 8)}...")
        else:
            print(f"  ❌ {var}: Not set")

def test_imports():
    """Test if we can import the required modules"""
    print("\n📦 Testing imports...")
    
    try:
        import github
        print("  ✅ PyGithub library available")
    except ImportError:
        print("  ❌ PyGithub not installed")
    
    try:
        import chromadb
        print("  ✅ ChromaDB library available") 
    except ImportError:
        print("  ❌ ChromaDB not installed")
    
    try:
        from dotenv import load_dotenv
        print("  ✅ python-dotenv available")
    except ImportError:
        print("  ❌ python-dotenv not installed")

def main():
    """Run basic tests"""
    print("🧪 PM-008 Basic Tests")
    print("=" * 40)
    
    test_url_parsing()
    check_environment()
    test_imports()
    
    print("\n" + "=" * 40)
    print("✨ Basic tests complete!")
    print("\nIf all tests pass, you can proceed to test with your actual services.")
    print("If any fail, install missing packages or set environment variables.")

if __name__ == "__main__":
    main()