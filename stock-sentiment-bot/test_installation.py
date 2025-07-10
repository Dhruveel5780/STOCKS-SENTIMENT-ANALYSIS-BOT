#!/usr/bin/env python3
"""
Test script to verify the Stock Sentiment Analysis Bot installation
"""

import sys
import os

def test_imports():
    """Test all required imports"""
    print("🧪 Testing imports...")
    
    try:
        import requests
        print("✅ requests imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import requests: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import pandas: {e}")
        return False
    
    try:
        from textblob import TextBlob
        print("✅ TextBlob imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import TextBlob: {e}")
        return False
    
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        print("✅ vaderSentiment imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import vaderSentiment: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import python-dotenv: {e}")
        return False
    
    return True

def test_sentiment_analysis():
    """Test basic sentiment analysis functionality"""
    print("\n🤖 Testing sentiment analysis...")
    
    try:
        from textblob import TextBlob
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        
        # Test TextBlob
        test_text = "Apple stock is performing very well this quarter with strong earnings."
        blob = TextBlob(test_text)
        tb_polarity = blob.sentiment.polarity
        print(f"✅ TextBlob sentiment for test text: {tb_polarity:.3f}")
        
        # Test VADER
        analyzer = SentimentIntensityAnalyzer()
        vader_score = analyzer.polarity_scores(test_text)['compound']
        print(f"✅ VADER sentiment for test text: {vader_score:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Sentiment analysis test failed: {e}")
        return False

def test_env_setup():
    """Test environment variable setup"""
    print("\n🔧 Testing environment setup...")
    
    if os.path.exists('.env'):
        print("✅ .env file exists")
        
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('NEWS_API_KEY')
        if api_key:
            if api_key.strip() and api_key != 'your_news_api_key_here':
                print("✅ NEWS_API_KEY is set")
                return True
            else:
                print("⚠️  NEWS_API_KEY is empty or contains placeholder value")
                print("   Please add your actual NewsAPI key to the .env file")
                return False
        else:
            print("⚠️  NEWS_API_KEY not found in .env file")
            print("   Please add your NewsAPI key to the .env file")
            return False
    else:
        print("⚠️  .env file not found")
        print("   Please create a .env file with your NewsAPI key")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Stock Sentiment Analysis Bot Installation")
    print("=" * 60)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please check your installation.")
        return False
    
    # Test sentiment analysis
    if not test_sentiment_analysis():
        print("\n❌ Sentiment analysis tests failed.")
        return False
    
    # Test environment setup
    env_ok = test_env_setup()
    
    print("\n" + "=" * 60)
    
    if env_ok:
        print("🎉 All tests passed! The bot is ready to use.")
        print("Run: python sentiment_bot.py")
    else:
        print("⚠️  Tests completed with warnings.")
        print("The bot will work after you add your NewsAPI key to the .env file.")
        print("\nTo get your free API key:")
        print("1. Visit: https://newsapi.org/register")
        print("2. Sign up for a free account")
        print("3. Copy your API key to the .env file")
    
    print("\n📖 For more information, check the README.md file.")
    return True

if __name__ == "__main__":
    main()
