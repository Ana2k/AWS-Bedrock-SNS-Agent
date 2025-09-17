#!/usr/bin/env python3
"""
LLM Invocation Test
Tests if the LLM can properly invoke messages and return responses
"""

import os
import json
import boto3
from datetime import datetime

def test_bedrock_llm_invocation():
    """Test Bedrock LLM message invocation and response."""
    print("🧪 Testing Bedrock LLM Invocation")
    print("=" * 50)
    
    try:
        # Initialize Bedrock client
        print("1. Initializing Bedrock client...")
        bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
        print("✅ Bedrock client initialized")
        
        # Test 1: Simple message
        print("\n2. Testing simple message...")
        simple_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 100,
            "messages": [
                {
                    "role": "user",
                    "content": "What is 2+2? Please respond with just the number."
                }
            ]
        }
        
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
            body=json.dumps(simple_body),
            contentType="application/json"
        )
        
        response_body = json.loads(response['body'].read())
        content = response_body['content'][0]['text']
        print(f"✅ Simple message response: {content}")
        
        # Test 2: Complex message
        print("\n3. Testing complex message...")
        complex_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 200,
            "messages": [
                {
                    "role": "user",
                    "content": "Analyze the sentiment of this text: 'I love this new product! It's amazing and works perfectly.' Please provide: 1) Overall sentiment, 2) Key positive words, 3) Confidence score (0-100)."
                }
            ]
        }
        
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
            body=json.dumps(complex_body),
            contentType="application/json"
        )
        
        response_body = json.loads(response['body'].read())
        content = response_body['content'][0]['text']
        print(f"✅ Complex message response: {content}")
        
        # Test 3: Multi-turn conversation
        print("\n4. Testing multi-turn conversation...")
        conversation_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 150,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, my name is John. What's your name?"
                },
                {
                    "role": "assistant",
                    "content": "Hello John! I'm Claude, an AI assistant created by Anthropic. How can I help you today?"
                },
                {
                    "role": "user",
                    "content": "Nice to meet you Claude! Can you help me with a simple math problem?"
                }
            ]
        }
        
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
            body=json.dumps(conversation_body),
            contentType="application/json"
        )
        
        response_body = json.loads(response['body'].read())
        content = response_body['content'][0]['text']
        print(f"✅ Multi-turn conversation response: {content}")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM invocation failed: {str(e)}")
        return False

def test_crewai_llm_invocation():
    """Test CrewAI LLM invocation."""
    print("\n🤖 Testing CrewAI LLM Invocation")
    print("=" * 50)
    
    try:
        from crewai import LLM
        
        # Set AWS credentials for boto3
        os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID")
        os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_ACCESS_KEY")
        os.environ["AWS_SESSION_TOKEN"] = os.getenv("AWS_SESSION_TOKEN")
        os.environ["AWS_DEFAULT_REGION"] = "us-west-2"
        
        print("1. Initializing CrewAI LLM...")
        llm = LLM(
            model="bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0",
            temperature=0.1
        )
        print("✅ CrewAI LLM initialized")
        
        # Test 1: Simple call
        print("\n2. Testing simple CrewAI call...")
        response = llm.call("What is the capital of France? Please respond with just the city name.")
        print(f"✅ CrewAI simple response: {response}")
        
        # Test 2: Complex call
        print("\n3. Testing complex CrewAI call...")
        complex_prompt = """
        You are a brand monitoring specialist. Analyze the following brand mention:
        
        "I just tried the new iPhone 15 and it's absolutely incredible! The camera quality is amazing and the battery life is much better than my old phone. Highly recommend!"
        
        Please provide:
        1. Overall sentiment (Positive/Negative/Neutral)
        2. Key positive aspects mentioned
        3. Confidence score (0-100)
        """
        
        response = llm.call(complex_prompt)
        print(f"✅ CrewAI complex response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ CrewAI LLM invocation failed: {str(e)}")
        return False

def test_llm_performance():
    """Test LLM performance metrics."""
    print("\n⚡ Testing LLM Performance")
    print("=" * 50)
    
    try:
        bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
        
        # Test response time
        print("1. Testing response time...")
        start_time = datetime.now()
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 50,
            "messages": [
                {
                    "role": "user",
                    "content": "Count from 1 to 5."
                }
            ]
        }
        
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
            body=json.dumps(body),
            contentType="application/json"
        )
        
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()
        
        response_body = json.loads(response['body'].read())
        content = response_body['content'][0]['text']
        
        print(f"✅ Response time: {response_time:.2f} seconds")
        print(f"✅ Response content: {content}")
        
        # Test token usage
        if 'usage' in response_body:
            usage = response_body['usage']
            print(f"✅ Token usage: {usage}")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {str(e)}")
        return False

def main():
    """Main test function."""
    print("🚀 LLM INVOCATION TEST")
    print("=" * 60)
    
    # Test Bedrock LLM
    bedrock_ok = test_bedrock_llm_invocation()
    
    # Test CrewAI LLM
    crewai_ok = test_crewai_llm_invocation()
    
    # Test performance
    performance_ok = test_llm_performance()
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Bedrock LLM: {'✅ PASS' if bedrock_ok else '❌ FAIL'}")
    print(f"CrewAI LLM: {'✅ PASS' if crewai_ok else '❌ FAIL'}")
    print(f"Performance: {'✅ PASS' if performance_ok else '❌ FAIL'}")
    
    if bedrock_ok and crewai_ok and performance_ok:
        print("\n🎉 All LLM tests passed! The LLM is working perfectly.")
        print("✅ Messages are being invoked successfully")
        print("✅ Responses are being returned properly")
        print("✅ Both Bedrock and CrewAI integrations work")
    else:
        print("\n❌ Some LLM tests failed.")
        if not bedrock_ok:
            print("- Check Bedrock model access")
        if not crewai_ok:
            print("- Check CrewAI LLM configuration")
        if not performance_ok:
            print("- Check network connectivity")

if __name__ == "__main__":
    main()
