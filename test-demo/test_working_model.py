#!/usr/bin/env python3
"""
Test the working Bedrock model that we know works
"""

import os
import boto3
import json
from boto3.session import Session

def test_working_bedrock_model():
    """Test the working Bedrock model."""
    print("🧪 Testing Working Bedrock Model")
    print("=" * 50)
    
    try:
        # Set up region
        boto_session = Session()
        region = "us-west-2"
        print(f"✅ Using region: {region}")
        
        # Initialize Bedrock client
        print("1. Initializing Bedrock client...")
        bedrock = boto3.client('bedrock-runtime', region_name=region)
        print("✅ Bedrock client initialized")
        
        # Test the working model ID
        print("\n2. Testing working model...")
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
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
            body=json.dumps(body),
            contentType="application/json"
        )
        
        response_body = json.loads(response['body'].read())
        content = response_body['content'][0]['text']
        print(f"✅ Working model response: {content}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_working_bedrock_model()
