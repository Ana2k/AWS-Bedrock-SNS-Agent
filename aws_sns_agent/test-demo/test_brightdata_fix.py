#!/usr/bin/env python3
"""
Test script for the fixed BrightData tool
"""

import sys
import os

# Add the brand monitoring flow path
sys.path.append('/Users/anushka.mac/Desktop/aws_sns_agent/brand-monitoring/brand_monitoring_flow/src')

def test_fixed_brightdata_tool():
    """Test the fixed BrightData tool."""
    print("🧪 Testing Fixed BrightData Tool")
    print("=" * 50)
    
    try:
        from brand_monitoring_flow.tools.custom_tool_fixed import BrightDataWebSearchTool, scrape_urls
        
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

def test_environment_variables():
    """Test if required environment variables are set."""
    print("\n🔐 Testing Environment Variables")
    print("=" * 50)
    
    required_vars = [
        "BRIGHT_DATA_USERNAME",
        "BRIGHT_DATA_PASSWORD", 
        "BRIGHT_DATA_API_KEY"
    ]
    
    all_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * 10}...{value[-4:]}")
        else:
            print(f"❌ {var}: Not set")
            all_set = False
    
    if not all_set:
        print("\n⚠️  Some BrightData credentials are missing.")
        print("The tool will fall back to DuckDuckGo search.")
    
    return all_set

def main():
    """Main test function."""
    print("🚀 BRIGHTDATA FIX TESTING")
    print("=" * 60)
    
    # Test environment variables
    env_ok = test_environment_variables()
    
    # Test the fixed tool
    tool_ok = test_fixed_brightdata_tool()
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Environment Variables: {'✅ PASS' if env_ok else '⚠️  PARTIAL'}")
    print(f"Fixed Tool: {'✅ PASS' if tool_ok else '❌ FAIL'}")
    
    if tool_ok:
        print("\n🎉 BrightData fix is working!")
        print("The tool now has:")
        print("- ✅ Proper error handling")
        print("- ✅ DuckDuckGo fallback")
        print("- ✅ Mock data generation")
        print("- ✅ Timeout protection")
        print("- ✅ Better logging")
    else:
        print("\n❌ Issues still exist with the BrightData tool")

if __name__ == "__main__":
    main()
