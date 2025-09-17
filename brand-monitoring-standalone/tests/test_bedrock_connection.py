#!/usr/bin/env python3
"""
Simple Bedrock Model Test
Tests if AWS Bedrock is accessible and working properly
"""

import os
import json
import boto3
from datetime import datetime

def test_bedrock_connection():
    """Test basic Bedrock connection and model access."""
    print("🧪 Testing AWS Bedrock Connection")
    print("=" * 50)
    
    try:
        # Initialize Bedrock client
        print("1. Initializing Bedrock client...")
        bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
        print("✅ Bedrock client initialized successfully")
        
        # Test 1: List available models
        print("\n2. Testing model access...")
        try:
            # Try to invoke a simple model
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 100,
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello, can you respond with just 'Hello World'?"
                    }
                ]
            }
            
            response = bedrock.invoke_model(
                modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
                body=json.dumps(body),
                contentType="application/json"
            )
            
            response_body = json.loads(response['body'].read())
            content = response_body['content'][0]['text']
            
            print(f"✅ Model response: {content}")
            return True
            
        except Exception as e:
            print(f"❌ Model invocation failed: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ Bedrock client initialization failed: {str(e)}")
        return False

def test_environment_variables():
    """Test AWS environment variables."""
    print("\n🔐 Testing AWS Environment Variables")
    print("=" * 50)
    
    required_vars = [
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY", 
        "AWS_SESSION_TOKEN",
        "AWS_DEFAULT_REGION"
    ]
    
    all_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * 10}...{value[-4:]}")
        else:
            print(f"❌ {var}: Not set")
            all_set = False
    
    return all_set

def test_boto3_session():
    """Test boto3 session and credentials."""
    print("\n🔑 Testing Boto3 Session")
    print("=" * 50)
    
    try:
        from boto3.session import Session
        
        session = Session()
        credentials = session.get_credentials()
        
        if credentials:
            print("✅ Boto3 session credentials found")
            print(f"   Access Key: {'*' * 10}...{credentials.access_key[-4:]}")
            print(f"   Secret Key: {'*' * 10}...{credentials.secret_key[-4:]}")
            if hasattr(credentials, 'token') and credentials.token:
                print(f"   Session Token: {'*' * 10}...{credentials.token[-4:]}")
            return True
        else:
            print("❌ No credentials found in boto3 session")
            return False
            
    except Exception as e:
        print(f"❌ Boto3 session test failed: {str(e)}")
        return False

def main():
    """Main test function."""
    print("🚀 AWS BEDROCK SIMPLE TEST")
    print("=" * 60)
    
    # Test environment variables
    env_ok = test_environment_variables()
    
    # Test boto3 session
    session_ok = test_boto3_session()
    
    # Test Bedrock connection
    bedrock_ok = test_bedrock_connection()
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Environment Variables: {'✅ PASS' if env_ok else '❌ FAIL'}")
    print(f"Boto3 Session: {'✅ PASS' if session_ok else '❌ FAIL'}")
    print(f"Bedrock Connection: {'✅ PASS' if bedrock_ok else '❌ FAIL'}")
    
    if env_ok and session_ok and bedrock_ok:
        print("\n🎉 All Bedrock tests passed! The model is accessible.")
    else:
        print("\n❌ Some Bedrock tests failed.")
        if not env_ok:
            print("- Check AWS environment variables")
        if not session_ok:
            print("- Verify AWS credentials")
        if not bedrock_ok:
            print("- Check Bedrock model access permissions")

if __name__ == "__main__":
    main()
