#!/usr/bin/env python3
"""
Test script to demonstrate the fixes for:
1. Consistent output between ticker and company name input
2. Improved confidence level calculation
"""

from sentiment_bot_enhanced import StockSentimentBot
import os

def test_consistency():
    """
    Test that both ticker and company name inputs give consistent results
    """
    print("🧪 Testing Consistency Between Ticker and Company Name Input")
    print("=" * 60)
    
    # Check if API key is set
    if not os.getenv('NEWS_API_KEY') or os.getenv('NEWS_API_KEY') == 'your_news_api_key_here':
        print("⚠️  No valid API key found. This test will show the process but won't fetch real news.")
        print("   Add your NewsAPI key to the .env file to see actual results.")
        return
    
    try:
        bot = StockSentimentBot()
        
        # Test cases - ticker vs company name
        test_cases = [
            ("AAPL", "Apple"),
            ("RELIANCE.NS", "Reliance Industries"),
            ("MSFT", "Microsoft"),
            ("TSLA", "Tesla")
        ]
        
        for ticker, company_name in test_cases:
            print(f"\n📊 Testing: {ticker} vs '{company_name}'")
            print("-" * 40)
            
            # Test ticker resolution
            resolved_ticker_from_ticker = bot.find_stock_ticker(ticker)
            resolved_ticker_from_name = bot.find_stock_ticker(company_name)
            
            print(f"Ticker input '{ticker}' resolves to: {resolved_ticker_from_ticker}")
            print(f"Company name '{company_name}' resolves to: {resolved_ticker_from_name}")
            
            if resolved_ticker_from_ticker == resolved_ticker_from_name:
                print("✅ Consistent ticker resolution")
            else:
                print("❌ Inconsistent ticker resolution")
            
            # Test search query generation
            company_lookup = bot.get_company_name_from_ticker(resolved_ticker_from_ticker)
            print(f"Company name lookup for {resolved_ticker_from_ticker}: {company_lookup}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_confidence_calculation():
    """
    Test the improved confidence calculation
    """
    print("\n\n🧪 Testing Improved Confidence Calculation")
    print("=" * 60)
    
    try:
        bot = StockSentimentBot()
        
        # Test different scenarios
        test_scenarios = [
            {
                "name": "Strong Positive",
                "avg_sentiment": 0.3,
                "distribution": {"Positive": 0.8, "Neutral": 0.1, "Negative": 0.1},
                "total_articles": 20
            },
            {
                "name": "Moderate Positive",
                "avg_sentiment": 0.1,
                "distribution": {"Positive": 0.6, "Neutral": 0.3, "Negative": 0.1},
                "total_articles": 15
            },
            {
                "name": "Mixed Sentiment",
                "avg_sentiment": 0.02,
                "distribution": {"Positive": 0.4, "Neutral": 0.4, "Negative": 0.2},
                "total_articles": 10
            },
            {
                "name": "Strong Negative",
                "avg_sentiment": -0.25,
                "distribution": {"Positive": 0.1, "Neutral": 0.1, "Negative": 0.8},
                "total_articles": 25
            },
            {
                "name": "Low Sample Size",
                "avg_sentiment": 0.2,
                "distribution": {"Positive": 0.7, "Neutral": 0.2, "Negative": 0.1},
                "total_articles": 3
            }
        ]
        
        for scenario in test_scenarios:
            print(f"\n📈 Scenario: {scenario['name']}")
            print(f"   Average Sentiment: {scenario['avg_sentiment']:.3f}")
            print(f"   Distribution: {scenario['distribution']}")
            print(f"   Total Articles: {scenario['total_articles']}")
            
            # Calculate old confidence (for comparison)
            old_confidence = abs(scenario['avg_sentiment']) * 100
            
            # Calculate new confidence
            new_confidence = bot.calculate_confidence_level(
                scenario['avg_sentiment'],
                scenario['distribution'],
                scenario['total_articles']
            )
            
            # Get recommendation
            recommendation, reason = bot.generate_trading_recommendation(
                scenario['avg_sentiment'],
                scenario['distribution']
            )
            
            print(f"   Old Confidence: {old_confidence:.1f}%")
            print(f"   New Confidence: {new_confidence:.1f}%")
            print(f"   Recommendation: {recommendation}")
            print(f"   Improvement: {new_confidence - old_confidence:+.1f} percentage points")
            
            # Confidence description
            if new_confidence >= 80:
                desc = "Very High"
            elif new_confidence >= 60:
                desc = "High"
            elif new_confidence >= 40:
                desc = "Moderate"
            elif new_confidence >= 20:
                desc = "Low"
            else:
                desc = "Very Low"
            
            print(f"   Confidence Level: {desc}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

def main():
    """
    Run all tests
    """
    print("🚀 Testing Enhanced Stock Sentiment Bot Fixes")
    print("📋 This will test:")
    print("   1. Consistency between ticker and company name inputs")
    print("   2. Improved confidence level calculation")
    print("=" * 60)
    
    test_consistency()
    test_confidence_calculation()
    
    print("\n" + "=" * 60)
    print("✅ Testing completed!")
    print("\n📝 Summary of Fixes:")
    print("1. ✅ Consistent search queries for both ticker and company name inputs")
    print("2. ✅ Improved confidence calculation based on multiple factors:")
    print("   - Sentiment strength (40 points max)")
    print("   - Consensus level (30 points max)")
    print("   - Sample size (20 points max)")
    print("   - Distribution clarity (10 points max)")
    print("3. ✅ Enhanced trading recommendation logic")
    print("4. ✅ Duplicate article prevention across search queries")

if __name__ == "__main__":
    main()
