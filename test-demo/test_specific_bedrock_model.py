#!/usr/bin/env python3
"""
Test the specific Bedrock model snippet provided by user
"""

import os
import sys
from boto3.session import Session

def test_specific_bedrock_model():
    """Test the specific Bedrock model snippet."""
    print("🧪 Testing Specific Bedrock Model Snippet")
    print("=" * 50)
    
    try:
        # Import required modules
        print("1. Importing required modules...")
        
        # Try to import strands (as used in lab1_py.py)
        try:
            from strands.models import BedrockModel
            from strands import Agent
            print("✅ Strands framework imported successfully")
            use_strands = True
        except ImportError:
            print("⚠️  Strands framework not available, trying alternative...")
            use_strands = False
        
        # Set up region
        boto_session = Session()
        region = boto_session.region_name or "us-west-2"
        print(f"✅ Using region: {region}")
        
        # Set up system prompt
        SYSTEM_PROMPT = """
        You are a helpful AI assistant. Respond to user queries clearly and concisely.
        """
        
        if use_strands:
            # Test with strands framework
            print("\n2. Testing with Strands framework...")
            model = BedrockModel(
                model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
                temperature=0.3,
                region_name=region
            )
            agent = Agent(
                model=model,
                system_prompt=SYSTEM_PROMPT,
            )
            response = agent('hi')
            print(f"✅ Strands response: {response}")
            
        else:
            # Test with direct Bedrock call
            print("\n2. Testing with direct Bedrock call...")
            import boto3
            import json
            
            bedrock = boto3.client('bedrock-runtime', region_name=region)
            
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 100,
                "messages": [
                    {
                        "role": "user",
                        "content": "hi"
                    }
                ]
            }
            
            response = bedrock.invoke_model(
                modelId="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
                body=json.dumps(body),
                contentType="application/json"
            )
            
            response_body = json.loads(response['body'].read())
            content = response_body['content'][0]['text']
            print(f"✅ Direct Bedrock response: {content}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def test_alternative_model_ids():
    """Test alternative model IDs that might work."""
    print("\n🔄 Testing Alternative Model IDs")
    print("=" * 50)
    
    import boto3
    import json
    
    # Alternative model IDs to try
    model_ids = [
        "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "anthropic.claude-3-haiku-20240307-v1:0",
        "anthropic.claude-3-sonnet-20240229-v1:0"
    ]
    
    bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
    
    for model_id in model_ids:
        try:
            print(f"\nTesting model: {model_id}")
            
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 50,
                "messages": [
                    {
                        "role": "user",
                        "content": "hi"
                    }
                ]
            }
            
            response = bedrock.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType="application/json"
            )
            
            response_body = json.loads(response['body'].read())
            content = response_body['content'][0]['text']
            print(f"✅ {model_id}: {content}")
            
        except Exception as e:
            print(f"❌ {model_id}: {str(e)}")

def main():
    """Main test function."""
    print("🚀 SPECIFIC BEDROCK MODEL TEST")
    print("=" * 60)
    
    # Test the specific model snippet
    specific_ok = test_specific_bedrock_model()
    
    # Test alternative models
    test_alternative_model_ids()
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Specific Model Test: {'✅ PASS' if specific_ok else '❌ FAIL'}")
    
    if specific_ok:
        print("\n🎉 The specific Bedrock model snippet is working!")
    else:
        print("\n❌ The specific model snippet failed, but check alternative models above.")

if __name__ == "__main__":
    main()
