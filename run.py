#!/usr/bin/env python3
"""
Simple script to run the Toronto Business Lead Generator app.
"""

import subprocess
import sys
import os

def main():
    """Run the Streamlit app."""
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  Warning: .env file not found.")
        print("Please copy env_example.txt to .env and add your API keys.")
        print("You can still run the app, but some features may not work.")
        print()
    
    # Check if requirements are installed
    try:
        import streamlit
        import requests
        import pandas
        import openai
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)
    
    # Run the app
    print("🚀 Starting Toronto Business Lead Generator...")
    print("The app will open in your browser at http://localhost:8501")
    print("Press Ctrl+C to stop the app")
    print()
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
