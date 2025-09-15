#!/usr/bin/env python3
"""
Demo Startup Script
Starts the brand monitoring frontend and provides options to run the agent
"""

import subprocess
import sys
import os
import time
import webbrowser
from threading import Thread

def start_frontend():
    """Start the Flask frontend"""
    print("🚀 Starting Brand Monitoring Frontend...")
    try:
        # Change to frontend directory
        os.chdir('frontend')
        
        # Start Flask app
        subprocess.run([sys.executable, 'app.py'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped by user")
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")

def run_brand_monitoring():
    """Run the brand monitoring agent"""
    print("🤖 Running Brand Monitoring Agent...")
    try:
        # Go back to root directory
        os.chdir('..')
        
        # Run the brand monitoring agent with storage
        subprocess.run([sys.executable, 'brand_monitoring_agent_with_storage.py'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Brand monitoring stopped by user")
    except Exception as e:
        print(f"❌ Error running brand monitoring: {e}")

def main():
    """Main demo function"""
    print("🎯 Brand Monitoring Demo")
    print("=" * 50)
    print("This demo will:")
    print("1. Start the web frontend at http://localhost:5000")
    print("2. Provide options to run brand monitoring")
    print("3. Display results in the web interface")
    print()
    
    # Check if required files exist
    required_files = [
        'frontend/app.py',
        'frontend/templates/index.html',
        'data_storage.py',
        'brand_monitoring_agent_with_storage.py'
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print("❌ Missing required files:")
        for f in missing_files:
            print(f"   - {f}")
        print("\nPlease ensure all files are in place before running the demo.")
        return
    
    print("✅ All required files found!")
    print()
    
    # Start frontend in a separate thread
    frontend_thread = Thread(target=start_frontend, daemon=True)
    frontend_thread.start()
    
    # Wait a moment for frontend to start
    print("⏳ Starting frontend...")
    time.sleep(3)
    
    # Open browser
    try:
        webbrowser.open('http://localhost:5000')
        print("🌐 Frontend opened in browser: http://localhost:5000")
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print("🌐 Please manually open: http://localhost:5000")
    
    print()
    print("🎮 Demo Options:")
    print("1. Run brand monitoring agent (will save results to frontend)")
    print("2. View existing results in frontend")
    print("3. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == '1':
                print("\n🤖 Starting brand monitoring...")
                run_brand_monitoring()
                print("\n✅ Brand monitoring completed! Check the frontend for results.")
                
            elif choice == '2':
                print("\n🌐 Frontend is running at: http://localhost:5000")
                print("   - View all brand monitoring results")
                print("   - Search and filter results")
                print("   - View detailed JSON data")
                print("   - Delete old results")
                
            elif choice == '3':
                print("\n👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Demo stopped by user. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
