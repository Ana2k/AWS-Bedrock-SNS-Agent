#!/usr/bin/env python3
"""
Data Storage Utility for Brand Monitoring Results
Saves brand monitoring results to JSON files for the frontend to display
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List

class BrandMonitoringDataStorage:
    """Handles saving and loading brand monitoring results"""
    
    def __init__(self, results_dir: str = "results"):
        self.results_dir = results_dir
        os.makedirs(self.results_dir, exist_ok=True)
    
    def save_result(self, brand_name: str, search_results: List[Dict], 
                   scraped_data: List[Dict] = None, sentiment_analysis: Dict = None,
                   report_data: Dict = None, metadata: Dict = None) -> str:
        """
        Save brand monitoring results to a JSON file
        
        Args:
            brand_name: Name of the brand being monitored
            search_results: List of search results from web search
            scraped_data: List of scraped content data
            sentiment_analysis: Sentiment analysis results
            report_data: Generated report data
            metadata: Additional metadata
            
        Returns:
            str: Filename of the saved result
        """
        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_brand_name = brand_name.replace(' ', '_').replace('/', '_').lower()
            filename = f"brand_monitoring_{safe_brand_name}_{timestamp}.json"
            filepath = os.path.join(self.results_dir, filename)
            
            # Prepare result data
            result_data = {
                "brand_name": brand_name,
                "timestamp": datetime.now().isoformat(),
                "search_results": search_results or [],
                "scraped_data": scraped_data or [],
                "sentiment_analysis": sentiment_analysis or {},
                "report_data": report_data or {},
                "metadata": metadata or {},
                "summary": {
                    "total_search_results": len(search_results) if search_results else 0,
                    "total_scraped_items": len(scraped_data) if scraped_data else 0,
                    "has_sentiment_analysis": bool(sentiment_analysis),
                    "has_report": bool(report_data)
                }
            }
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Brand monitoring result saved: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error saving result: {str(e)}")
            return None
    
    def save_from_agent_output(self, agent_output: str, brand_name: str = "Unknown") -> str:
        """
        Save results from agent output string
        
        Args:
            agent_output: Raw output from the brand monitoring agent
            brand_name: Name of the brand
            
        Returns:
            str: Filename of the saved result
        """
        try:
            # Try to parse the agent output as JSON
            try:
                parsed_output = json.loads(agent_output)
                return self.save_result(
                    brand_name=brand_name,
                    search_results=parsed_output.get('search_results', []),
                    scraped_data=parsed_output.get('scraped_data', []),
                    sentiment_analysis=parsed_output.get('sentiment_analysis', {}),
                    report_data=parsed_output.get('report_data', {}),
                    metadata={'source': 'agent_output', 'raw_output': agent_output}
                )
            except json.JSONDecodeError:
                # If not JSON, save as raw text
                return self.save_raw_output(agent_output, brand_name)
                
        except Exception as e:
            print(f"❌ Error saving agent output: {str(e)}")
            return None
    
    def save_raw_output(self, raw_output: str, brand_name: str = "Unknown") -> str:
        """
        Save raw output as text file
        
        Args:
            raw_output: Raw text output
            brand_name: Name of the brand
            
        Returns:
            str: Filename of the saved result
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_brand_name = brand_name.replace(' ', '_').replace('/', '_').lower()
            filename = f"brand_monitoring_{safe_brand_name}_{timestamp}.txt"
            filepath = os.path.join(self.results_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Brand Monitoring Result for: {brand_name}\n")
                f.write(f"Generated at: {datetime.now().isoformat()}\n")
                f.write("=" * 50 + "\n\n")
                f.write(raw_output)
            
            print(f"✅ Raw output saved: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error saving raw output: {str(e)}")
            return None
    
    def get_all_results(self) -> List[Dict]:
        """
        Get all saved results
        
        Returns:
            List of result dictionaries
        """
        results = []
        try:
            for filename in os.listdir(self.results_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.results_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            data['filename'] = filename
                            data['file_size'] = os.path.getsize(filepath)
                            data['modified'] = datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                            results.append(data)
                    except Exception as e:
                        print(f"Error reading {filename}: {e}")
            
            # Sort by modification time (newest first)
            results.sort(key=lambda x: x.get('modified', ''), reverse=True)
            return results
            
        except Exception as e:
            print(f"❌ Error getting results: {str(e)}")
            return []
    
    def get_result_by_filename(self, filename: str) -> Dict:
        """
        Get a specific result by filename
        
        Args:
            filename: Name of the result file
            
        Returns:
            Result dictionary or None if not found
        """
        try:
            filepath = os.path.join(self.results_dir, filename)
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"❌ Error getting result {filename}: {str(e)}")
            return None
    
    def delete_result(self, filename: str) -> bool:
        """
        Delete a result file
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            filepath = os.path.join(self.results_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"✅ Deleted result: {filename}")
                return True
            else:
                print(f"⚠️  File not found: {filename}")
                return False
                
        except Exception as e:
            print(f"❌ Error deleting {filename}: {str(e)}")
            return False

# Example usage and testing
if __name__ == "__main__":
    # Test the data storage
    storage = BrandMonitoringDataStorage()
    
    # Sample data
    sample_search_results = [
        {
            "title": "OpenAI Announces New Features",
            "link": "https://example.com/openai-news",
            "snippet": "OpenAI has announced new features for their AI platform..."
        },
        {
            "title": "OpenAI Partnership with Microsoft",
            "link": "https://example.com/openai-microsoft",
            "snippet": "Microsoft and OpenAI have extended their partnership..."
        }
    ]
    
    sample_sentiment = {
        "sentiment_score": 0.8,
        "sentiment_label": "positive",
        "explanation": "Overall positive sentiment with mentions of new features and partnerships"
    }
    
    # Save sample result
    filename = storage.save_result(
        brand_name="OpenAI",
        search_results=sample_search_results,
        sentiment_analysis=sample_sentiment,
        metadata={"test": True, "source": "sample_data"}
    )
    
    if filename:
        print(f"Sample result saved as: {filename}")
        
        # Test retrieving results
        all_results = storage.get_all_results()
        print(f"Total results in storage: {len(all_results)}")
        
        # Test getting specific result
        if all_results:
            specific_result = storage.get_result_by_filename(all_results[0]['filename'])
            if specific_result:
                print(f"Retrieved result for: {specific_result.get('brand_name', 'Unknown')}")
