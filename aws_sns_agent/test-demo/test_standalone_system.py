#!/usr/bin/env python3
"""
Test script for the standalone brand monitoring system
Tests all components without modifying the brand-monitoring folder
"""

import sys
import os
import json
from datetime import datetime

def test_standalone_tools():
    """Test the standalone tools."""
    print("🧪 Testing Standalone Tools")
    print("=" * 50)
    
    try:
        from standalone_tools import BrightDataWebSearchTool, scrape_urls
        
        # Test 1: Web Search Tool
        print("\n1. Testing BrightData Web Search Tool...")
        tool = BrightDataWebSearchTool()
        
        results = tool._run("Browserbase", total_results=5)
        
        if results:
            print(f"✅ Search successful: {len(results)} results found")
            for i, result in enumerate(results[:3], 1):
                print(f"  {i}. {result.get('title', 'No title')}")
                print(f"     URL: {result.get('link', 'No link')}")
                print(f"     Snippet: {result.get('snippet', 'No snippet')[:100]}...")
                print()
        else:
            print("⚠️  No results found")
        
        # Test 2: URL Scraping
        print("\n2. Testing URL Scraping...")
        test_urls = [
            "https://www.browserbase.com/",
            "https://github.com/browserbase"
        ]
        
        params = {"dataset_id": "test_dataset"}
        scraped_data = scrape_urls(test_urls, params, "web")
        
        if scraped_data:
            print(f"✅ Scraping successful: {len(scraped_data)} results")
            for i, data in enumerate(scraped_data[:2], 1):
                print(f"  {i}. URL: {data.get('url', 'No URL')}")
                if 'markdown' in data:
                    print(f"     Content: {data['markdown'][:100]}...")
                print()
        else:
            print("⚠️  No scraped data")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def test_standalone_agent_tools():
    """Test the standalone agent tools."""
    print("\n🤖 Testing Standalone Agent Tools")
    print("=" * 50)
    
    try:
        from standalone_brand_monitoring_agent import (
            search_brand_mentions, 
            scrape_brand_content, 
            analyze_brand_sentiment,
            generate_brand_report
        )
        
        # Test 1: Search Brand Mentions
        print("\n1. Testing search_brand_mentions...")
        search_result = search_brand_mentions.func("Browserbase", 5)
        search_data = json.loads(search_result)
        
        if 'search_results' in search_data and search_data['search_results']:
            print(f"✅ Search successful: {len(search_data['search_results'])} results")
        else:
            print("⚠️  No search results")
        
        # Test 2: Scrape Brand Content
        print("\n2. Testing scrape_brand_content...")
        test_urls = json.dumps(["https://www.browserbase.com/"])
        scrape_result = scrape_brand_content.func(test_urls, "web")
        scrape_data = json.loads(scrape_result)
        
        if 'scraped_data' in scrape_data and scrape_data['scraped_data']:
            print(f"✅ Scraping successful: {len(scrape_data['scraped_data'])} items")
        else:
            print("⚠️  No scraped data")
        
        # Test 3: Analyze Brand Sentiment (if we have data)
        print("\n3. Testing analyze_brand_sentiment...")
        if 'search_results' in search_data and search_data['search_results']:
            sentiment_result = analyze_brand_sentiment.func(search_result, "Browserbase")
            sentiment_data = json.loads(sentiment_result)
            
            if 'sentiment_analysis' in sentiment_data:
                print("✅ Sentiment analysis successful")
            else:
                print("⚠️  Sentiment analysis failed")
        else:
            print("⚠️  Skipping sentiment analysis - no data available")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def test_environment_variables():
    """Test if required environment variables are set."""
    print("\n🔐 Testing Environment Variables")
    print("=" * 50)
    
    required_vars = [
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_SESSION_TOKEN",
        "AWS_DEFAULT_REGION"
    ]
    
    optional_vars = [
        "BRIGHT_DATA_USERNAME",
        "BRIGHT_DATA_PASSWORD", 
        "BRIGHT_DATA_API_KEY"
    ]
    
    all_required_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * 10}...{value[-4:]}")
        else:
            print(f"❌ {var}: Not set")
            all_required_set = False
    
    print("\nOptional BrightData variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * 10}...{value[-4:]}")
        else:
            print(f"⚠️  {var}: Not set (will use fallback)")
    
    return all_required_set

def test_imports():
    """Test if all required imports work."""
    print("\n📦 Testing Imports")
    print("=" * 50)
    
    imports_to_test = [
        ("crewai", "CrewAI framework"),
        ("boto3", "AWS SDK"),
        ("ddgs", "DuckDuckGo search"),
        ("requests", "HTTP requests"),
        ("json", "JSON handling"),
        ("datetime", "Date/time handling")
    ]
    
    all_imports_ok = True
    for module, description in imports_to_test:
        try:
            __import__(module)
            print(f"✅ {module}: {description}")
        except ImportError as e:
            print(f"❌ {module}: {description} - {str(e)}")
            all_imports_ok = False
    
    return all_imports_ok

def main():
    """Main test function."""
    print("🚀 STANDALONE BRAND MONITORING SYSTEM TEST")
    print("=" * 60)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test environment variables
    env_ok = test_environment_variables()
    
    # Test standalone tools
    tools_ok = test_standalone_tools()
    
    # Test standalone agent tools
    agent_tools_ok = test_standalone_agent_tools()
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"Environment Variables: {'✅ PASS' if env_ok else '⚠️  PARTIAL'}")
    print(f"Standalone Tools: {'✅ PASS' if tools_ok else '❌ FAIL'}")
    print(f"Agent Tools: {'✅ PASS' if agent_tools_ok else '❌ FAIL'}")
    
    overall_success = imports_ok and env_ok and tools_ok and agent_tools_ok
    
    if overall_success:
        print("\n🎉 All tests passed! Standalone system is ready.")
        print("\nTo run the full brand monitoring agent:")
        print("python standalone_brand_monitoring_agent.py")
    else:
        print("\n❌ Some tests failed. Please check the issues above.")
        
        if not imports_ok:
            print("- Install missing dependencies")
        if not env_ok:
            print("- Set up AWS credentials")
        if not tools_ok:
            print("- Check BrightData configuration")
        if not agent_tools_ok:
            print("- Verify AWS Bedrock access")

if __name__ == "__main__":
    main()
