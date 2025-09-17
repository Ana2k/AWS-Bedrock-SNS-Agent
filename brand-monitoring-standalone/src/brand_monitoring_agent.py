#!/usr/bin/env python3
"""
Standalone Brand Monitoring Agent with CrewAI @tool decorators
Refactored to avoid modifying the brand-monitoring folder
"""

import os
import time
import json
import boto3
from boto3.session import Session
from typing import List, Dict, Any
from datetime import datetime

# CrewAI framework imports
try:
    from crewai.tools import tool
    from crewai import Agent, Crew, Process, Task, LLM
    from ddgs import DDGS
    from ddgs.exceptions import DDGSException, RatelimitException
except ImportError as e:
    print(f"Warning: A required library is not installed. {e}")
    print("Please ensure 'crewai', 'ddgs-search', and boto3 are installed.")
    # Define a dummy decorator if 'crewai' is not available
    def tool(func):
        return func

# Import standalone tools
from standalone_tools import BrightDataWebSearchTool, scrape_urls

# ==============================================================================
# SECTION 1: BRAND MONITORING TOOL DEFINITIONS
# ==============================================================================

@tool
def search_brand_mentions(brand_name: str, total_results: int = 15) -> str:
    """
    Search for brand mentions across the web using BrightData.

    Args:
        brand_name: The brand/company name to search for
        total_results: Number of search results to return (default: 15)

    Returns:
        JSON string containing search results with titles, links, and snippets
    """
    try:
        print(f"🔍 Searching for brand mentions: {brand_name}")
        
        # Use the standalone BrightData tool
        search_tool = BrightDataWebSearchTool()
        results = search_tool._run(brand_name, total_results)
        
        if results:
            print(f"✅ Found {len(results)} brand mentions")
            return json.dumps({
                "brand_name": brand_name,
                "total_results": len(results),
                "search_results": results,
                "timestamp": datetime.now().isoformat()
            })
        else:
            print("⚠️  No brand mentions found")
            return json.dumps({
                "brand_name": brand_name,
                "total_results": 0,
                "search_results": [],
                "timestamp": datetime.now().isoformat(),
                "message": "No results found"
            })
            
    except Exception as e:
        error_msg = f"Error searching for brand mentions: {str(e)}"
        print(f"❌ {error_msg}")
        return json.dumps({
            "brand_name": brand_name,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        })

@tool
def scrape_brand_content(urls: str, platform: str = "web") -> str:
    """
    Scrape content from URLs for brand analysis.

    Args:
        urls: JSON string containing list of URLs to scrape
        platform: Platform type (linkedin, instagram, youtube, twitter, web)

    Returns:
        JSON string containing scraped content
    """
    try:
        print(f"🔍 Scraping content from {platform} URLs...")
        
        # Parse URLs
        if isinstance(urls, str):
            url_list = json.loads(urls)
        else:
            url_list = urls
            
        if not isinstance(url_list, list):
            raise ValueError("URLs must be a list")
        
        # Scrape content
        scraped_data = scrape_urls(url_list, {}, platform)
        
        if scraped_data:
            print(f"✅ Scraped {len(scraped_data)} items from {platform}")
            return json.dumps({
                "platform": platform,
                "urls": url_list,
                "scraped_data": scraped_data,
                "timestamp": datetime.now().isoformat()
            })
        else:
            print("⚠️  No content scraped")
            return json.dumps({
                "platform": platform,
                "urls": url_list,
                "scraped_data": [],
                "timestamp": datetime.now().isoformat(),
                "message": "No content scraped"
            })
            
    except Exception as e:
        error_msg = f"Error scraping content: {str(e)}"
        print(f"❌ {error_msg}")
        return json.dumps({
            "platform": platform,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        })

