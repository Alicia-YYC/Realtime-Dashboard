#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-time Dashboard Launcher
Real-time Data Visualization Dashboard Launcher Script
"""

import os
import sys
import subprocess
import time

def check_requirements():
    """Check and install necessary dependencies"""
    print("🔍 Checking dependencies...")
    
    try:
        import dash
        import plotly
        import pandas
        import requests
        import bs4
        import yfinance
        import psutil
        print("✅ All dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Auto-installing dependencies...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            print("💡 Please run manually: pip install -r requirements.txt")
            return False

def create_env_file():
    """Create environment variables file"""
    if not os.path.exists('.env'):
        print("🔧 Creating environment file...")
        with open('.env', 'w', encoding='utf-8') as f:
            f.write('# Weather API Key (Optional, leave empty to use mock data)\n')
            f.write('# Get free API key from: https://openweathermap.org/api\n')
            f.write('WEATHER_API_KEY=\n')
        print("✅ Created .env file")

def main():
    """Main startup function"""
    print("🔴 REAL-TIME DATA DASHBOARD LAUNCHER")
    print("=" * 60)
    
    # Check dependencies
    if not check_requirements():
        return
    
    # Create environment variables file
    create_env_file()
    
    print("\n🎯 STARTUP INFO:")
    print("   - Access URL: http://127.0.0.1:8050")
    print("   - Update Interval: 30 seconds")
    print("   - Data Sources: Weather, Stocks, News, Crypto")
    print("   - Style: Hacker Matrix Theme")
    print("   - Press Ctrl+C to EXIT")
    print("\n" + "=" * 60)
    
    # Launch application
    try:
        print("🔥 LAUNCHING HACKER DASHBOARD...")
        time.sleep(2)
        
        # Import and run main application
        from app import app
        import config
        
        app.run_server(
            host=config.APP_HOST,
            port=config.APP_PORT,
            debug=False,  # Close debug mode for production environment
            dev_tools_hot_reload=False
        )
        
    except KeyboardInterrupt:
        print("\n👋 DASHBOARD TERMINATED")
    except Exception as e:
        print(f"\n❌ LAUNCH FAILED: {e}")
        print("💡 TROUBLESHOOTING:")
        print("   - Check if port 8050 is available")
        print("   - Ensure all dependencies are installed")
        print("   - Verify Python version is 3.7+")
        print("   - Check network connection for data sources")

if __name__ == "__main__":
    main()
