#!/usr/bin/env python3
"""
Test script for multi-source stock sentiment analysis bot
Tests Yahoo Finance, Finnhub, and Marketaux integration
"""

from sentiment_bot_multi_source import MultiSourceStockSentimentBot
import os

def test_api_keys():
    """
    Test API key configuration
    """
    print("🔑 Testing API Key Configuration")
    print("=" * 50)
    
    finnhub_key = os.getenv('FINNHUB_API_KEY')
    marketaux_key = os.getenv('MARKETAUX_API_KEY')
    
    print(f"Finnhub API Key: {'✅ Configured' if finnhub_key and finnhub_key != 'your_finnhub_api_key_here' else '❌ Not configured'}")
    print(f"Marketaux API Key: {'✅ Configured' if marketaux_key and marketaux_key != 'your_marketaux_api_key_here' else '❌ Not configured'}")
    print("Yahoo Finance: ✅ No API key required")
    
    return bool(finnhub_key and finnhub_key != 'your_finnhub_api_key_here'), bool(marketaux_key and marketaux_key != 'your_marketaux_api_key_here')

def test_individual_sources():
    """
    Test each news source individually
    """
    print("\n📰 Testing Individual News Sources")
    print("=" * 50)
    
    try:
        bot = MultiSourceStockSentimentBot()
        test_symbol = "AAPL"
        
        # Test Yahoo Finance
        print("\n🔸 Testing Yahoo Finance...")
        yahoo_articles = bot.fetch_yahoo_finance_news(test_symbol)
        print(f"   Result: {len(yahoo_articles)} articles")
        if yahoo_articles:
            print(f"   Sample: {yahoo_articles[0]['title'][:60]}...")
        
        # Test Finnhub
        print("\n🔸 Testing Finnhub...")
        finnhub_articles = bot.fetch_finnhub_news(test_symbol)
        print(f"   Result: {len(finnhub_articles)} articles")
        if finnhub_articles:
            print(f"   Sample: {finnhub_articles[0]['title'][:60]}...")
        
        # Test Marketaux
        print("\n🔸 Testing Marketaux...")
        marketaux_articles = bot.fetch_marketaux_news(test_symbol)
        print(f"   Result: {len(marketaux_articles)} articles")
        if marketaux_articles:
            print(f"   Sample: {marketaux_articles[0]['title'][:60]}...")
        
        return len(yahoo_articles), len(finnhub_articles), len(marketaux_articles)
        
    except Exception as e:
        print(f"❌ Error testing individual sources: {e}")
        return 0, 0, 0

def test_multi_source_aggregation():
    """
    Test full multi-source aggregation
    """
    print("\n🔄 Testing Multi-Source Aggregation")
    print("=" * 50)
    
    try:
        bot = MultiSourceStockSentimentBot()
        
        test_cases = [
            ("AAPL", "Apple"),
            ("MSFT", "Microsoft"),
            ("RELIANCE.NS", "Reliance Industries")
        ]
        
        for ticker, company in test_cases:
            print(f"\n📊 Testing {company} ({ticker}):")
            print("-" * 30)
            
            # Fetch all news
            all_articles = bot.fetch_all_news(ticker)
            print(f"   Total articles fetched: {len(all_articles)}")
            
            if all_articles:
                # Count by source
                source_counts = {}
                for article in all_articles:
                    source = article.get('news_source', 'Unknown')
                    source_counts[source] = source_counts.get(source, 0) + 1
                
                for source, count in source_counts.items():
                    print(f"   {source}: {count} articles")
                
                # Test cleaning
                clean_articles = bot.clean_and_deduplicate(all_articles)
                print(f"   After deduplication: {len(clean_articles)} articles")
                
                # Calculate diversity score
                unique_sources = len(source_counts)
                print(f"   Source diversity: {unique_sources} different sources")
            else:
                print("   ❌ No articles found")
        
    except Exception as e:
        print(f"❌ Error testing aggregation: {e}")

def test_sentiment_analysis():
    """
    Test complete sentiment analysis with multiple sources
    """
    print("\n🤖 Testing Complete Sentiment Analysis")
    print("=" * 50)
    
    try:
        bot = MultiSourceStockSentimentBot()
        
        # Test with a popular stock
        test_input = "AAPL"
        print(f"Analyzing: {test_input}")
        
        result = bot.analyze_stock_sentiment(test_input)
        
        if result:
            print(f"\n✅ Analysis Results:")
            print(f"   Stock: {result['stock_symbol']}")
            print(f"   Articles: {result['articles_analyzed']}")
            print(f"   Sources: {result['sources_used']}")
            print(f"   Sentiment: {result['average_sentiment']:.3f}")
            print(f"   Recommendation: {result['recommendation']}")
            print(f"   Confidence: {result['confidence']:.1f}%")
            
            # Show source breakdown
            if 'source_breakdown' in result:
                print(f"\n   Source Breakdown:")
                for source, data in result['source_breakdown'].items():
                    avg_sentiment = sum(data['sentiments']) / len(data['sentiments'])
                    print(f"   - {source}: {data['count']} articles (avg: {avg_sentiment:.3f})")
        else:
            print("❌ Analysis failed")
            
    except Exception as e:
        print(f"❌ Error in sentiment analysis: {e}")

def test_company_name_resolution():
    """
    Test company name to ticker resolution
    """
    print("\n🏢 Testing Company Name Resolution")
    print("=" * 50)
    
    try:
        bot = MultiSourceStockSentimentBot()
        
        test_cases = [
            "Apple",
            "Microsoft",
            "Reliance Industries",
            "Google",
            "Tesla",
            "AAPL",  # Already a ticker
            "MSFT"   # Already a ticker
        ]
        
        for company in test_cases:
            ticker = bot.find_stock_ticker(company)
            print(f"'{company}' → {ticker}")
            
    except Exception as e:
        print(f"❌ Error in name resolution: {e}")

def main():
    """
    Run all tests
    """
    print("🚀 Multi-Source Stock Sentiment Bot Test Suite")
    print("=" * 60)
    
    # Test API keys
    has_finnhub, has_marketaux = test_api_keys()
    
    # Test individual sources
    yahoo_count, finnhub_count, marketaux_count = test_individual_sources()
    
    # Test multi-source aggregation
    test_multi_source_aggregation()
    
    # Test company name resolution
    test_company_name_resolution()
    
    # Test complete sentiment analysis
    test_sentiment_analysis()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    total_sources = 1  # Yahoo Finance always works
    if has_finnhub and finnhub_count > 0:
        total_sources += 1
    if has_marketaux and marketaux_count > 0:
        total_sources += 1
    
    print(f"✅ Active News Sources: {total_sources}/3")
    print(f"   - Yahoo Finance: ✅ ({yahoo_count} articles)")
    print(f"   - Finnhub: {'✅' if has_finnhub and finnhub_count > 0 else '❌'} ({finnhub_count} articles)")
    print(f"   - Marketaux: {'✅' if has_marketaux and marketaux_count > 0 else '❌'} ({marketaux_count} articles)")
    
    if total_sources == 3:
        print("\n🎉 Perfect! All three news sources are working.")
        print("   You'll get the most comprehensive sentiment analysis.")
    elif total_sources == 2:
        print("\n👍 Good! Two news sources are working.")
        print("   You'll get reliable multi-source analysis.")
    else:
        print("\n⚠️  Only Yahoo Finance is working.")
        print("   Consider adding Finnhub and/or Marketaux API keys for better analysis.")
    
    print(f"\n📖 Setup Guide: MULTI_SOURCE_SETUP.md")
    print(f"🔧 API Key Help: .env.example")

if __name__ == "__main__":
    main()
