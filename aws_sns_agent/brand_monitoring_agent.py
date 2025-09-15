#!/usr/bin/env python3
"""
Brand Monitoring Agent with CrewAI @tool decorators

This script defines a set of tools for brand monitoring using CrewAI's @tool decorator pattern,
similar to the lab1_py.py customer support agent structure.

Based on the existing brand monitoring system but using CrewAI framework.
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

# Import existing brand monitoring tools
import sys
sys.path.append('/Users/anushka.mac/Desktop/aws_sns_agent/brand-monitoring/brand_monitoring_flow/src')
from brand_monitoring_flow.tools.custom_tool import BrightDataWebSearchTool, scrape_urls

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
        JSON string with search results including URLs, titles, and snippets
    """
    try:
        print(f"Searching for mentions of '{brand_name}'...")
        web_search_tool = BrightDataWebSearchTool()
        results = web_search_tool._run(brand_name, total_results=total_results)
        
        # Format results for better readability
        formatted_results = []
        for result in results:
            formatted_results.append({
                "title": result.get("title", ""),
                "link": result.get("link", ""),
                "snippet": result.get("snippet", "")
            })
        
        return json.dumps({
            "brand_name": brand_name,
            "total_results": len(formatted_results),
            "search_results": formatted_results
        }, indent=2)
        
    except Exception as e:
        return f"Error searching for brand mentions: {str(e)}"

@tool
def scrape_platform_content(urls: str, platform: str) -> str:
    """
    Scrape content from specific platform URLs.

    Args:
        urls: JSON string containing list of URLs to scrape
        platform: Platform type (linkedin, instagram, youtube, x, web)

    Returns:
        JSON string with scraped content data
    """
    try:
        # Parse URLs from JSON string
        url_list = json.loads(urls) if isinstance(urls, str) else urls
        
        print(f"Scraping {len(url_list)} URLs from {platform}...")
        
        # Platform-specific dataset IDs (from your existing config)
        dataset_ids = {
            "linkedin": "gd_lyy3tktm25m4avu764",
            "instagram": "gd_lk5ns7kz21pck8jpis", 
            "youtube": "gd_lk56epmy2i5g7lzu0k",
            "x": "gd_lwxkxvnf1cynvib9co",
            "web": "gd_m6gjtfmeh43we6cqc"
        }
        
        if platform not in dataset_ids:
            return f"Unsupported platform: {platform}"
        
        # Scrape URLs using existing function
        params = {"dataset_id": dataset_ids[platform]}
        scraped_data = scrape_urls(url_list, params, platform)
        
        return json.dumps({
            "platform": platform,
            "urls_scraped": len(url_list),
            "scraped_data": scraped_data
        }, indent=2)
        
    except Exception as e:
        return f"Error scraping {platform} content: {str(e)}"

@tool
def analyze_brand_sentiment(content: str, brand_name: str) -> str:
    """
    Analyze sentiment of brand mentions using Bedrock.

    Args:
        content: JSON string containing scraped content to analyze
        brand_name: The brand name to analyze sentiment for

    Returns:
        JSON string with sentiment analysis results
    """
    try:
        # Parse content from JSON string
        content_data = json.loads(content) if isinstance(content, str) else content
        
        print(f"Analyzing sentiment for '{brand_name}'...")
        
        # Initialize Bedrock client
        bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
        
        # Prepare content for analysis
        analysis_text = f"Brand: {brand_name}\n\nContent to analyze:\n"
        
        if isinstance(content_data, dict) and 'scraped_data' in content_data:
            for item in content_data['scraped_data']:
                if isinstance(item, dict):
                    # Extract relevant text based on platform
                    if 'post_text' in item:
                        analysis_text += f"Post: {item['post_text']}\n"
                    elif 'description' in item:
                        analysis_text += f"Description: {item['description']}\n"
                    elif 'transcript' in item:
                        analysis_text += f"Transcript: {item['transcript'][:500]}...\n"
                    elif 'markdown' in item:
                        analysis_text += f"Content: {item['markdown'][:500]}...\n"
        
        # Create sentiment analysis prompt
        prompt = f"""
        Analyze the sentiment of the following brand mentions for "{brand_name}".
        Provide a sentiment score between -1 (very negative) and 1 (very positive).
        Also provide a brief explanation of the sentiment.
        
        Content:
        {analysis_text}
        
        Please respond in JSON format:
        {{
            "sentiment_score": <number between -1 and 1>,
            "sentiment_label": "<positive/negative/neutral>",
            "explanation": "<brief explanation>",
            "confidence": <number between 0 and 1>
        }}
        """
        
        # Call Bedrock model
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 300,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )
        
        result = json.loads(response['body'].read())
        analysis_result = result['content'][0]['text'].strip()
        
        # Try to parse the JSON response
        try:
            sentiment_data = json.loads(analysis_result)
        except:
            # Fallback if JSON parsing fails
            sentiment_data = {
                "sentiment_score": 0.0,
                "sentiment_label": "neutral",
                "explanation": analysis_result,
                "confidence": 0.5
            }
        
        return json.dumps({
            "brand_name": brand_name,
            "sentiment_analysis": sentiment_data,
            "timestamp": datetime.now().isoformat()
        }, indent=2)
        
    except Exception as e:
        return f"Error analyzing sentiment: {str(e)}"

