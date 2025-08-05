#!/usr/bin/env python3
"""
Setup script for integrating SearXNG with FacTool
This script helps configure and test the integration
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path

def check_searxng_running(url="http://localhost:8080"):
    """Check if SearXNG is running"""
    try:
        import requests
        response = requests.get(f"{url}/config", timeout=5)
        return response.status_code == 200
    except:
        return False

def setup_environment():
    """Setup environment variables for SearXNG integration"""
    print("Setting up environment for SearXNG integration...")
    
    # Set environment variables
    os.environ['FACTOOL_USE_SEARXNG'] = 'true'
    
    searxng_url = input("Enter your SearXNG URL (default: http://localhost:8080): ").strip()
    if not searxng_url:
        searxng_url = "http://localhost:8080"
    
    os.environ['SEARXNG_URL'] = searxng_url
    
    print(f"Environment configured:")
    print(f"  FACTOOL_USE_SEARXNG=true")
    print(f"  SEARXNG_URL={searxng_url}")
    
    return searxng_url

def create_env_file():
    """Create a .env file for persistent configuration"""
    searxng_url = os.environ.get('SEARXNG_URL', 'http://localhost:8080')
    
    env_content = f"""# FacTool SearXNG Configuration
FACTOOL_USE_SEARXNG=true
SEARXNG_URL={searxng_url}

# OpenAI API Key (still needed)
OPENAI_API_KEY=your_openai_key_here
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("Created .env file with configuration")

async def test_integration():
    """Test the SearXNG integration"""
    print("\nTesting SearXNG integration...")
    
    try:
        # Import and test SearXNG wrapper
        from factool.knowledge_qa.searxng_wrapper import SearXNGAPIWrapper
        
        searxng = SearXNGAPIWrapper(snippet_cnt=5)
        
        # Test search
        test_queries = [["What is machine learning?", "machine learning definition"]]
        results = await searxng.run(test_queries)
        
        print(f"✓ SearXNG search successful! Found {len(results[0])} results")
        for i, result in enumerate(results[0][:2]):  # Show first 2 results
            print(f"  Result {i+1}: {result['content'][:100]}...")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("Make sure searxng_wrapper.py is in the factool/knowledge_qa/ directory")
        return False
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

async def test_factool_integration():
    """Test full FacTool integration"""
    print("\nTesting full FacTool integration...")
    
    try:
        from factool import Factool
        
        # Test with a simple KBQA example
        factool_instance = Factool("gpt-3.5-turbo")  # Using cheaper model for testing
        
        inputs = [
            {
                "prompt": "Who is the president of the United States?",
                "response": "The president of the United States is Joe Biden.",
                "category": "kbqa"
            }
        ]
        
        print("Running FacTool with SearXNG backend...")
        results = await asyncio.get_event_loop().run_in_executor(
            None, factool_instance.run, inputs
        )
        
        print("✓ FacTool integration successful!")
        print(f"  Factuality score: {results.get('average_claim_level_factuality', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"✗ FacTool integration test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("=" * 50)
    print("FacTool SearXNG Integration Setup")
    print("=" * 50)
    
    # Check if SearXNG is running
    searxng_url = setup_environment()
    
    if not check_searxng_running(searxng_url):
        print(f"\n⚠️  Warning: Cannot connect to SearXNG at {searxng_url}")
        print("Please make sure SearXNG is running before proceeding.")
        
        choice = input("Continue anyway? (y/n): ").lower()
        if choice != 'y':
            print("Setup cancelled.")
            return
    else:
        print(f"✓ SearXNG is running at {searxng_url}")
    
    # Create environment file
    create_env_file()
    
    # Test integration
    print("\nRunning integration tests...")
    
    # Test async components
    loop = asyncio.get_event_loop()
    
    searxng_test = loop.run_until_complete(test_integration())
    
    if searxng_test:
        print("\n✓ SearXNG integration is working!")
        
        # Ask if user wants to test full FacTool integration
        if input("\nTest full FacTool integration? (requires OpenAI API key) (y/n): ").lower() == 'y':
            openai_key = input("Enter your OpenAI API key: ").strip()
            if openai_key:
                os.environ['OPENAI_API_KEY'] = openai_key
                factool_test = loop.run_until_complete(test_factool_integration())
                if factool_test:
                    print("\n🎉 Full integration successful!")
                else:
                    print("\n❌ FacTool integration failed. Check your OpenAI API key and try again.")
    else:
        print("\n❌ SearXNG integration failed. Please check your setup.")
    
    print("\n" + "=" * 50)
    print("Setup complete!")
    print("\nTo use SearXNG with FacTool, make sure:")
    print("1. SearXNG is running")
    print("2. Environment variables are set (or load from .env file)")
    print("3. Your OpenAI API key is configured")
    print("\nExample usage:")
    print("  export FACTOOL_USE_SEARXNG=true")
    print("  export SEARXNG_URL=http://localhost:8080")
    print("  python your_factool_script.py")

if __name__ == "__main__":
    main()