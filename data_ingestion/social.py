import re
import praw
from textblob import TextBlob
import pandas as pd
from datetime import datetime, timedelta
import logging
import time
from typing import List, Dict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Load HuggingFace Sentiment Model once (global)
sentiment_pipeline = pipeline("sentiment-analysis")

class RedditSentimentAnalyzer:
    def __init__(self):
        """Initialize Reddit API client and sentiment analyzer"""
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent='Hermes Market Analysis Bot v1.0'
        )
        self.subreddits = ['wallstreetbets', 'stocks', 'investing']
        self.rate_limit_delay = 2  # seconds between API calls

    def fetch_reddit_posts(self, subreddit: str, limit: int = 100, time_filter: str = 'day') -> List[Dict]:
        """
        Fetch posts from a specific subreddit
        
        Args:
            subreddit: Name of the subreddit
            limit: Maximum number of posts to fetch
            time_filter: Time period to fetch posts from ('hour', 'day', 'week', 'month', 'year', 'all')
            
        Returns:
            List of dictionaries containing post data
        """
        try:
            posts = []
            sub = self.reddit.subreddit(subreddit)
            
            for post in sub.top(time_filter=time_filter, limit=limit):
                post_data = {
                    'id': post.id,
                    'title': post.title,
                    'selftext': post.selftext,
                    'score': post.score,
                    'num_comments': post.num_comments,
                    'created_utc': datetime.fromtimestamp(post.created_utc),
                    'subreddit': subreddit,
                    'url': post.url
                }
                posts.append(post_data)
                time.sleep(self.rate_limit_delay)  # Respect rate limits
                
            logger.info(f"Fetched {len(posts)} posts from r/{subreddit}")
            return posts
            
        except Exception as e:
            logger.error(f"Error fetching posts from r/{subreddit}: {str(e)}")
            return []

    def clean_reddit_text(self, text: str) -> str:
        """
        Clean and preprocess Reddit text for sentiment analysis
        
        Args:
            text: Raw text from Reddit post
            
        Returns:
            Cleaned text
        """
        # Remove URLs
        text = ' '.join(word for word in text.split() if not word.startswith('http'))
        
        # Remove special characters and extra whitespace
        text = ' '.join(text.split())
        
        return text

    def extract_stock_mentions(self, text: str, watchlist: List[str]) -> List[str]:
        """
        Extract stock tickers mentioned in text
        
        Args:
            text: Text to analyze
            watchlist: List of stock tickers to look for
            
        Returns:
            List of mentioned tickers
        """
        mentioned_tickers = []
        text = text.upper()
        
        for ticker in watchlist:
            if ticker in text:
                mentioned_tickers.append(ticker)
                
        return mentioned_tickers

    def analyze_sentiment(self, text: str) -> str:
        """
        Analyze sentiment of text using TextBlob
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment classification ('POSITIVE', 'NEGATIVE', or 'NEUTRAL')
        """
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity
        
        if polarity > 0.1:
            return 'POSITIVE'
        elif polarity < -0.1:
            return 'NEGATIVE'
        else:
            return 'NEUTRAL'

    def get_sentiment_summary(self, watchlist: List[str], time_filter: str = 'day') -> pd.DataFrame:
        """
        Get sentiment summary for all stocks in watchlist
        
        Args:
            watchlist: List of stock tickers to analyze
            time_filter: Time period to analyze ('hour', 'day', 'week', 'month', 'year', 'all')
            
        Returns:
            DataFrame with sentiment summary
        """
        all_results = []
        
        for subreddit in self.subreddits:
            posts = self.fetch_reddit_posts(subreddit, limit=100, time_filter=time_filter)
            
            for post in posts:
                clean_text = self.clean_reddit_text(post['title'] + " " + post['selftext'])
                mentions = self.extract_stock_mentions(clean_text, watchlist)
                
                for ticker in mentions:
                    sentiment = self.analyze_sentiment(clean_text)
                    result = {
                        'ticker': ticker,
                        'sentiment': sentiment,
                        'subreddit': subreddit,
                        'post_score': post['score'],
                        'num_comments': post['num_comments'],
                        'timestamp': post['created_utc']
                    }
                    all_results.append(result)
                    
        df = pd.DataFrame(all_results)
        
        if not df.empty:
            # Calculate sentiment score (positive - negative mentions)
            sentiment_counts = df.groupby(['ticker', 'sentiment']).size().unstack(fill_value=0)
            sentiment_counts['sentiment_score'] = sentiment_counts.get('POSITIVE', 0) - sentiment_counts.get('NEGATIVE', 0)
            
            # Add engagement metrics
            engagement = df.groupby('ticker').agg({
                'post_score': 'sum',
                'num_comments': 'sum'
            })
            
            result = pd.concat([sentiment_counts, engagement], axis=1)
            result = result.fillna(0)
            
            return result
        else:
            return pd.DataFrame()

def update_social_sentiment_log(watchlist: List[str]):
    """
    Update the social sentiment log with latest data
    
    Args:
        watchlist: List of stock tickers to track
    """
    analyzer = RedditSentimentAnalyzer()
    sentiment_summary = analyzer.get_sentiment_summary(watchlist)
    
    if not sentiment_summary.empty:
        # Get the correct output directory
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs')
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'social_sentiment_log.csv')
        
        # Add timestamp
        sentiment_summary['timestamp'] = datetime.now()
        
        try:
            # Try to read existing log
            existing_df = pd.read_csv(output_file)
            combined = pd.concat([existing_df, sentiment_summary], ignore_index=True)
        except FileNotFoundError:
            combined = sentiment_summary
            
        combined.to_csv(output_file, index=False)
        logger.info(f"Social sentiment log updated at {output_file}")
    else:
        logger.warning("No sentiment data to log")
