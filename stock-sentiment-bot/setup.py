#!/usr/bin/env python3
"""
Setup script for Stock Sentiment Analysis Bot
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Stock Sentiment Analysis Bot")
    print("=" * 50)
    
    # Check if we're in a virtual environment
    if sys.prefix == sys.base_prefix:
        print("⚠️  Warning: You're not in a virtual environment")
        print("   It's recommended to use a virtual environment")
        response = input("Continue anyway? (y/n): ").lower()
        if response != 'y':
            print("👋 Setup cancelled")
            return
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return
    
    # Download TextBlob corpora
    print("📚 Downloading TextBlob corpora...")
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('brown', quiet=True)
        print("✅ TextBlob corpora downloaded successfully")
    except Exception as e:
        print(f"⚠️  Warning: Could not download TextBlob corpora: {e}")
        print("   The bot will still work, but accuracy might be reduced")
    
    # Create .env file if it doesn't exist
    env_file = Path('.env')
    if not env_file.exists():
        print("🔧 Creating .env file...")
        with open('.env', 'w') as f:
            f.write("# NewsAPI Configuration\n")
            f.write("# Get your free API key from: https://newsapi.org/register\n")
            f.write("NEWS_API_KEY=\n")
        print("✅ .env file created")
        print("📝 Please add your NewsAPI key to the .env file")
    else:
        print("✅ .env file already exists")
    
    # Test import
    print("🧪 Testing imports...")
    try:
        from sentiment_bot import StockSentimentBot
        print("✅ All imports successful")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Please check your Python environment")
        return
    
    print("\n🎉 Setup completed successfully!")
    print("=" * 50)
    print("Next steps:")
    print("1. Get your free NewsAPI key from: https://newsapi.org/register")
    print("2. Add your API key to the .env file")
    print("3. Run the bot: python sentiment_bot.py")
    print("\n⚠️  Remember: This is for educational purposes only!")

if __name__ == "__main__":
    main()