@tool
def analyze_brand_sentiment(content: str, brand_name: str) -> str:
    """
    Analyze sentiment of brand mentions using AWS Bedrock.

    Args:
        content: JSON string containing content to analyze
        brand_name: The brand name to analyze sentiment for

    Returns:
        JSON string containing sentiment analysis results
    """
    try:
        # Parse content
        content_data = json.loads(content) if isinstance(content, str) else content
        
        print(f"Analyzing sentiment for '{brand_name}'...")
        
        # Initialize Bedrock client
        bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
        
        # Prepare content for analysis
        analysis_text = f"Brand: {brand_name}\n\nContent to analyze:\n"
        
        if isinstance(content_data, dict) and 'scraped_data' in content_data:
            # Handle scraped data format
            for item in content_data['scraped_data']:
                if 'post_text' in item:
                    analysis_text += f"- {item['post_text']}\n"
                elif 'description' in item:
                    analysis_text += f"- {item['description']}\n"
                elif 'markdown' in item:
                    analysis_text += f"- {item['markdown']}\n"
        elif isinstance(content_data, dict) and 'search_results' in content_data:
            # Handle search results format
            for result in content_data['search_results']:
                analysis_text += f"- {result.get('snippet', '')}\n"
        else:
            analysis_text += str(content_data)
        
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
        
        # Prepare Bedrock request
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.1
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
        
        return json.dumps({
            "brand_name": brand_name,
            "sentiment_analysis": analysis_result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        error_msg = f"Error analyzing sentiment: {str(e)}"
        print(f"❌ {error_msg}")
        return json.dumps({
            "brand_name": brand_name,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        })

@tool
def generate_brand_report(analysis_data: str, brand_name: str) -> str:
    """
    Generate a comprehensive brand monitoring report.

    Args:
        analysis_data: JSON string containing all analysis data
        brand_name: The brand name for the report

    Returns:
        JSON string containing the generated report
    """
    try:
        print(f"📊 Generating brand report for '{brand_name}'...")
        
        # Parse analysis data
        data = json.loads(analysis_data) if isinstance(analysis_data, str) else analysis_data
        
        # Initialize Bedrock client
        bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
        
        # Create report prompt
        prompt = f"""
        Generate a comprehensive brand monitoring report for "{brand_name}" based on the following data:
        
        {json.dumps(data, indent=2)}
        
        The report should include:
        1. Executive Summary
        2. Brand Mention Overview
        3. Sentiment Analysis Summary
        4. Key Findings
        5. Recommendations
        6. Next Steps
        
        Format the report in markdown and make it professional and actionable.
        """
        
        # Prepare Bedrock request
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.3
        }
        
        # Call Bedrock
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
            body=json.dumps(body),
            contentType="application/json"
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        report_content = response_body['content'][0]['text']
        
        print(f"✅ Brand report generated for '{brand_name}'")
        
        return json.dumps({
            "brand_name": brand_name,
            "report_content": report_content,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        error_msg = f"Error generating report: {str(e)}"
        print(f"❌ {error_msg}")
        return json.dumps({
            "brand_name": brand_name,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        })

# ==============================================================================
# SECTION 2: MAIN EXECUTION
# ==============================================================================

if __name__ == "__main__":
    # --- Step 1: Define Agent Configuration ---
    boto_session = Session()
    region = boto_session.region_name or "us-west-2"

    SYSTEM_PROMPT = """
    You are a Brand Monitoring Specialist with expertise in:
    - Web search and content discovery
    - Sentiment analysis and brand perception
    - Data scraping and content analysis
    - Report generation and insights

    Your role is to:
    1. Search for brand mentions across various platforms
    2. Scrape and analyze content related to the brand
    3. Perform sentiment analysis on brand mentions
    4. Generate comprehensive reports with actionable insights

    Always use the appropriate tools to get accurate, up-to-date information about brand mentions.
    When analyzing sentiment, be thorough and provide detailed explanations.
    Generate comprehensive reports that include actionable recommendations.
    """

    # --- Step 2: Create the Brand Monitoring Agent ---
    print("Initializing Bedrock model...")
    
    # Set AWS credentials for boto3
    os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID")
    os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_ACCESS_KEY")
    os.environ["AWS_SESSION_TOKEN"] = os.getenv("AWS_SESSION_TOKEN")
    os.environ["AWS_DEFAULT_REGION"] = region
    
    llm = LLM(
        model="bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0",
        temperature=0.1
    )

    print("Creating the brand monitoring agent with all tools...")
    agent = Agent(
        role="Brand Monitoring Specialist",
        goal="Monitor brand mentions across platforms and analyze sentiment",
        backstory=SYSTEM_PROMPT,
        tools=[
            search_brand_mentions,
            scrape_brand_content,
            analyze_brand_sentiment,
            generate_brand_report
        ],
        llm=llm,
        verbose=True
    )

    print("✅ Brand Monitoring Agent created successfully!")

    # --- Step 3: Create Tasks ---
    print("Creating brand monitoring tasks...")
    
    # Task 1: Search for brand mentions
    search_task = Task(
        description="Search for mentions of 'OpenAI' across the web and analyze the sentiment of the findings",
        expected_output="A comprehensive analysis of brand mentions including sentiment scores and key insights",
        agent=agent
    )

    # --- Step 4: Create Crew ---
    print("Creating brand monitoring crew...")
    crew = Crew(
        agents=[agent],
        tasks=[search_task],
        process=Process.sequential,
        verbose=True
    )

    # --- Step 5: Execute ---
    print("\n--- Starting Brand Monitoring Analysis ---")
    print("This will run all tasks sequentially...")
    
    try:
        result = crew.kickoff()
        print("\n" + "="*60)
        print("🎉 BRAND MONITORING ANALYSIS COMPLETED!")
        print("="*60)
        print(result)
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"brand_monitoring_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "brand_name": "OpenAI",
                "results": str(result)
            }, f, indent=2)
        
        print(f"\n📄 Results saved to: {filename}")
        
    except Exception as e:
        print(f"\n❌ Error during brand monitoring analysis: {str(e)}")
        print("This might be due to:")
        print("1. AWS credentials not properly configured")
        print("2. Network connectivity issues")
        print("3. BrightData proxy configuration")
        print("4. Bedrock model access permissions")
