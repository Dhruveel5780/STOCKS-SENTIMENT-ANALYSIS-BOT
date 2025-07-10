# Quick Start Guide 🚀

## 1. Get Your API Key
1. Visit [newsapi.org/register](https://newsapi.org/register)
2. Sign up for a free account
3. Copy your API key

## 2. Configure the Bot
1. Open the `.env` file in the project folder
2. Replace `your_news_api_key_here` with your actual API key:
   ```
   NEWS_API_KEY=your_actual_api_key_here
   ```

## 3. Run the Bot
Open PowerShell/Command Prompt and run:
```bash
# Navigate to the project folder
cd stock-sentiment-bot

# Activate the virtual environment
venv\Scripts\activate

# Run the bot
python sentiment_bot.py
```

## 4. Analyze a Stock
When prompted, enter a stock symbol (e.g., AAPL, TSLA, GOOGL, MSFT)

## Example Analysis
```
🔍 Analyzing sentiment for AAPL...
📰 Fetching latest news...
📊 Found 25 articles
🧹 Cleaning and deduplicating articles...
✅ 18 articles after cleaning
🤖 Analyzing sentiment...

📈 SENTIMENT ANALYSIS RESULTS
Stock Symbol: AAPL
Average Sentiment Score: 0.234
Sentiment Distribution:
  Positive: 72.2% (13 articles)
  Neutral: 22.2% (4 articles)
  Negative: 5.6% (1 articles)

🎯 TRADING RECOMMENDATION: BUY
Reasoning: Strong positive sentiment indicates potential upward movement
```

## Troubleshooting
- **API Key Issues**: Make sure your key is correctly added to the `.env` file
- **No News Found**: Try different stock symbols or check your internet connection
- **Import Errors**: Ensure you've activated the virtual environment

## Popular Stock Symbols to Try
- **Tech**: AAPL, GOOGL, MSFT, TSLA, NVDA
- **Finance**: JPM, BAC, GS, WFC
- **Healthcare**: JNJ, PFE, UNH, MRK
- **Consumer**: AMZN, WMT, KO, PG

## ⚠️ Important Disclaimer
This tool is for educational purposes only. Always do your own research and consult financial advisors before making investment decisions.
