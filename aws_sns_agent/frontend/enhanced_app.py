#!/usr/bin/env python3
"""
Enhanced Flask Frontend for Brand Monitoring System
Includes interactive features to run brand monitoring components
"""

from flask import Flask, render_template, jsonify, request
import json
import os
import sys
import subprocess
import threading
import time
from datetime import datetime
import glob

app = Flask(__name__)

# Add the parent directory to the path for imports
sys.path.append('/Users/anushka.mac/Desktop/aws_sns_agent')

# Ensure results directory exists
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

# Global variable to track running processes
running_processes = {}

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('enhanced_index.html')

@app.route('/api/run-search', methods=['POST'])
def run_search():
    """API endpoint to run brand search"""
    try:
        data = request.get_json()
        brand_name = data.get('brand_name', 'OpenAI')
        total_results = data.get('total_results', 5)
        
        # Import and run the search function
        from brand_monitoring_agent import search_brand_mentions
        
        result = search_brand_mentions.func(brand_name, total_results)
        result_data = json.loads(result)
        
        # Save result
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"search_{brand_name}_{timestamp}.json"
        file_path = os.path.join(RESULTS_DIR, filename)
        
        with open(file_path, 'w') as f:
            json.dump({
                'type': 'search',
                'brand_name': brand_name,
                'timestamp': datetime.now().isoformat(),
                'data': result_data
            }, f, indent=2)
        
        return jsonify({
            'success': True,
            'data': result_data,
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/run-sentiment', methods=['POST'])
def run_sentiment():
    """API endpoint to run sentiment analysis"""
    try:
        data = request.get_json()
        brand_name = data.get('brand_name', 'OpenAI')
        content = data.get('content', '')
        
        # Create mock content if none provided
        if not content:
            content = json.dumps({
                "scraped_data": [
                    {
                        "markdown": f"Recent news about {brand_name}: The company continues to innovate and receive positive feedback from users and industry experts."
                    }
                ]
            })
        
        # Import and run the sentiment analysis function
        from brand_monitoring_agent import analyze_brand_sentiment
        
        result = analyze_brand_sentiment.func(content, brand_name)
        result_data = json.loads(result)
        
        # Save result
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sentiment_{brand_name}_{timestamp}.json"
        file_path = os.path.join(RESULTS_DIR, filename)
        
        with open(file_path, 'w') as f:
            json.dump({
                'type': 'sentiment',
                'brand_name': brand_name,
                'timestamp': datetime.now().isoformat(),
                'data': result_data
            }, f, indent=2)
        
        return jsonify({
            'success': True,
            'data': result_data,
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/run-demo', methods=['POST'])
def run_demo():
    """API endpoint to run the complete demo"""
    try:
        data = request.get_json()
        brand_name = data.get('brand_name', 'OpenAI')
        
        # Start the demo in a separate thread
        process_id = f"demo_{int(time.time())}"
        running_processes[process_id] = {
            'status': 'running',
            'start_time': datetime.now().isoformat(),
            'brand_name': brand_name
        }
        
        def run_demo_thread():
            try:
                # Import and run the demo components
                from brand_monitoring_agent import search_brand_mentions, analyze_brand_sentiment, generate_brand_report
                
                # Step 1: Search
                search_result = search_brand_mentions.func(brand_name, 5)
                search_data = json.loads(search_result)
                
                time.sleep(2)  # Rate limiting
                
                # Step 2: Sentiment Analysis
                mock_content = json.dumps({
                    "scraped_data": [
                        {
                            "markdown": f"Recent news about {brand_name}: The company continues to innovate in AI technology with positive reception from the community."
                        }
                    ]
                })
                
                sentiment_result = analyze_brand_sentiment.func(mock_content, brand_name)
                sentiment_data = json.loads(sentiment_result)
                
                time.sleep(2)  # Rate limiting
                
                # Step 3: Generate Report
                report = generate_brand_report.func(brand_name, search_result, sentiment_result)
                
                # Save complete result
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"demo_{brand_name}_{timestamp}.json"
                file_path = os.path.join(RESULTS_DIR, filename)
                
                with open(file_path, 'w') as f:
                    json.dump({
                        'type': 'demo',
                        'brand_name': brand_name,
                        'timestamp': datetime.now().isoformat(),
                        'search_data': search_data,
                        'sentiment_data': sentiment_data,
                        'report': report
                    }, f, indent=2)
                
                running_processes[process_id].update({
                    'status': 'completed',
                    'end_time': datetime.now().isoformat(),
                    'filename': filename
                })
                
            except Exception as e:
                running_processes[process_id].update({
                    'status': 'failed',
                    'end_time': datetime.now().isoformat(),
                    'error': str(e)
                })
        
        # Start the thread
        thread = threading.Thread(target=run_demo_thread)
        thread.start()
        
        return jsonify({
            'success': True,
            'process_id': process_id,
            'message': 'Demo started successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/process-status/<process_id>')
def get_process_status(process_id):
    """API endpoint to get process status"""
    if process_id in running_processes:
        return jsonify({
            'success': True,
            'status': running_processes[process_id]
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Process not found'
        }), 404

@app.route('/api/results')
def get_results():
    """API endpoint to get all brand monitoring results"""
    try:
        # Get all JSON result files
        result_files = glob.glob(f"{RESULTS_DIR}/*.json")
        results = []
        
        for file_path in sorted(result_files, key=os.path.getmtime, reverse=True):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    data['filename'] = os.path.basename(file_path)
                    data['file_size'] = os.path.getsize(file_path)
                    data['modified'] = datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                    results.append(data)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        return jsonify({
            'success': True,
            'results': results,
            'total_files': len(results)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/system-status')
def get_system_status():
    """API endpoint to get system status"""
    try:
        # Test basic imports
        status = {
            'bedrock': False,
            'crewai': False,
            'search': False,
            'sentiment': False
        }
        
        try:
            import boto3
            bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
            status['bedrock'] = True
        except:
            pass
        
        try:
            from crewai import Agent, Crew, Task, LLM
            status['crewai'] = True
        except:
            pass
        
        try:
            from brand_monitoring_agent import search_brand_mentions
            status['search'] = True
        except:
            pass
        
        try:
            from brand_monitoring_agent import analyze_brand_sentiment
            status['sentiment'] = True
        except:
            pass
        
        return jsonify({
            'success': True,
            'status': status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/test-bedrock')
def test_bedrock():
    """API endpoint to test Bedrock connection"""
    try:
        import boto3
        import json
        
        bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 50,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, respond with just 'Hi'"
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
        
        return jsonify({
            'success': True,
            'response': content,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Enhanced Brand Monitoring Frontend...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("📁 Results will be saved to: ./results/")
    print("🔧 Interactive features enabled!")
    app.run(debug=True, host='0.0.0.0', port=5000)
