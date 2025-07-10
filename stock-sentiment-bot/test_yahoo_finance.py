#!/usr/bin/env python3
"""
Test script to verify Yahoo Finance integration works correctly
"""

from sentiment_bot_enhanced import StockSentimentBot

def test_yahoo_finance():
    """
    Test Yahoo Finance news fetching functionality
    """
    print("🚀 Testing Yahoo Finance Integration")
    print("=" * 50)
    
    try:
        bot = StockSentimentBot()
        
        # Test cases for different markets
        test_symbols = [
            "AAPL",        # US stock
            "RELIANCE.NS", # Indian stock
            "MSFT",        # US tech stock
            "TSLA"         # Popular stock
        ]
        
        for symbol in test_symbols:
            print(f"\n📊 Testing news fetch for: {symbol}")
            print("-" * 30)
            
            articles = bot.fetch_news(symbol)
            
            if articles:
                print(f"✅ Successfully fetched {len(articles)} articles")
                
                # Show first article as example
                if len(articles) > 0:
                    first_article = articles[0]
                    print(f"   Sample headline: {first_article['title'][:80]}...")
                    print(f"   Source: {first_article['source']}")
                    print(f"   Has description: {'Yes' if first_article['description'] else 'No'}")
            else:
                print(f"❌ No articles found for {symbol}")
                
        print(f"\n" + "=" * 50)
        print("✅ Yahoo Finance integration test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_company_name_resolution():
    """
    Test company name to ticker resolution
    """
    print("\n🧪 Testing Company Name Resolution")
    print("=" * 50)
    
    try:
        bot = StockSentimentBot()
        
        test_cases = [
            "Apple",
            "Reliance Industries", 
            "Microsoft",
            "Tesla",
            "Google",
            "AAPL"  # Test ticker pass-through
        ]
        
        for company in test_cases:
            ticker = bot.find_stock_ticker(company)
            print(f"'{company}' → {ticker}")
            
    except Exception as e:
        print(f"❌ Company name resolution test failed: {e}")

if __name__ == "__main__":
    test_yahoo_finance()
    test_company_name_resolution()
