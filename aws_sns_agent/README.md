# Brand Monitoring Agent with CrewAI @tool Decorators

A simplified brand monitoring system using CrewAI with `@tool` decorators, based on the pattern from `lab1_py.py`.

## Overview

This project transforms your existing CrewAI-based brand monitoring system into a simple, tool-based approach using CrewAI's `@tool` decorator pattern. Each functionality is implemented as a standalone tool with the `@tool` decorator.

## Architecture

```
User Query → Brand Monitoring Crew → @tool Functions → Bedrock LLM → Structured Response
```

## Tools Available

1. **`search_brand_mentions()`** - Search for brand mentions using BrightData
2. **`scrape_platform_content()`** - Scrape content from specific platforms
3. **`analyze_brand_sentiment()`** - Analyze sentiment using Bedrock Claude
4. **`generate_brand_report()`** - Generate comprehensive reports
5. **`web_search_duckduckgo()`** - Additional web search using DuckDuckGo

## Installation

```bash
# Install dependencies
%pip install -U -r requirements.txt -q
```

## Environment Setup

Create a `.env` file with your credentials:

```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1

# BrightData Credentials
BRIGHT_DATA_USERNAME=your_brightdata_username
BRIGHT_DATA_PASSWORD=your_brightdata_password
BRIGHT_DATA_API_KEY=your_brightdata_api_key
```

## Usage

### Run the Agent

```bash
python brand_monitoring_agent.py
```

### Example Queries

- "Search for mentions of 'OpenAI' and analyze the sentiment"
- "Generate a comprehensive brand monitoring report for 'Hugging Face'"
- "What is the current sentiment around 'Anthropic' brand mentions?"
- "Search for 'DeepSeek' mentions using both BrightData and DuckDuckGo"

## Key Features

- **Simple @tool Decorators**: Each function is a standalone tool
- **Bedrock Integration**: Uses Claude 3.5 Sonnet for analysis
- **Multi-source Search**: BrightData + DuckDuckGo
- **Sentiment Analysis**: AI-powered sentiment scoring
- **Comprehensive Reports**: Detailed brand monitoring insights

## File Structure

```
aws_sns_agent/
├── brand_monitoring_agent.py    # Main agent with @tool functions
├── requirements.txt             # Simplified dependencies
├── README.md                   # This file
├── anushka_aws_sns/
│   └── lab1_py.py             # Reference implementation
└── brand-monitoring/           # Original CrewAI system (for reference)
```

## Dependencies

- `crewai[tools]` - Core CrewAI framework with tools
- `boto3` - AWS SDK
- `ddgs-search` - DuckDuckGo search
- `python-dotenv` - Environment variables
- `requests` - HTTP requests
- `pydantic` - Data validation

## Testing

The agent includes built-in tests that run automatically using CrewAI tasks:

1. **Brand Search Task** - Search for OpenAI mentions and analyze sentiment
2. **Brand Report Task** - Generate comprehensive Hugging Face brand report
3. **Sentiment Analysis Task** - Analyze Anthropic brand sentiment
4. **Multi-source Search Task** - Search DeepSeek using multiple sources

## Benefits of @tool Approach

- **Simplicity**: Each function is independent and testable
- **Modularity**: Easy to add/remove tools
- **Debugging**: Individual tools can be tested separately
- **Maintainability**: Clear separation of concerns
- **Scalability**: Tools can be distributed across services

## Next Steps

1. Install dependencies: `%pip install -U -r requirements.txt -q`
2. Set up environment variables
3. Run the agent: `python brand_monitoring_agent.py`
4. Test with your own brand queries
5. Customize tools as needed

This simplified approach maintains the core functionality of your brand monitoring system while making it much easier to understand, maintain, and extend.
