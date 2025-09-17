#!/usr/bin/env python3
"""
Sentiment Analysis Test
Tests the specific sentiment analysis functionality that was failing
"""

import os
import json
import boto3
from datetime import datetime

def test_sentiment_analysis():
    """Test sentiment analysis with proper Bedrock format."""
    print("🧪 Testing Sentiment Analysis")
    print("=" * 50)
    
    try:
        # Initialize Bedrock client
        print("1. Initializing Bedrock client...")
        bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
        print("✅ Bedrock client initialized")
        
        # Test data
        test_content = {
            "search_results": [
                {
                    "title": "OpenAI",
                    "snippet": "OpenAI, Inc. is an American artificial intelligence (AI) organization headquartered in San Francisco, California. It aims to develop 'safe and beneficial' artificial general intelligence (AGI)."
                },
                {
                    "title": "LinkedIn OpenAI",
                    "snippet": "OpenAI | 4,987,740 followers on LinkedIn. Creating safe AGI that benefits all of humanity. OpenAI is an AI research and deployment company."
                }
            ]
        }
        
        brand_name = "OpenAI"
        
        # Prepare content for analysis
        analysis_text = f"Brand: {brand_name}\n\nContent to analyze:\n"
        
        for result in test_content['search_results']:
            analysis_text += f"- {result.get('snippet', '')}\n"
        
        # Create prompt for sentiment analysis
        prompt = f"""
        Analyze the sentiment of mentions about the brand "{brand_name}" in the following content.
        
        Content:
        {analysis_text}
        
        Please provide:
        1. Overall sentiment (Positive, Negative, Neutral)
        2. Sentiment score (-1 to 1, where -1 is very negative, 0 is neutral, 1 is very positive)
        3. Key positive mentions
        4. Key negative mentions
        5. Summary of findings
        
        Format your response as JSON with these fields.
        """
        
        print("2. Testing sentiment analysis...")
        
        # Prepare Bedrock request with correct format
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        # Call Bedrock
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
            body=json.dumps(body),
            contentType="application/json"
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        analysis_result = response_body['content'][0]['text']
        
        print(f"✅ Sentiment analysis completed for '{brand_name}'")
        print(f"✅ Analysis result: {analysis_result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Sentiment analysis failed: {str(e)}")
        return False

def test_brand_monitoring_sentiment():
    """Test the exact sentiment analysis function from brand monitoring."""
    print("\n🔍 Testing Brand Monitoring Sentiment Analysis")
    print("=" * 50)
    
    try:
        # Import the function from standalone agent
        import sys
        sys.path.append('/Users/anushka.mac/Desktop/aws_sns_agent/test-demo')
        from standalone_brand_monitoring_agent import analyze_brand_sentiment
        
        # Test data
        test_content = json.dumps({
            "search_results": [
                {
                    "title": "OpenAI",
                    "snippet": "OpenAI is a leading AI company developing safe and beneficial artificial general intelligence."
                },
                {
                    "title": "OpenAI News",
                    "snippet": "OpenAI continues to innovate in the AI space with groundbreaking research and development."
                }
            ]
        })
        
        print("1. Testing brand monitoring sentiment function...")
        result = analyze_brand_sentiment.func(test_content, "OpenAI")
        result_data = json.loads(result)
        
        if 'sentiment_analysis' in result_data:
            print("✅ Brand monitoring sentiment analysis successful")
            print(f"✅ Result: {result_data['sentiment_analysis'][:200]}...")
            return True
        else:
            print(f"❌ Sentiment analysis failed: {result_data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Brand monitoring sentiment test failed: {str(e)}")
        return False

def main():
    """Main test function."""
    print("🚀 SENTIMENT ANALYSIS TEST")
    print("=" * 60)
    
    # Test basic sentiment analysis
    basic_ok = test_sentiment_analysis()
    
    # Test brand monitoring sentiment
    brand_ok = test_brand_monitoring_sentiment()
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Basic Sentiment Analysis: {'✅ PASS' if basic_ok else '❌ FAIL'}")
    print(f"Brand Monitoring Sentiment: {'✅ PASS' if brand_ok else '❌ FAIL'}")
    
    if basic_ok and brand_ok:
        print("\n🎉 All sentiment analysis tests passed!")
        print("✅ LLM can analyze sentiment properly")
        print("✅ Brand monitoring sentiment function works")
        print("✅ Proper JSON responses are returned")
    else:
        print("\n❌ Some sentiment analysis tests failed.")
        if not basic_ok:
            print("- Check Bedrock model access for sentiment analysis")
        if not brand_ok:
            print("- Check brand monitoring sentiment function")

if __name__ == "__main__":
    main()
