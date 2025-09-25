#!/usr/bin/env python3
"""
Simple script to run the Toronto Business Lead Generator demo app.
"""

import subprocess
import sys
import os

def main():
    """Run the Streamlit demo app."""
    
    print("🚀 Starting Toronto Business Lead Generator (Demo Version)...")
    print("The app will open in your browser at http://localhost:8501")
    print("Press Ctrl+C to stop the app")
    print()
    print("Note: This is a demo version with sample data.")
    print("For real data sources, use the full version with API keys.")
    print()
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app_minimal.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