@tool
def generate_brand_report(brand_name: str, search_results: str, sentiment_data: str) -> str:
    """
    Generate a comprehensive brand monitoring report.

    Args:
        brand_name: The brand name being monitored
        search_results: JSON string with search results
        sentiment_data: JSON string with sentiment analysis

    Returns:
        Formatted brand monitoring report
    """
    try:
        print(f"Generating brand report for '{brand_name}'...")
        
        # Parse input data
        search_data = json.loads(search_results) if isinstance(search_results, str) else search_results
        sentiment_info = json.loads(sentiment_data) if isinstance(sentiment_data, str) else sentiment_data
        
        # Extract key metrics
        total_mentions = search_data.get('total_results', 0)
        sentiment_score = sentiment_info.get('sentiment_analysis', {}).get('sentiment_score', 0)
        sentiment_label = sentiment_info.get('sentiment_analysis', {}).get('sentiment_label', 'unknown')
        
        # Generate report
        report = f"""
# Brand Monitoring Report: {brand_name}

## Executive Summary
- **Total Mentions Found**: {total_mentions}
- **Overall Sentiment**: {sentiment_label.title()} (Score: {sentiment_score:.2f})
- **Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Key Findings
"""
        
        if sentiment_score > 0.3:
            report += "- Brand sentiment is **positive** with good online presence\n"
        elif sentiment_score < -0.3:
            report += "- Brand sentiment is **negative** - attention needed\n"
        else:
            report += "- Brand sentiment is **neutral** - monitoring recommended\n"
        
        report += f"- Found {total_mentions} mentions across web sources\n"
        
        # Add top mentions
        if 'search_results' in search_data:
            report += "\n## Top Mentions\n"
            for i, result in enumerate(search_data['search_results'][:5], 1):
                report += f"{i}. **{result.get('title', 'No title')}**\n"
                report += f"   - URL: {result.get('link', 'No link')}\n"
                report += f"   - Snippet: {result.get('snippet', 'No snippet')[:100]}...\n\n"
        
        # Add sentiment details
        if 'sentiment_analysis' in sentiment_info:
            sentiment_analysis = sentiment_info['sentiment_analysis']
            report += f"## Sentiment Analysis Details\n"
            report += f"- **Score**: {sentiment_analysis.get('sentiment_score', 'N/A')}\n"
            report += f"- **Label**: {sentiment_analysis.get('sentiment_label', 'N/A')}\n"
            report += f"- **Explanation**: {sentiment_analysis.get('explanation', 'N/A')}\n"
            report += f"- **Confidence**: {sentiment_analysis.get('confidence', 'N/A')}\n"
        
        report += f"\n## Recommendations\n"
        if sentiment_score > 0.3:
            report += "- Continue current brand strategy - positive sentiment detected\n"
            report += "- Consider amplifying positive mentions\n"
        elif sentiment_score < -0.3:
            report += "- Address negative sentiment immediately\n"
            report += "- Consider reputation management strategies\n"
        else:
            report += "- Monitor brand mentions regularly\n"
            report += "- Consider proactive engagement strategies\n"
        
        return report
        
    except Exception as e:
        return f"Error generating brand report: {str(e)}"

