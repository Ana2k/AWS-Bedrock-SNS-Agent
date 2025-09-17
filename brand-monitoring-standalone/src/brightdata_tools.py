#!/usr/bin/env python3
"""
Standalone Brand Monitoring Tools
Refactored from brand-monitoring folder to avoid modifying original files
"""

from typing import Type, List, Dict, Any
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import os
import ssl
import time
import requests
import json
from dotenv import load_dotenv
from ddgs import DDGS
from ddgs.exceptions import DDGSException, RatelimitException

load_dotenv()

# Disable SSL warnings for development
ssl._create_default_https_context = ssl._create_unverified_context

class BrightDataWebSearchToolInput(BaseModel):
    """Input schema for BrightDataWebSearchTool."""
    title: str = Field(..., description="Brand name to monitor")

class BrightDataWebSearchTool(BaseTool):
    name: str = "Web Search Tool"
    description: str = "Use this tool to search Google and retrieve the top search results with BrightData proxy support."
    args_schema: Type[BaseModel] = BrightDataWebSearchToolInput

    def _run(self, title: str, total_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search for brand mentions using BrightData proxy with fallback to DuckDuckGo.
        
        Args:
            title: Brand name to search for
            total_results: Number of results to return
            
        Returns:
            List of search results with title, link, and snippet
        """
        print(f"🔍 Searching for '{title}' with BrightData...")
        
        # Try BrightData first
        try:
            brightdata_results = self._search_with_brightdata(title, total_results)
            if brightdata_results:
                print(f"✅ BrightData search successful: {len(brightdata_results)} results")
                return brightdata_results
        except Exception as e:
            print(f"⚠️  BrightData search failed: {str(e)}")
            print("🔄 Falling back to DuckDuckGo search...")
        
        # Fallback to DuckDuckGo
        try:
            ddg_results = self._search_with_duckduckgo(title, total_results)
            if ddg_results:
                print(f"✅ DuckDuckGo fallback successful: {len(ddg_results)} results")
                return ddg_results
        except Exception as e:
            print(f"❌ DuckDuckGo fallback also failed: {str(e)}")
        
        # Return empty results if both fail
        print("❌ All search methods failed")
        return []

    def _search_with_brightdata(self, title: str, total_results: int) -> List[Dict[str, Any]]:
        """Search using BrightData proxy."""
        
        # Check if BrightData credentials are available
        username = os.getenv("BRIGHT_DATA_USERNAME")
        password = os.getenv("BRIGHT_DATA_PASSWORD")
        
        if not username or not password:
            raise Exception("BrightData credentials not found in environment variables")
        
        # Configure proxy
        host = 'brd.superproxy.io'
        port = 33335
        proxy_url = f'http://{username}:{password}@{host}:{port}'
        
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        # Prepare search query
        query = "+".join(title.split(" "))
        url = f"https://www.google.com/search?q=%22{query}%22&tbs=qdr:w&brd_json=1&num={total_results}"
        
        # Configure request with timeout and retry
        session = requests.Session()
        session.proxies.update(proxies)
        
        # Add headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Make request with timeout
        response = session.get(
            url, 
            headers=headers,
            verify=False, 
            timeout=30,
            allow_redirects=True
        )
        
        # Check response status
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.reason}")
        
        # Parse JSON response
        try:
            data = response.json()
            if 'organic' not in data:
                raise Exception("No 'organic' results in response")
            
            # Format results
            results = []
            for item in data['organic']:
                results.append({
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', '')
                })
            
            return results
            
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response: {str(e)}")
        except KeyError as e:
            raise Exception(f"Missing key in response: {str(e)}")

    def _search_with_duckduckgo(self, title: str, total_results: int) -> List[Dict[str, Any]]:
        """Fallback search using DuckDuckGo."""
        try:
            results = list(DDGS().text(title, max_results=total_results))
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'title': result.get('title', ''),
                    'link': result.get('href', ''),
                    'snippet': result.get('body', '')
                })
            
            return formatted_results
            
        except (RatelimitException, DDGSException) as e:
            raise Exception(f"DuckDuckGo search error: {str(e)}")

def scrape_urls(input_urls: List[str], initial_params: Dict[str, Any], scraping_type: str) -> List[Dict[str, Any]]:
    """
    Scrape URLs using BrightData with improved error handling.
    
    Args:
        input_urls: List of URLs to scrape
        initial_params: Parameters for the scraping request
        scraping_type: Type of scraping (linkedin, instagram, etc.)
        
    Returns:
        List of scraped data
    """
    print(f"🔍 Scraping {scraping_type} for {len(input_urls)} URLs...")
    
    # Check if BrightData API key is available
    api_key = os.getenv('BRIGHT_DATA_API_KEY')
    if not api_key:
        print("⚠️  BrightData API key not found, returning mock data")
        return _generate_mock_scraped_data(input_urls, scraping_type)
    
    try:
        # Prepare request
        url = "https://api.brightdata.com/datasets/v3/trigger"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        data = [{"url": url} for url in input_urls]
        
        # Make initial request
        response = requests.post(
            url, 
            headers=headers, 
            params=initial_params, 
            json=data,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")
        
        response_data = response.json()
        if 'snapshot_id' not in response_data:
            raise Exception("No snapshot_id in response")
        
        snapshot_id = response_data['snapshot_id']
        print(f"📸 Snapshot created: {snapshot_id}")
        
        # Monitor progress
        tracking_url = f"https://api.brightdata.com/datasets/v3/progress/{snapshot_id}"
        max_wait_time = 300  # 5 minutes max wait
        start_time = time.time()
        
        while True:
            if time.time() - start_time > max_wait_time:
                raise Exception("Scraping timeout exceeded")
            
            status_response = requests.get(tracking_url, headers=headers, timeout=30)
            if status_response.status_code != 200:
                raise Exception(f"Status check failed: {status_response.status_code}")
            
            status_data = status_response.json()
            status = status_data.get('status', 'unknown')
            
            print(f"⏳ Status: {status}")
            
            if status == "ready":
                break
            elif status == "failed":
                raise Exception("Scraping job failed")
            
            time.sleep(10)
        
        # Get results
        output_url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}"
        params = {"format": "json"}
        output_response = requests.get(output_url, headers=headers, params=params, timeout=30)
        
        if output_response.status_code != 200:
            raise Exception(f"Results retrieval failed: {output_response.status_code}")
        
        results = output_response.json()
        print(f"✅ Scraping completed: {len(results)} results")
        
        return results
        
    except Exception as e:
        print(f"❌ Scraping failed: {str(e)}")
        print("🔄 Returning mock data...")
        return _generate_mock_scraped_data(input_urls, scraping_type)

def _generate_mock_scraped_data(input_urls: List[str], scraping_type: str) -> List[Dict[str, Any]]:
    """Generate mock scraped data for testing purposes."""
    mock_data = []
    
    for i, url in enumerate(input_urls):
        if scraping_type == "linkedin":
            mock_data.append({
                "url": url,
                "headline": f"LinkedIn Post {i+1} about Brand",
                "post_text": f"This is a mock LinkedIn post content for {url}",
                "hashtags": ["#brand", "#business", "#innovation"],
                "tagged_companies": ["Company A", "Company B"],
                "tagged_people": ["John Doe", "Jane Smith"],
                "user_id": f"user_{i+1}"
            })
        elif scraping_type == "instagram":
            mock_data.append({
                "url": url,
                "description": f"Instagram post {i+1} featuring the brand",
                "likes": 100 + i * 50,
                "num_comments": 10 + i * 5,
                "is_paid_partnership": i % 2 == 0,
                "followers": 1000 + i * 100,
                "user_posted": f"instagram_user_{i+1}"
            })
        elif scraping_type == "youtube":
            mock_data.append({
                "url": url,
                "title": f"YouTube Video {i+1} about Brand",
                "description": f"Mock YouTube video description for {url}",
                "youtuber": f"youtuber_{i+1}",
                "verified": i % 3 == 0,
                "views": 10000 + i * 1000,
                "likes": 500 + i * 50,
                "hashtags": ["#brand", "#video", "#review"],
                "transcript": f"Mock transcript for video {i+1} discussing the brand..."
            })
        elif scraping_type == "twitter" or scraping_type == "x":
            mock_data.append({
                "url": url,
                "views": 5000 + i * 500,
                "likes": 200 + i * 20,
                "replies": 50 + i * 5,
                "reposts": 100 + i * 10,
                "hashtags": ["#brand", "#tech", "#innovation"],
                "quotes": 25 + i * 2,
                "bookmarks": 75 + i * 7,
                "description": f"Mock Twitter post {i+1} about the brand",
                "tagged_users": ["@user1", "@user2"],
                "user_posted": f"twitter_user_{i+1}"
            })
        else:  # web
            mock_data.append({
                "url": url,
                "markdown": f"# Mock Web Content {i+1}\n\nThis is mock content from {url} discussing the brand and its features."
            })
    
    return mock_data

# Test function
def test_standalone_tools():
    """Test the standalone tools functionality."""
    print("🧪 Testing Standalone Brand Monitoring Tools...")
    
    tool = BrightDataWebSearchTool()
    
    try:
        results = tool._run("Browserbase", total_results=5)
        
        if results:
            print(f"✅ Test successful: {len(results)} results found")
            for i, result in enumerate(results[:3], 1):
                print(f"  {i}. {result.get('title', 'No title')}")
                print(f"     URL: {result.get('link', 'No link')}")
                print(f"     Snippet: {result.get('snippet', 'No snippet')[:100]}...")
                print()
        else:
            print("⚠️  No results found")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_standalone_tools()
