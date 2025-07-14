#!/usr/bin/env python3
"""
Test script to evaluate the stock sentiment bot functionality
"""

from sentiment_bot_multi_source import MultiSourceStockSentimentBot
import sys

def test_bot():
    """Test the bot with various stocks"""
    print("🚀 Testing Stock Sentiment Analysis Bot")
    print("=" * 60)
    
    # Initialize bot
    bot = MultiSourceStockSentimentBot()
    
    # Test stocks
    test_stocks = ['AAPL', 'TSLA', 'RELIANCE.NS', 'INFY.NS', 'GOOGL']
    
    results = {}
    
    for stock in test_stocks:
        print(f'\n=== Testing {stock} ===')
        try:
            result = bot.analyze_stock_sentiment(stock)
            if result:
                results[stock] = result
                print(f'✅ Stock: {result["stock_symbol"]}')
                print(f'📊 Articles: {result["articles_analyzed"]}')
                print(f'💭 Sentiment: {result["average_sentiment"]:.3f}')
                print(f'🎯 Recommendation: {result["recommendation"]}')
                print(f'📈 Confidence: {result["confidence"]:.1f}%')
                print(f'📰 Sources: {result["sources_used"]}')
            else:
                print('❌ No results obtained')
        except Exception as e:
            print(f'❌ Error: {e}')
            continue
        print('\n' + '='*50)
    
    # Summary
    print(f"\n🎯 SUMMARY:")
    print(f"Tested {len(test_stocks)} stocks")
    print(f"Successful: {len(results)}")
    print(f"Failed: {len(test_stocks) - len(results)}")
    
    if results:
        print(f"\n📊 Results Summary:")
        for stock, result in results.items():
            print(f"{stock}: {result['recommendation']} (Confidence: {result['confidence']:.1f}%)")
    
    return results

if __name__ == "__main__":
    test_bot()