@tool
def web_search_duckduckgo(keywords: str, max_results: int = 10) -> str:
    """
    Search the web using DuckDuckGo for additional brand mentions.

    Args:
        keywords: Search keywords (brand name)
        max_results: Maximum number of results to return

    Returns:
        JSON string with search results
    """
    try:
        print(f"Searching DuckDuckGo for: {keywords}")
        results = DDGS().text(keywords, max_results=max_results)
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                "title": result.get('title', ''),
                "link": result.get('href', ''),
                "snippet": result.get('body', '')
            })
        
        return json.dumps({
            "search_engine": "DuckDuckGo",
            "keywords": keywords,
            "total_results": len(formatted_results),
            "results": formatted_results
        }, indent=2)
        
    except RatelimitException:
        return json.dumps({"error": "Rate limit reached. Please try again later."})
    except DDGSException as e:
        return json.dumps({"error": f"Search error: {e}"})
    except Exception as e:
        return json.dumps({"error": f"Search error: {str(e)}"})

# ==============================================================================
# SECTION 2: MAIN EXECUTION BLOCK (CREATE AND TEST AGENT)
# ==============================================================================

if __name__ == '__main__':
    
    # --- Step 1: Define Agent Configuration ---
    boto_session = Session()
    region = boto_session.region_name

    SYSTEM_PROMPT = """You are a professional brand monitoring assistant for companies and organizations.
    Your role is to:
    - Search for brand mentions across the web and social media platforms
    - Analyze sentiment of brand mentions using AI
    - Generate comprehensive brand monitoring reports
    - Provide actionable insights and recommendations
    - Be thorough and accurate in your analysis

    You have access to the following tools:
    1. search_brand_mentions() - Search for brand mentions using BrightData
    2. scrape_platform_content() - Scrape content from specific platforms (LinkedIn, Instagram, YouTube, X, Web)
    3. analyze_brand_sentiment() - Analyze sentiment of brand mentions using Bedrock AI
    4. generate_brand_report() - Generate comprehensive brand monitoring reports
    5. web_search_duckduckgo() - Additional web search using DuckDuckGo

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
        backstory="You are an expert brand monitoring specialist with deep knowledge of social media platforms and sentiment analysis.",
        llm=llm,
        tools=[
            search_brand_mentions,      # Tool 1: Search for brand mentions
            scrape_platform_content,    # Tool 2: Scrape platform content
            analyze_brand_sentiment,    # Tool 3: Analyze sentiment
            generate_brand_report,      # Tool 4: Generate reports
            web_search_duckduckgo,      # Tool 5: Additional web search
        ],
        verbose=True
    )
    print("✅ Brand Monitoring Agent created successfully!")

    # --- Step 3: Create Tasks and Test the Agent ---
    print("\nCreating brand monitoring tasks...")
    
    # Task 1: Brand Search and Analysis
    brand_search_task = Task(
        description="Search for mentions of 'OpenAI' across the web and analyze the sentiment of the findings",
        expected_output="A comprehensive analysis of OpenAI brand mentions including sentiment scores and key insights",
        agent=agent
    )
    
    # Task 2: Comprehensive Brand Report
    brand_report_task = Task(
        description="Generate a comprehensive brand monitoring report for 'Hugging Face' including search results, sentiment analysis, and recommendations",
        expected_output="A detailed brand monitoring report with executive summary, key findings, and actionable recommendations",
        agent=agent
    )
    
    # Task 3: Sentiment Analysis
    sentiment_task = Task(
        description="Analyze the current sentiment around 'Anthropic' brand mentions and provide insights",
        expected_output="Sentiment analysis results with scores, explanations, and trend insights",
        agent=agent
    )
    
    # Task 4: Multi-source Search
    multi_search_task = Task(
        description="Search for 'DeepSeek' mentions using both BrightData and DuckDuckGo search engines",
        expected_output="Combined search results from multiple sources with comparison and analysis",
        agent=agent
    )

    # Create the crew
    print("Creating brand monitoring crew...")
    crew = Crew(
        agents=[agent],
        tasks=[brand_search_task, brand_report_task, sentiment_task, multi_search_task],
        process=Process.sequential,
        verbose=True
    )

    print("\n--- Starting Brand Monitoring Analysis ---")
    print("This will run all tasks sequentially...")
    
    # Execute the crew
    result = crew.kickoff()
    
    print("\n--- Results ---")
    print(result)
    
    print("\n🎉 Brand Monitoring Agent testing completed!")
