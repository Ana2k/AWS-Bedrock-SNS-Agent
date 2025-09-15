#!/usr/bin/env python3
"""
Simple Flask Frontend for Brand Monitoring Results
Displays JSON results from brand monitoring tools in a clean web interface
"""

from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime
import glob

app = Flask(__name__)

# Ensure results directory exists
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

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

@app.route('/api/results/<filename>')
def get_specific_result(filename):
    """API endpoint to get a specific result file"""
    try:
        file_path = os.path.join(RESULTS_DIR, filename)
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/save-result', methods=['POST'])
def save_result():
    """API endpoint to save a new result"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        brand_name = data.get('brand_name', 'unknown').replace(' ', '_').lower()
        filename = f"brand_monitoring_{brand_name}_{timestamp}.json"
        file_path = os.path.join(RESULTS_DIR, filename)
        
        # Add metadata
        data['saved_at'] = datetime.now().isoformat()
        data['filename'] = filename
        
        # Save to file
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'message': 'Result saved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/delete-result/<filename>', methods=['DELETE'])
def delete_result(filename):
    """API endpoint to delete a result file"""
    try:
        file_path = os.path.join(RESULTS_DIR, filename)
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        os.remove(file_path)
        return jsonify({
            'success': True,
            'message': 'File deleted successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Brand Monitoring Frontend...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("📁 Results will be saved to: ./results/")
    app.run(debug=True, host='0.0.0.0', port=5000)
