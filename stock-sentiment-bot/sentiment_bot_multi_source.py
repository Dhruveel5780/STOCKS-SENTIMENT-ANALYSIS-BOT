#!/usr/bin/env python3
"""
Multi-Source Stock Sentiment Analysis Bot
Aggregates news from trusted Indian financial RSS feeds and Google News
for comprehensive sentiment analysis and trading recommendations
"""

import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import BertTokenizer, BertForSequenceClassification
import torch
from dotenv import load_dotenv
import json
import re
from difflib import get_close_matches
import time
import feedparser
from bs4 import BeautifulSoup
from urllib.parse import quote

# Load environment variables
load_dotenv()

class MultiSourceStockSentimentBot:
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
        
        # Initialize FINBERT for financial sentiment analysis
        print("🤖 Loading FINBERT model...")
        try:
            self.finbert_tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone')
            self.finbert_model = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone')
            print("✅ FINBERT model loaded successfully")
        except Exception as e:
            print(f"⚠️  Could not load FINBERT model: {e}")
            print("   Falling back to TextBlob + VADER only")
            self.finbert_tokenizer = None
            self.finbert_model = None
        
        # Initialize RSS feed sources - only trusted Indian financial news sources
        self.rss_sources = {
            'Moneycontrol': 'https://www.moneycontrol.com/rss/business.xml',
            'Economic Times': 'https://economictimes.indiatimes.com/rssfeedsdefault.cms',
            'Mint': 'https://www.livemint.com/rss/companies'
        }
        
        # Sources that don't have direct RSS feeds - will use Google News with source filtering
        self.google_news_sources = [
            'BQ Prime',
            'Reuters India', 
            'CNBC TV18'
        ]
        
        print("✅ RSS feed sources initialized")
        print(f"📰 Configured {len(self.rss_sources)} RSS sources")
        
        # Initialize company-to-ticker mapping
        self.company_ticker_map = self._load_company_ticker_mapping()
    
    def _load_company_ticker_mapping(self):
        """
        Load a comprehensive mapping of company names to stock tickers
        """
        return {
            # US Tech Giants
            'apple': 'AAPL',
            'apple inc': 'AAPL',
            'apple incorporated': 'AAPL',
            'apple company': 'AAPL',
            'microsoft': 'MSFT',
            'microsoft corporation': 'MSFT',
            'google': 'GOOGL',
            'alphabet': 'GOOGL',
            'alphabet inc': 'GOOGL',
            'amazon': 'AMZN',
            'amazon.com': 'AMZN',
            'amazon inc': 'AMZN',
            'tesla': 'TSLA',
            'tesla inc': 'TSLA',
            'tesla motors': 'TSLA',
            'meta': 'META',
            'facebook': 'META',
            'meta platforms': 'META',
            'nvidia': 'NVDA',
            'nvidia corporation': 'NVDA',
            'netflix': 'NFLX',
            'netflix inc': 'NFLX',
            'amd': 'AMD',
            'advanced micro devices': 'AMD',
            'intel': 'INTC',
            'intel corporation': 'INTC',
            'qualcomm': 'QCOM',
            'broadcom': 'AVGO',
            'oracle': 'ORCL',
            'salesforce': 'CRM',
            'adobe': 'ADBE',
            'adobe systems': 'ADBE',
            
            # Indian Companies
            'reliance': 'RELIANCE.NS',
            'reliance industries': 'RELIANCE.NS',
            'reliance industries limited': 'RELIANCE.NS',
            'ril': 'RELIANCE.NS',
            'tata consultancy services': 'TCS.NS',
            'tcs': 'TCS.NS',
            'infosys': 'INFY.NS',
            'infosys limited': 'INFY.NS',
            'hdfc bank': 'HDFCBANK.NS',
            'housing development finance corporation': 'HDFC.NS',
            'hdfc': 'HDFC.NS',
            'icici bank': 'ICICIBANK.NS',
            'icici': 'ICICIBANK.NS',
            'state bank of india': 'SBIN.NS',
            'sbi': 'SBIN.NS',
            'bharti airtel': 'BHARTIARTL.NS',
            'airtel': 'BHARTIARTL.NS',
            'itc': 'ITC.NS',
            'itc limited': 'ITC.NS',
            'hindustan unilever': 'HINDUNILVR.NS',
            'hul': 'HINDUNILVR.NS',
            'larsen and toubro': 'LT.NS',
            'l&t': 'LT.NS',
            'lt': 'LT.NS',
            'wipro': 'WIPRO.NS',
            'wipro limited': 'WIPRO.NS',
            'bajaj finance': 'BAJFINANCE.NS',
            'maruti suzuki': 'MARUTI.NS',
            'maruti': 'MARUTI.NS',
            'asian paints': 'ASIANPAINT.NS',
            'mahindra and mahindra': 'M&M.NS',
            'mahindra': 'M&M.NS',
            'm&m': 'M&M.NS',
            'tata motors': 'TATAMOTORS.NS',
            'sun pharmaceutical': 'SUNPHARMA.NS',
            'sun pharma': 'SUNPHARMA.NS',
            'axis bank': 'AXISBANK.NS',
            'kotak mahindra bank': 'KOTAKBANK.NS',
            'kotak bank': 'KOTAKBANK.NS',
            'kotak': 'KOTAKBANK.NS',
            'ultratech cement': 'ULTRACEMCO.NS',
            'ultratech': 'ULTRACEMCO.NS',
            'nestle india': 'NESTLEIND.NS',
            'nestle': 'NESTLEIND.NS',
            'power grid corporation': 'POWERGRID.NS',
            'powergrid': 'POWERGRID.NS',
            'ntpc': 'NTPC.NS',
            'coal india': 'COALINDIA.NS',
            'ongc': 'ONGC.NS',
            'oil and natural gas corporation': 'ONGC.NS',
            'indian oil corporation': 'IOC.NS',
            'ioc': 'IOC.NS',
            'grasim industries': 'GRASIM.NS',
            'grasim': 'GRASIM.NS',
            'adani enterprises': 'ADANIENT.NS',
            'adani': 'ADANIENT.NS',
            'bajaj auto': 'BAJAJ-AUTO.NS',
            'titan': 'TITAN.NS',
            'titan company': 'TITAN.NS',
            'dr reddy': 'DRREDDY.NS',
            'dr reddys laboratories': 'DRREDDY.NS',
            'dr reddy laboratories': 'DRREDDY.NS',
            'cipla': 'CIPLA.NS',
            'britannia industries': 'BRITANNIA.NS',
            'britannia': 'BRITANNIA.NS',
            'tech mahindra': 'TECHM.NS',
            'hero motocorp': 'HEROMOTOCO.NS',
            'hero': 'HEROMOTOCO.NS',
            'eicher motors': 'EICHERMOT.NS',
            'eicher': 'EICHERMOT.NS',
            'shree cement': 'SHREECEM.NS',
            'divis laboratories': 'DIVISLAB.NS',
            'divis lab': 'DIVISLAB.NS',
            'sbi life insurance': 'SBILIFE.NS',
            'sbi life': 'SBILIFE.NS',
            'hdfc life insurance': 'HDFCLIFE.NS',
            'hdfc life': 'HDFCLIFE.NS',
            'bajaj finserv': 'BAJAJFINSV.NS',
            'indusind bank': 'INDUSINDBK.NS',
            'indusind': 'INDUSINDBK.NS',
            'zee entertainment': 'ZEEL.NS',
            'zee': 'ZEEL.NS',
            'vedanta': 'VEDL.NS',
            'vedanta limited': 'VEDL.NS',
            'tata steel': 'TATASTEEL.NS',
            'jsw steel': 'JSWSTEEL.NS',
            'jsw': 'JSWSTEEL.NS',
            'hindalco': 'HINDALCO.NS',
            'hindalco industries': 'HINDALCO.NS',
            'upl': 'UPL.NS',
            'upl limited': 'UPL.NS',
            'hcl technologies': 'HCLTECH.NS',
            'hcl tech': 'HCLTECH.NS',
            'hcl': 'HCLTECH.NS',
            'godrej consumer products': 'GODREJCP.NS',
            'godrej': 'GODREJCP.NS',
            'dabur': 'DABUR.NS',
            'dabur india': 'DABUR.NS',
            'pidilite industries': 'PIDILITIND.NS',
            'pidilite': 'PIDILITIND.NS',
            'berger paints': 'BERGEPAINT.NS',
            'berger': 'BERGEPAINT.NS',
            'marico': 'MARICO.NS',
            'marico limited': 'MARICO.NS',
            'colgate palmolive': 'COLPAL.NS',
            'colgate': 'COLPAL.NS',
            'hindustan zinc': 'HINDZINC.NS',
            'hindzinc': 'HINDZINC.NS',
            'muthoot finance': 'MUTHOOTFIN.NS',
            'muthoot': 'MUTHOOTFIN.NS',
            'bajaj holdings': 'BAJAJHLDNG.NS',
            'avenue supermarts': 'DMART.NS',
            'dmart': 'DMART.NS',
            'info edge': 'NAUKRI.NS',
            'naukri': 'NAUKRI.NS',
            'zomato': 'ZOMATO.NS',
            'paytm': 'PAYTM.NS',
            'one97 communications': 'PAYTM.NS',
            'policybazaar': 'POLICYBZR.NS',
            'pb fintech': 'POLICYBZR.NS',
            'nykaa': 'NYKAA.NS',
            'fsl nykaa': 'NYKAA.NS',
            
            # US Financial
            'jpmorgan': 'JPM',
            'jpmorgan chase': 'JPM',
            'jp morgan': 'JPM',
            'bank of america': 'BAC',
            'wells fargo': 'WFC',
            'goldman sachs': 'GS',
            'morgan stanley': 'MS',
            'citigroup': 'C',
            'citi': 'C',
            'american express': 'AXP',
            'amex': 'AXP',
            'visa': 'V',
            'mastercard': 'MA',
            'berkshire hathaway': 'BRK.A',
            'berkshire': 'BRK.A',
            
            # US Healthcare
            'johnson and johnson': 'JNJ',
            'johnson & johnson': 'JNJ',
            'j&j': 'JNJ',
            'pfizer': 'PFE',
            'merck': 'MRK',
            'merck & co': 'MRK',
            'abbott': 'ABT',
            'abbott laboratories': 'ABT',
            'bristol myers squibb': 'BMY',
            'bms': 'BMY',
            'eli lilly': 'LLY',
            'lilly': 'LLY',
            'unitedhealth': 'UNH',
            'united health': 'UNH',
            
            # US Consumer
            'walmart': 'WMT',
            'wal-mart': 'WMT',
            'target': 'TGT',
            'costco': 'COST',
            'home depot': 'HD',
            'lowes': 'LOW',
            'starbucks': 'SBUX',
            'mcdonalds': 'MCD',
            'mcdonald\'s': 'MCD',
            'coca cola': 'KO',
            'coca-cola': 'KO',
            'pepsi': 'PEP',
            'pepsico': 'PEP',
            'procter gamble': 'PG',
            'procter & gamble': 'PG',
            'p&g': 'PG',
            'nike': 'NKE',
            'disney': 'DIS',
            'walt disney': 'DIS',
            'comcast': 'CMCSA',
            'at&t': 'T',
            'att': 'T',
            'verizon': 'VZ',
            't-mobile': 'TMUS',
            'tmobile': 'TMUS',
            'general motors': 'GM',
            'gm': 'GM',
            'ford': 'F',
            'ford motor': 'F',
            
            # US Industrial
            'boeing': 'BA',
            'caterpillar': 'CAT',
            'general electric': 'GE',
            'ge': 'GE',
            'honeywell': 'HON',
            '3m': 'MMM',
            'mmm': 'MMM',
            
            # Energy
            'chevron': 'CVX',
            'exxon mobil': 'XOM',
            'exxon': 'XOM',
            'conocophillips': 'COP',
            'schlumberger': 'SLB',
            'halliburton': 'HAL',
        }
    
    def find_stock_ticker(self, company_input):
        """
        Find stock ticker from company name or return as-is if it's already a ticker
        """
        # Clean the input
        cleaned_input = company_input.strip().lower()
        
        # First check for direct match in our mapping (prioritize known companies)
        if cleaned_input in self.company_ticker_map:
            return self.company_ticker_map[cleaned_input]
        
        # Try fuzzy matching for close matches
        close_matches = get_close_matches(cleaned_input, self.company_ticker_map.keys(), n=1, cutoff=0.8)
        if close_matches:
            return self.company_ticker_map[close_matches[0]]
        
        # Try partial matching (more aggressive)
        for company_name, ticker in self.company_ticker_map.items():
            if cleaned_input in company_name or company_name in cleaned_input:
                return ticker
        
        # Check if it's already a valid ticker (short alphanumeric string with optional suffix)
        if re.match(r'^[A-Z]{1,6}(\.[A-Z]{1,3})?$', company_input.upper()):
            return company_input.upper()
        
        # Return original input if no match found
        return company_input.upper()
    
    def get_company_suggestions(self, partial_name):
        """
        Get suggestions for partial company names
        """
        partial_name = partial_name.lower()
        suggestions = []
        
        # Direct matches first
        for company_name, ticker in self.company_ticker_map.items():
            if company_name.startswith(partial_name):
                suggestions.append(f"{company_name.title()} ({ticker})")
        
        # Then partial matches
        for company_name, ticker in self.company_ticker_map.items():
            if partial_name in company_name and f"{company_name.title()} ({ticker})" not in suggestions:
                suggestions.append(f"{company_name.title()} ({ticker})")
        
        return suggestions[:10]  # Return top 10 suggestions
    
    def fetch_rss_news(self, source_name, rss_url, search_terms):
        """
        Fetch news from RSS feeds and filter by search terms
        """
        articles = []
        try:
            print(f"   📰 {source_name}: Querying RSS feed...")
            
            # Parse RSS feed
            feed = feedparser.parse(rss_url)
            
            if not feed.entries:
                print(f"   ⚠️  {source_name}: No entries found in RSS feed")
                return articles
            
            # Filter articles by search terms
            for entry in feed.entries:
                title = entry.get('title', '')
                description = entry.get('description', '') or entry.get('summary', '')
                published = entry.get('published', '') or entry.get('updated', '')
                url = entry.get('link', '')
                
                # Check if any search term is in title or description
                content_text = f"{title} {description}".lower()
                if any(term.lower() in content_text for term in search_terms):
                    # Clean HTML tags from description if present
                    if description:
                        description = BeautifulSoup(description, 'html.parser').get_text()
                    
                    articles.append({
                        'title': title,
                        'description': description,
                        'source': source_name,
                        'publishedAt': published,
                        'url': url,
                        'news_source': source_name
                    })
            
            print(f"   ✅ {source_name}: Found {len(articles)} relevant articles")
            return articles
            
        except Exception as e:
            print(f"   ❌ {source_name} RSS error: {e}")
            return []
    
    def fetch_google_news_rss(self, search_terms):
        """
        Fetch news from Google News RSS feed as fallback
        """
        articles = []
        try:
            print(f"   📰 Google News: Searching for {', '.join(search_terms)}...")
            
            # Create Google News RSS URL
            query = ' OR '.join(search_terms)
            encoded_query = quote(query)
            google_news_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN%3Aen"
            
            # Parse RSS feed
            feed = feedparser.parse(google_news_url)
            
            if not feed.entries:
                print(f"   ⚠️  Google News: No entries found")
                return articles
            
            # Process entries
            for entry in feed.entries:
                title = entry.get('title', '')
                description = entry.get('description', '') or entry.get('summary', '')
                published = entry.get('published', '') or entry.get('updated', '')
                url = entry.get('link', '')
                
                # Clean HTML tags from description if present
                if description:
                    description = BeautifulSoup(description, 'html.parser').get_text()
                
                articles.append({
                    'title': title,
                    'description': description,
                    'source': 'Google News',
                    'publishedAt': published,
                    'url': url,
                    'news_source': 'Google News'
                })
            
            print(f"   ✅ Google News: Found {len(articles)} articles")
            return articles
            
        except Exception as e:
            print(f"   ❌ Google News RSS error: {e}")
            return []
    
    def generate_search_terms(self, stock_symbol, company_input):
        """
        Generate search terms for news filtering
        """
        search_terms = []
        
        # Add the original company input
        search_terms.append(company_input)
        
        # Add stock symbol without exchange suffix
        base_symbol = stock_symbol.replace('.NS', '').replace('.BO', '')
        search_terms.append(base_symbol)
        
        # Add company name if we can find it in our mapping
        for company_name, ticker in self.company_ticker_map.items():
            if ticker == stock_symbol:
                search_terms.append(company_name)
                # Also add title case version
                search_terms.append(company_name.title())
                break
        
        # Remove duplicates while preserving order
        unique_terms = []
        for term in search_terms:
            if term not in unique_terms:
                unique_terms.append(term)
        
        return unique_terms
    
    def fetch_all_news(self, stock_symbol, company_input):
        """
        Aggregate news from all RSS sources and Google News
        """
        print(f"📰 Fetching news from RSS feeds for {stock_symbol}...")
        
        # Generate search terms for filtering
        search_terms = self.generate_search_terms(stock_symbol, company_input)
        print(f"🔍 Search terms: {', '.join(search_terms)}")
        
        all_articles = []
        
        # Fetch from RSS sources
        for source_name, rss_url in self.rss_sources.items():
            articles = self.fetch_rss_news(source_name, rss_url, search_terms)
            all_articles.extend(articles)
            
            # Add small delay between RSS calls
            time.sleep(0.5)
        
        # If we don't have enough articles, fetch from Google News as fallback
        if len(all_articles) < 5:
            print(f"\n📰 Fetching additional news from Google News...")
            google_articles = self.fetch_google_news_rss(search_terms)
            all_articles.extend(google_articles)
        
        # Display source summary
        source_counts = {}
        for article in all_articles:
            source = article.get('news_source', 'Unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        print(f"\n📊 News Source Summary:")
        for source, count in source_counts.items():
            print(f"   {source}: {count} articles")
        
        return all_articles
    
    def clean_and_deduplicate(self, articles):
        """
        Clean and remove duplicate articles across all sources
        """
        if not articles:
            return []
        
        print(f"🧹 Cleaning and deduplicating {len(articles)} articles...")
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(articles)
        
        # Remove articles with null titles or descriptions
        df = df.dropna(subset=['title', 'description'])
        
        # Remove duplicates based on title similarity (case-insensitive)
        df = df.drop_duplicates(subset=['title'], keep='first')
        
        # Filter out articles that might not be relevant
        df = df[df['title'].str.len() > 10]  # Remove very short titles
        
        # Remove articles with very similar titles (to catch slight variations)
        # This is more aggressive deduplication
        cleaned_articles = []
        seen_titles = []
        
        for _, row in df.iterrows():
            current_title = row['title'].lower().strip()
            is_duplicate = False
            
            for seen_title in seen_titles:
                # Check if titles are very similar (>80% similarity)
                if self._similarity(current_title, seen_title) > 0.8:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                seen_titles.append(current_title)
                cleaned_articles.append(row.to_dict())
        
        print(f"✅ After cleaning: {len(cleaned_articles)} unique articles")
        return cleaned_articles
    
    def _similarity(self, a, b):
        """
        Calculate similarity between two strings
        """
        from difflib import SequenceMatcher
        return SequenceMatcher(None, a, b).ratio()
    
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
    
    def analyze_sentiment_finbert(self, text):
        """
        Analyze sentiment using FINBERT
        Returns sentiment score (-1 to 1) and probabilities
        """
        if self.finbert_tokenizer is None or self.finbert_model is None:
            return 0, [0, 0, 0]  # neutral sentiment if model not available
        
        try:
            # Truncate text to max length for BERT (512 tokens)
            max_length = 512
            inputs = self.finbert_tokenizer.encode_plus(
                text,
                add_special_tokens=True,
                max_length=max_length,
                padding='max_length',
                truncation=True,
                return_attention_mask=True,
                return_tensors='pt'
            )
            
            with torch.no_grad():
                outputs = self.finbert_model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                probabilities = predictions[0].detach().numpy()
            
            # FINBERT output classes: [negative, neutral, positive]
            # Convert to sentiment score (-1 to 1)
            sentiment_score = probabilities[2] - probabilities[0]  # positive - negative
            
            return sentiment_score, probabilities.tolist()
            
        except Exception as e:
            print(f"FINBERT error: {e}")
            return 0, [0, 0, 0]
    
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
                'news_source': article.get('news_source', 'Unknown'),
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
    
    def calculate_confidence_level(self, avg_sentiment, sentiment_distribution, total_articles, source_diversity):
        """
        Calculate confidence level with source diversity factor
        """
        # Factor 1: Sentiment strength (0-35 points)
        sentiment_strength = min(abs(avg_sentiment) * 100, 35)
        
        # Factor 2: Consensus level (0-25 points)
        max_category_ratio = max(sentiment_distribution.values()) if sentiment_distribution else 0
        consensus_score = max_category_ratio * 25
        
        # Factor 3: Sample size factor (0-20 points)
        if total_articles >= 30:
            sample_score = 20
        elif total_articles >= 20:
            sample_score = 18
        elif total_articles >= 15:
            sample_score = 15
        elif total_articles >= 10:
            sample_score = 12
        elif total_articles >= 5:
            sample_score = 8
        else:
            sample_score = 4
        
        # Factor 4: Distribution clarity (0-10 points)
        neutral_ratio = sentiment_distribution.get('Neutral', 0)
        clarity_score = (1 - neutral_ratio) * 10
        
        # Factor 5: Source diversity bonus (0-10 points)
        # More diverse sources = higher confidence
        diversity_score = min(source_diversity * 3, 10)
        
        # Total confidence (0-100)
        total_confidence = sentiment_strength + consensus_score + sample_score + clarity_score + diversity_score
        
        return min(total_confidence, 100)  # Cap at 100%
    
    def generate_trading_recommendation(self, avg_sentiment, sentiment_distribution):
        """
        Generate buy/sell/hold recommendation based on sentiment analysis
        """
        positive_ratio = sentiment_distribution.get('Positive', 0)
        negative_ratio = sentiment_distribution.get('Negative', 0)
        neutral_ratio = sentiment_distribution.get('Neutral', 0)
        
        # Decision logic with more nuanced thresholds
        if avg_sentiment >= 0.15 and positive_ratio >= 0.7:
            return "BUY", "Very strong positive sentiment indicates potential upward movement"
        elif avg_sentiment >= 0.1 and positive_ratio >= 0.6:
            return "BUY", "Strong positive sentiment indicates potential upward movement"
        elif avg_sentiment >= 0.05 and positive_ratio >= 0.5:
            return "HOLD", "Moderately positive sentiment suggests maintaining position"
        elif avg_sentiment <= -0.15 and negative_ratio >= 0.7:
            return "SELL", "Very strong negative sentiment indicates potential downward movement"
        elif avg_sentiment <= -0.1 and negative_ratio >= 0.6:
            return "SELL", "Strong negative sentiment indicates potential downward movement"
        elif avg_sentiment <= -0.05 and negative_ratio >= 0.5:
            return "HOLD", "Moderately negative sentiment suggests caution"
        else:
            return "HOLD", "Mixed or neutral sentiment suggests waiting for clearer signals"
    
    def analyze_stock_sentiment(self, company_input):
        """
        Main method to analyze stock sentiment from multiple sources
        """
        # Convert company name to stock ticker
        print(f"\n🔍 Processing input: '{company_input}'")
        stock_symbol = self.find_stock_ticker(company_input)
        
        if stock_symbol != company_input.upper():
            print(f"📊 Found ticker: {stock_symbol} for '{company_input}'")
        else:
            print(f"📊 Using ticker: {stock_symbol}")
        
        print(f"\n🔍 Analyzing sentiment for {stock_symbol}...")
        print("=" * 60)
        
        # Fetch news from all sources
        articles = self.fetch_all_news(stock_symbol, company_input)
        
        if not articles:
            print(f"❌ No news articles found for {stock_symbol} from any source.")
            print("   This could be due to:")
            print("   - Invalid ticker symbol")
            print("   - No recent news available")
            print("   - API connectivity issues")
            return
        
        print(f"\n📊 Total articles fetched: {len(articles)}")
        
        # Clean and deduplicate
        clean_articles = self.clean_and_deduplicate(articles)
        
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
        
        # Calculate source diversity
        unique_sources = len(set(item['news_source'] for item in sentiment_data))
        
        # Generate recommendation
        recommendation, reason = self.generate_trading_recommendation(avg_sentiment, sentiment_distribution)
        
        # Calculate confidence with source diversity
        confidence = self.calculate_confidence_level(
            avg_sentiment, sentiment_distribution, total_articles, unique_sources
        )
        
        # Display results
        print("\n📈 MULTI-SOURCE SENTIMENT ANALYSIS RESULTS")
        print("=" * 60)
        print(f"Company: {company_input}")
        print(f"Stock Symbol: {stock_symbol}")
        print(f"Analysis Period: Last 7 days")
        print(f"Articles Analyzed: {total_articles}")
        print(f"News Sources: {unique_sources} different sources")
        print(f"Average Sentiment Score: {avg_sentiment:.3f}")
        print(f"Sentiment Scale: -1 (Very Negative) to +1 (Very Positive)")
        
        print("\n📊 SENTIMENT DISTRIBUTION")
        print("-" * 30)
        for label, ratio in sentiment_distribution.items():
            percentage = ratio * 100
            print(f"{label}: {percentage:.1f}% ({sentiment_counts[label]} articles)")
        
        print(f"\n🎯 TRADING RECOMMENDATION: {recommendation}")
        print(f"Reasoning: {reason}")
        
        # Show confidence level with description
        if confidence >= 85:
            confidence_desc = "Very High"
        elif confidence >= 70:
            confidence_desc = "High"
        elif confidence >= 55:
            confidence_desc = "Moderate-High"
        elif confidence >= 40:
            confidence_desc = "Moderate"
        elif confidence >= 25:
            confidence_desc = "Low"
        else:
            confidence_desc = "Very Low"
        
        print(f"Confidence Level: {confidence:.1f}% ({confidence_desc})")
        
        # Show source breakdown
        print("\n📰 NEWS SOURCE BREAKDOWN")
        print("-" * 40)
        source_breakdown = {}
        for item in sentiment_data:
            source = item['news_source']
            if source not in source_breakdown:
                source_breakdown[source] = {'count': 0, 'avg_sentiment': 0, 'sentiments': []}
            source_breakdown[source]['count'] += 1
            source_breakdown[source]['sentiments'].append(item['average_sentiment'])
        
        for source, data in source_breakdown.items():
            avg_source_sentiment = sum(data['sentiments']) / len(data['sentiments'])
            print(f"{source}: {data['count']} articles (avg sentiment: {avg_source_sentiment:.3f})")
        
        # Show recent headlines by source
        print("\n📰 RECENT HEADLINES BY SOURCE")
        print("-" * 50)
        for source in source_breakdown.keys():
            print(f"\n🔸 {source}:")
            source_articles = [item for item in sentiment_data if item['news_source'] == source]
            for i, item in enumerate(source_articles[:3], 1):  # Show top 3 from each source
                sentiment_label = self.classify_sentiment(item['average_sentiment'])
                print(f"   {i}. [{sentiment_label}] {item['title'][:80]}...")
                print(f"      Score: {item['average_sentiment']:.3f}")
        
        return {
            'company_input': company_input,
            'stock_symbol': stock_symbol,
            'average_sentiment': avg_sentiment,
            'sentiment_distribution': sentiment_distribution,
            'recommendation': recommendation,
            'reason': reason,
            'confidence': confidence,
            'articles_analyzed': total_articles,
            'sources_used': unique_sources,
            'source_breakdown': source_breakdown,
            'detailed_analysis': sentiment_data
        }

def main():
    """
    Main function to run the multi-source sentiment analysis bot
    """
    print("🚀 Welcome to the Multi-Source Stock Sentiment Analysis Bot!")
    print("📊 Aggregating news from trusted Indian financial RSS feeds")
    print("💡 You can enter company names or stock symbols!")
    print("📝 Examples: 'Apple', 'AAPL', 'Reliance Industries', 'RELIANCE.NS'")
    print("=" * 70)
    
    try:
        # Initialize the bot
        bot = MultiSourceStockSentimentBot()
        
        # Get company name or stock symbol from user
        user_input = input("\nEnter company name or stock symbol: ").strip()
        
        if not user_input:
            print("❌ Please provide a valid company name or stock symbol.")
            return
        
        # Show suggestions if input seems partial and might need clarification
        if len(user_input) >= 3 and not re.match(r'^[A-Z]{2,6}(\.[A-Z]{1,3})?$', user_input.upper()):
            suggestions = bot.get_company_suggestions(user_input)
            if suggestions and len(suggestions) > 1:
                print(f"\n💡 Found {len(suggestions)} potential matches:")
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"{i}. {suggestion}")
                
                choice = input("\nEnter the number of your choice (or press Enter to continue with original input): ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(suggestions):
                    # Extract company name from suggestion
                    selected = suggestions[int(choice) - 1]
                    user_input = selected.split(' (')[0]  # Remove ticker from display
                    print(f"✅ Selected: {selected}")
        
        # Analyze sentiment
        result = bot.analyze_stock_sentiment(user_input)
        
        if result:
            print(f"\n✅ Multi-source analysis complete for {result['company_input']} ({result['stock_symbol']})")
            print(f"📊 Data from {result['sources_used']} different news sources")
            print("⚠️  Disclaimer: This is for educational purposes only. Not financial advice.")
        
    except KeyboardInterrupt:
        print("\n\n👋 Analysis interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check your API keys and try again.")

if __name__ == "__main__":
    main()
