# Stock Sentiment Analysis Bot 📈

An AI-powered sentiment analysis tool that provides buy/sell/hold recommendations for stocks based on recent news sentiment analysis.

## Features

- 🔍 **Real-time News Analysis**: Fetches latest news articles from NewsAPI
- 🤖 **Dual Sentiment Analysis**: Uses both TextBlob and VADER for accurate sentiment scoring
- 📊 **Comprehensive Reports**: Provides detailed sentiment distribution and confidence levels
- 🎯 **Trading Recommendations**: Generates actionable buy/sell/hold suggestions
- 🧹 **Data Cleaning**: Removes duplicates and irrelevant articles
- 🔐 **Secure**: Uses environment variables for API keys
- ⚡ **Error Handling**: Robust error handling for API calls and data processing

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd stock-sentiment-bot
   ```

2. **Activate the virtual environment**:
   ```bash
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   - Copy `.env.example` to `.env`
   - Get your free NewsAPI key from [newsapi.org](https://newsapi.org/register)
   - Add your API key to the `.env` file:
     ```
     NEWS_API_KEY=your_actual_api_key_here
     ```

## Usage

1. **Run the sentiment analysis bot**:
   ```bash
   python sentiment_bot.py
   ```

2. **Enter a stock symbol** when prompted (e.g., AAPL, TSLA, GOOGL, MSFT)

3. **View the analysis results**:
   - Average sentiment score (-1 to +1)
   - Sentiment distribution (Positive/Negative/Neutral percentages)
   - Trading recommendation (BUY/SELL/HOLD)
   - Confidence level
   - Recent headlines analyzed

## How It Works

### 1. News Fetching
- Searches for articles related to the stock symbol
- Fetches articles from the past 7 days
- Uses multiple search queries to ensure comprehensive coverage

### 2. Data Processing
- Removes duplicate articles
- Filters out irrelevant or low-quality content
- Cleans and preprocesses text data

### 3. Sentiment Analysis
- **TextBlob**: Provides polarity and subjectivity scores
- **VADER**: Specialized for social media and informal text
- **Combined Score**: Averages both methods for accuracy

### 4. Trading Recommendation Logic
- **BUY**: Strong positive sentiment (≥0.1) with 60%+ positive articles
- **SELL**: Strong negative sentiment (≤-0.1) with 60%+ negative articles
- **HOLD**: Mixed, neutral, or moderate sentiment

### 5. Confidence Calculation
- Based on the absolute value of the average sentiment score
- Higher confidence indicates stronger sentiment signals

## Example Output

```
🔍 Analyzing sentiment for AAPL...
==================================================
📰 Fetching latest news...
📊 Found 45 articles
🧹 Cleaning and deduplicating articles...
✅ 23 articles after cleaning
🤖 Analyzing sentiment...

📈 SENTIMENT ANALYSIS RESULTS
==================================================
Stock Symbol: AAPL
Analysis Period: Last 7 days
Articles Analyzed: 23
Average Sentiment Score: 0.156
Sentiment Scale: -1 (Very Negative) to +1 (Very Positive)

📊 SENTIMENT DISTRIBUTION
------------------------------
Positive: 65.2% (15 articles)
Neutral: 26.1% (6 articles)
Negative: 8.7% (2 articles)

🎯 TRADING RECOMMENDATION: BUY
Reasoning: Strong positive sentiment indicates potential upward movement
Confidence Level: 15.6%
```

## Dependencies

- `requests`: For API calls to NewsAPI
- `pandas`: For data manipulation and cleaning
- `textblob`: For sentiment analysis
- `vaderSentiment`: For social media sentiment analysis
- `python-dotenv`: For environment variable management
- `numpy`: For numerical operations

## API Requirements

### NewsAPI
- **Free Tier**: 1,000 requests per month
- **Rate Limit**: 1,000 requests per day
- **Features**: Access to news articles from 80,000+ sources
- **Sign up**: [newsapi.org/register](https://newsapi.org/register)

## Limitations

- **News Coverage**: Dependent on NewsAPI's article availability
- **Sentiment Context**: May not capture market-specific nuances
- **Historical Data**: Limited to recent articles (past 7 days)
- **Market Factors**: Doesn't consider technical analysis or financial metrics

## Disclaimer

⚠️ **Important**: This tool is for educational and research purposes only. It should not be used as the sole basis for investment decisions. Always consult with financial advisors and conduct thorough research before making investment choices.

## Troubleshooting

### Common Issues

1. **"NEWS_API_KEY environment variable is required"**
   - Ensure you've created a `.env` file with your API key
   - Check that the key is correctly formatted

2. **"No news articles found"**
   - Verify your internet connection
   - Check if the stock symbol is correct
   - Ensure your API key is valid and not expired

3. **"API Error: Rate limit exceeded"**
   - You've reached your daily API limit
   - Wait 24 hours or upgrade your NewsAPI plan

4. **Import errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Make sure you're using the correct Python environment

## Contributing

Feel free to contribute to this project by:
- Reporting bugs
- Suggesting new features
- Improving the sentiment analysis algorithms
- Adding new data sources
- Enhancing the trading recommendation logic

## License

This project is open source and available under the MIT License.
