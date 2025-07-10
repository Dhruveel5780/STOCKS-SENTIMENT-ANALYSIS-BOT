#!/usr/bin/env python3
"""
Stock Sentiment Analysis Bot
Analyzes news sentiment for stock trading recommendations using RSS feeds
"""

import os
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv
import json
import feedparser
from urllib.parse import quote
import hashlib

# Load environment variables
load_dotenv()

class StockSentimentBot:
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
        print("ℹ️  Using RSS feeds for news data - no API key required!")
        
        # RSS feed URLs for trusted financial news sources
        self.rss_feeds = {
            'Moneycontrol': 'https://www.moneycontrol.com/rss/business.xml',
            'Economic Times': 'https://economictimes.indiatimes.com/rssfeedstopstories.cms',
            'Mint': 'https://www.livemint.com/rss/money'
        }
    
    def fetch_rss_news(self, rss_url, source_name):
        """
        Fetch news articles from RSS feed
        """
        try:
            print(f"   Fetching from {source_name}...")
            feed = feedparser.parse(rss_url)
            
            articles = []
            for entry in feed.entries:
                # Extract article data
                title = entry.get('title', 'No Title')
                description = entry.get('summary', entry.get('description', ''))
                link = entry.get('link', '')
                published = entry.get('published', '')
                
                # Only add articles with valid content
                if title and title != 'No Title':
                    articles.append({
                        'title': title,
                        'description': description,
                        'source': source_name,
                        'publishedAt': published,
                        'url': link,
                        'news_source': source_name
                    })
            
            print(f"   Retrieved {len(articles)} articles from {source_name}")
            return articles
            
        except Exception as e:
            print(f"   Error fetching from {source_name}: {e}")
            return []
    
    def fetch_google_news(self, query):
        """
        Fetch news from Google News RSS feed
        """
        try:
            encoded_query = quote(query)
            google_news_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
            
            print(f"   Fetching from Google News for: {query}")
            feed = feedparser.parse(google_news_url)
            
            articles = []
            for entry in feed.entries:
                title = entry.get('title', 'No Title')
                description = entry.get('summary', entry.get('description', ''))
                link = entry.get('link', '')
                published = entry.get('published', '')
                
                # Extract source from Google News title format
                source = 'Google News'
                if ' - ' in title:
                    title_parts = title.split(' - ')
                    if len(title_parts) >= 2:
                        source = title_parts[-1]
                        title = ' - '.join(title_parts[:-1])
                
                if title and title != 'No Title':
                    articles.append({
                        'title': title,
                        'description': description,
                        'source': source,
                        'publishedAt': published,
                        'url': link,
                        'news_source': 'Google News'
                    })
            
            print(f"   Retrieved {len(articles)} articles from Google News")
            return articles
            
        except Exception as e:
            print(f"   Error fetching from Google News: {e}")
            return []
    
    def fetch_news(self, stock_symbol, days_back=7, max_articles=10):
        """
        Fetch news articles for a given stock symbol from RSS feeds
        """
        try:
            all_articles = []
            
            # First, get targeted news from Google News (prioritize stock-specific content)
            search_queries = [
                f'{stock_symbol} stock',
                f'{stock_symbol} shares',
                f'{stock_symbol} earnings',
                f'{stock_symbol} financial results',
                f'{stock_symbol} quarterly',
                f'{stock_symbol} company news'
            ]
            
            for query in search_queries:
                google_articles = self.fetch_google_news(query)
                if google_articles:
                    all_articles.extend(google_articles)
            
            # Then, get articles from RSS feeds and filter for stock relevance
            for source_name, rss_url in self.rss_feeds.items():
                articles = self.fetch_rss_news(rss_url, source_name)
                if articles:
                    all_articles.extend(articles)
            
            # Strengthen filtering for stock relevance
            relevant_articles = []
            for article in all_articles:
                title_lower = article['title'].lower()
                desc_lower = article['description'].lower()
                symbol_lower = stock_symbol.lower()
                
                # Create a combined text for analysis
                combined_text = f"{title_lower} {desc_lower}"
                
                # Strong relevance criteria - stock symbol must appear OR
                # article must have multiple stock-related keywords
                stock_keywords = ['stock', 'shares', 'earnings', 'financial', 'quarterly', 
                                'revenue', 'profit', 'loss', 'market cap', 'dividend', 
                                'investor', 'trading', 'price target', 'analyst', 'forecast']
                
                # Count stock-related keywords in the text
                keyword_count = sum(1 for keyword in stock_keywords if keyword in combined_text)
                
                # Include article if:
                # 1. Stock symbol appears in title or description, OR
                # 2. At least 2 stock-related keywords appear in the content
                if (symbol_lower in title_lower or 
                    symbol_lower in desc_lower or 
                    keyword_count >= 2):
                    
                    # Additional filter: exclude very general news that might not be relevant
                    excluded_terms = ['general news', 'weather', 'politics', 'sports', 
                                    'entertainment', 'celebrity', 'movie', 'cricket', 
                                    'bollywood', 'fashion', 'lifestyle']
                    
                    # Skip if article contains excluded terms
                    if not any(term in combined_text for term in excluded_terms):
                        relevant_articles.append(article)
            
            # Sort by relevance (prioritize articles with stock symbol in title)
            relevant_articles.sort(key=lambda x: (
                stock_symbol.lower() in x['title'].lower(),
                stock_symbol.lower() in x['description'].lower()
            ), reverse=True)
            
            return relevant_articles[:max_articles * 2]  # Return more articles since we're filtering
            
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []
    
    def clean_and_deduplicate(self, articles):
        """
        Clean and remove duplicate articles
        """
        if not articles:
            return []
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(articles)
        
        # Remove articles with null titles or descriptions
        df = df.dropna(subset=['title', 'description'])
        
        # Remove duplicates based on title similarity
        df = df.drop_duplicates(subset=['title'], keep='first')
        
        # Filter out articles that might not be relevant
        df = df[df['title'].str.len() > 10]  # Remove very short titles
        
        # Remove duplicates based on URL if available
        if 'url' in df.columns:
            df = df.drop_duplicates(subset=['url'], keep='first')
        
        return df.to_dict('records')
    
    def analyze_sentiment_textblob(self, text):
        """
        Analyze sentiment using TextBlob
        Returns polarity (-1 to 1) and subjectivity (0 to 1)
        """
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity, blob.sentiment.subjectivity
        except Exception as e:
            print(f"TextBlob error: {e}")
            return 0, 0
    
    def analyze_sentiment_vader(self, text):
        """
        Analyze sentiment using VADER
        Returns compound score (-1 to 1)
        """
        try:
            scores = self.vader_analyzer.polarity_scores(text)
            return scores['compound']
        except Exception as e:
            print(f"VADER error: {e}")
            return 0
    
    def calculate_sentiment_scores(self, articles):
        """
        Calculate sentiment scores for all articles
        """
        sentiment_data = []
        
        for article in articles:
            # Combine title and description for analysis
            text = f"{article.get('title', '')} {article.get('description', '')}"
            
            # TextBlob analysis
            tb_polarity, tb_subjectivity = self.analyze_sentiment_textblob(text)
            
            # VADER analysis
            vader_score = self.analyze_sentiment_vader(text)
            
            # Average the two sentiment scores
            average_sentiment = (tb_polarity + vader_score) / 2
            
            sentiment_data.append({
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'source': article.get('source', 'Unknown'),
                'publishedAt': article.get('publishedAt', ''),
                'url': article.get('url', ''),
                'textblob_polarity': tb_polarity,
                'textblob_subjectivity': tb_subjectivity,
                'vader_score': vader_score,
                'average_sentiment': average_sentiment
            })
        
        return sentiment_data
    
    def classify_sentiment(self, score):
        """
        Classify sentiment score into categories
        """
        if score >= 0.05:
            return 'Positive'
        elif score <= -0.05:
            return 'Negative'
        else:
            return 'Neutral'
    
    def generate_trading_recommendation(self, avg_sentiment, sentiment_distribution):
        """
        Generate buy/sell/hold recommendation based on sentiment analysis
        """
        positive_ratio = sentiment_distribution.get('Positive', 0)
        negative_ratio = sentiment_distribution.get('Negative', 0)
        neutral_ratio = sentiment_distribution.get('Neutral', 0)
        
        # Decision logic
        if avg_sentiment >= 0.1 and positive_ratio >= 0.6:
            return "BUY", "Strong positive sentiment indicates potential upward movement"
        elif avg_sentiment >= 0.05 and positive_ratio >= 0.4:
            return "HOLD", "Moderately positive sentiment suggests maintaining position"
        elif avg_sentiment <= -0.1 and negative_ratio >= 0.6:
            return "SELL", "Strong negative sentiment indicates potential downward movement"
        elif avg_sentiment <= -0.05 and negative_ratio >= 0.4:
            return "HOLD", "Moderately negative sentiment suggests caution"
        else:
            return "HOLD", "Mixed or neutral sentiment suggests waiting for clearer signals"
    
    def analyze_stock_sentiment(self, stock_symbol):
        """
        Main method to analyze stock sentiment and provide recommendation
        """
        print(f"\n🔍 Analyzing sentiment for {stock_symbol.upper()}...")
        print("=" * 50)
        
        # Fetch news
        print("📰 Fetching latest news from RSS feeds...")
        articles = self.fetch_news(stock_symbol)
        
        if not articles:
            print("❌ No news articles found. Please check your stock symbol and internet connection.")
            return
        
        print(f"📊 Found {len(articles)} articles")
        
        # Clean and deduplicate
        print("🧹 Cleaning and deduplicating articles...")
        clean_articles = self.clean_and_deduplicate(articles)
        print(f"✅ {len(clean_articles)} articles after cleaning")
        
        if not clean_articles:
            print("❌ No valid articles found after cleaning.")
            return
        
        # Analyze sentiment
        print("🤖 Analyzing sentiment...")
        sentiment_data = self.calculate_sentiment_scores(clean_articles)
        
        # Calculate statistics
        sentiment_scores = [item['average_sentiment'] for item in sentiment_data]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        
        # Classify sentiments
        sentiment_labels = [self.classify_sentiment(score) for score in sentiment_scores]
        sentiment_counts = Counter(sentiment_labels)
        total_articles = len(sentiment_labels)
        
        sentiment_distribution = {
            label: count / total_articles 
            for label, count in sentiment_counts.items()
        }
        
        # Generate recommendation
        recommendation, reason = self.generate_trading_recommendation(avg_sentiment, sentiment_distribution)
        
        # Display results
        print("\n📈 SENTIMENT ANALYSIS RESULTS")
        print("=" * 50)
        print(f"Stock Symbol: {stock_symbol.upper()}")
        print(f"Analysis Period: Last 7 days")
        print(f"Articles Analyzed: {total_articles}")
        print(f"Average Sentiment Score: {avg_sentiment:.3f}")
        print(f"Sentiment Scale: -1 (Very Negative) to +1 (Very Positive)")
        
        print("\n📊 SENTIMENT DISTRIBUTION")
        print("-" * 30)
        for label, ratio in sentiment_distribution.items():
            percentage = ratio * 100
            print(f"{label}: {percentage:.1f}% ({sentiment_counts[label]} articles)")
        
        print(f"\n🎯 TRADING RECOMMENDATION: {recommendation}")
        print(f"Reasoning: {reason}")
        
        # Show confidence level
        confidence = abs(avg_sentiment) * 100
        print(f"Confidence Level: {confidence:.1f}%")
        
        # Show recent headlines
        print("\n📰 RECENT HEADLINES ANALYZED")
        print("-" * 50)
        for i, item in enumerate(sentiment_data[:5], 1):
            sentiment_label = self.classify_sentiment(item['average_sentiment'])
            print(f"{i}. [{sentiment_label}] {item['title']}")
            print(f"   Source: {item['source']} | Score: {item['average_sentiment']:.3f}")
            print()
        
        return {
            'stock_symbol': stock_symbol.upper(),
            'average_sentiment': avg_sentiment,
            'sentiment_distribution': sentiment_distribution,
            'recommendation': recommendation,
            'reason': reason,
            'confidence': confidence,
            'articles_analyzed': total_articles,
            'detailed_analysis': sentiment_data
        }

def main():
    """
    Main function to run the sentiment analysis bot
    """
    try:
        # Initialize the bot
        bot = StockSentimentBot()
        
        # Get stock symbol from user
        stock_symbol = input("Enter stock symbol (e.g., AAPL, TSLA, GOOGL): ").strip().upper()
        
        if not stock_symbol:
            print("❌ Please provide a valid stock symbol.")
            return
        
        # Analyze sentiment
        result = bot.analyze_stock_sentiment(stock_symbol)
        
        if result:
            print(f"\n✅ Analysis complete for {stock_symbol}")
            print("⚠️  Disclaimer: This is for educational purposes only. Not financial advice.")
        
    except KeyboardInterrupt:
        print("\n\n👋 Analysis interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check your API key and try again.")

if __name__ == "__main__":
    main()
