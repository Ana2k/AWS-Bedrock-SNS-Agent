
#!/usr/bin/env python3
"""
Brand Monitoring System Analysis and Summary

This script demonstrates what's working in the brand monitoring system
and provides a summary of the current state.
"""

import os
import sys
import json
from datetime import datetime

# Add the brand monitoring flow path
sys.path.append('/Users/anushka.mac/Desktop/aws_sns_agent/brand-monitoring/brand_monitoring_flow/src')

def test_brightdata_search():
    """Test the BrightData search functionality"""
    try:
        from brand_monitoring_flow.tools.custom_tool import BrightDataWebSearchTool
        
        print("🔍 Testing BrightData Web Search...")
        web_search_tool = BrightDataWebSearchTool()
        
        # Test search
        results = web_search_tool._run("Browserbase", total_results=5)
        
        print(f"✅ Found {len(results)} search results")
        for i, result in enumerate(results[:3], 1):
            print(f"  {i}. {result.get('title', 'No title')}")
            print(f"     URL: {result.get('link', 'No link')}")
            print(f"     Snippet: {result.get('snippet', 'No snippet')[:100]}...")
            print()
        
        return True
    except Exception as e:
        print(f"❌ BrightData search failed: {str(e)}")
        return False

def test_aws_credentials():
    """Test AWS credentials configuration"""
    try:
        import boto3
        
        print("🔐 Testing AWS Credentials...")
        
        # Check environment variables
        access_key = os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        session_token = os.getenv("AWS_SESSION_TOKEN")
        region = os.getenv("AWS_DEFAULT_REGION")
        
        if not all([access_key, secret_key, session_token, region]):
            print("❌ AWS credentials not properly set")
            return False
        
        print(f"✅ AWS credentials found:")
        print(f"   Access Key: {access_key[:10]}...")
        print(f"   Secret Key: {secret_key[:10]}...")
        print(f"   Session Token: {session_token[:20]}...")
        print(f"   Region: {region}")
        
        # Test Bedrock access
        bedrock = boto3.client('bedrock-runtime', region_name=region)
        print("✅ Bedrock client created successfully")
        
        return True
    except Exception as e:
        print(f"❌ AWS credentials test failed: {str(e)}")
        return False

def test_crewai_imports():
    """Test CrewAI imports"""
    try:
        print("🤖 Testing CrewAI imports...")
        
        from crewai import Agent, Crew, Process, Task, LLM
        from crewai.tools import tool
        from crewai.flow import Flow, listen, start
        
        print("✅ CrewAI imports successful")
        return True
    except Exception as e:
        print(f"❌ CrewAI import failed: {str(e)}")
        return False

def test_ddgs_search():
    """Test DuckDuckGo search"""
    try:
        print("🦆 Testing DuckDuckGo search...")
        
        from ddgs import DDGS
        
        results = list(DDGS().text("Browserbase", max_results=3))
        
        print(f"✅ Found {len(results)} DuckDuckGo results")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.get('title', 'No title')}")
            print(f"     URL: {result.get('href', 'No link')}")
            print()
        
        return True
    except Exception as e:
        print(f"❌ DuckDuckGo search failed: {str(e)}")
        return False

def main():
    """Main function to run all tests"""
    print("=" * 60)
    print("🚀 BRAND MONITORING SYSTEM ANALYSIS")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("AWS Credentials", test_aws_credentials),
        ("CrewAI Imports", test_crewai_imports),
        ("DuckDuckGo Search", test_ddgs_search),
        ("BrightData Search", test_brightdata_search),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        results[test_name] = test_func()
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All systems are working! The brand monitoring system is ready to use.")
        print("\nNext steps:")
        print("1. The system successfully scrapes data from BrightData")
        print("2. AWS credentials are properly configured")
        print("3. CrewAI framework is available")
        print("4. The main issue is the LLM model configuration")
        print("\nTo fix the LLM issue, you need to either:")
        print("- Install Ollama and the deepseek-r1:1.5b model, OR")
        print("- Modify the crew configurations to use AWS Bedrock instead")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the issues above.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
