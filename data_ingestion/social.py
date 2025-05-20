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
from transformers import pipeline

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Initialize sentiment pipeline
try:
    sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
except Exception as e:
    logger.error(f"Failed to initialize sentiment pipeline: {str(e)}")
    sentiment_pipeline = None

class RedditSentimentAnalyzer:
    def __init__(self):
        """Initialize Reddit API client and sentiment analyzer"""
        try:
            self.reddit = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                user_agent=os.getenv('REDDIT_USER_AGENT')
            )
            if not all([os.getenv('REDDIT_CLIENT_ID'), os.getenv('REDDIT_CLIENT_SECRET'), os.getenv('REDDIT_USER_AGENT')]):
                raise ValueError("Missing required Reddit API credentials in environment variables")
        except Exception as e:
            logger.error(f"Failed to initialize Reddit client: {str(e)}")
            raise
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
            logger.info(f"Fetching posts from r/{subreddit} with time_filter={time_filter}")
            sub = self.reddit.subreddit(subreddit)
            
            for post in sub.top(time_filter=time_filter, limit=limit):
                logger.debug(f"Processing post: {post.id} - {post.title[:50]}...")
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
                logger.debug(f"Sleeping for {self.rate_limit_delay} seconds to respect rate limits")
                time.sleep(self.rate_limit_delay)  # Respect rate limits
                
            logger.info(f"Successfully fetched {len(posts)} posts from r/{subreddit}")
            return posts
            
        except Exception as e:
            logger.error(f"Error fetching posts from r/{subreddit}: {str(e)}", exc_info=True)
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
        Extract stock tickers mentioned in text, including common variations

        Args:
            text: Text to analyze
            watchlist: List of stock tickers to look for

        Returns:
            List of mentioned tickers
        """
        mentioned_tickers = []
        text = text.upper()
        
        # Common variations of ticker mentions
        variations = {
            'AAPL': ['AAPL', 'APPLE', '$AAPL', 'APPLE INC', 'APPLE STOCK'],
            'MSFT': ['MSFT', 'MICROSOFT', '$MSFT', 'MICROSOFT CORP', 'MICROSOFT STOCK'],
            'AMZN': ['AMZN', 'AMAZON', '$AMZN', 'AMAZON.COM', 'AMAZON STOCK'],
            'NVDA': ['NVDA', 'NVIDIA', '$NVDA', 'NVIDIA CORP', 'NVIDIA STOCK'],
            'TSLA': ['TSLA', 'TESLA', '$TSLA', 'TESLA MOTORS', 'TESLA STOCK']
        }

        for ticker in watchlist:
            # Check for ticker and its variations
            if any(var in text for var in variations.get(ticker, [ticker])):
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

    def fetch_comments(self, post_id: str) -> List[Dict]:
        """
        Fetch all comments for a specific post, including replies

        Args:
            post_id: ID of the post to fetch comments for

        Returns:
            List of dictionaries containing comment data
        """
        try:
            post = self.reddit.submission(id=post_id)
            post.comments.replace_more(limit=None)  # Fetch all comments, including replies
            comments = []
            
            def process_comment(comment):
                comment_data = {
                    'id': comment.id,
                    'body': comment.body,
                    'score': comment.score,
                    'created_utc': datetime.fromtimestamp(comment.created_utc)
                }
                comments.append(comment_data)
                # Process replies recursively
                for reply in comment.replies:
                    process_comment(reply)
            
            # Process all top-level comments and their replies
            for comment in post.comments:
                process_comment(comment)
                
            logger.info(f"Fetched {len(comments)} total comments for post {post_id}")
            return comments
            
        except Exception as e:
            logger.error(f"Error fetching comments for post {post_id}: {str(e)}", exc_info=True)
            return []

    def get_sentiment_summary(self, watchlist: List[str], time_filter: str = 'day', return_post_level: bool = False) -> pd.DataFrame:
        """
        Get sentiment summary for all stocks in watchlist

        Args:
            watchlist: List of stock tickers to analyze
            time_filter: Time period to analyze ('hour', 'day', 'week', 'month', 'year', 'all')
            return_post_level: If True, return post-level DataFrame (for comment sentiment aggregation)

        Returns:
            DataFrame with sentiment summary
        """
        logger.info(f"Getting sentiment summary for {len(watchlist)} tickers")
        all_results = []

        for subreddit in self.subreddits:
            logger.info(f"Processing subreddit: r/{subreddit}")
            posts = self.fetch_reddit_posts(subreddit, limit=100, time_filter=time_filter)

            for post in posts:
                logger.debug(f"Analyzing post {post['id']} for stock mentions")
                clean_text = self.clean_reddit_text(post['title'] + " " + post['selftext'])
                mentions = self.extract_stock_mentions(clean_text, watchlist)

                for ticker in mentions:
                    logger.debug(f"Found mention of {ticker} in post {post['id']}")
                    sentiment = self.analyze_sentiment(clean_text)
                    result = {
                        'ticker': ticker,
                        'sentiment': sentiment,
                        'subreddit': subreddit,
                        'post_score': post['score'],
                        'num_comments': post['num_comments'],
                        'post_id': post['id'],
                        'timestamp': post['created_utc'],
                        'text': clean_text
                    }
                    all_results.append(result)

        df = pd.DataFrame(all_results)
        logger.info(f"Found {len(df)} total mentions across all subreddits")

        if return_post_level:
            return df  # Return all post-level details for further aggregation

        if not df.empty:
            # Initialize result DataFrame with tickers
            result = pd.DataFrame({'ticker': watchlist})

            # Calculate sentiment counts
            sentiment_counts = df.groupby(['ticker', 'sentiment']).size().unstack(fill_value=0)
            logger.info("Calculated sentiment counts")

            # Merge sentiment counts with result
            result = result.merge(sentiment_counts, how='left', left_on='ticker', right_index=True)

            # Fill NaN values with 0
            result = result.fillna(0)

            # Ensure all sentiment columns exist
            for sentiment in ['POSITIVE', 'NEGATIVE', 'NEUTRAL']:
                if sentiment not in result.columns:
                    result[sentiment] = 0

            # Calculate sentiment score
            result['sentiment_score'] = result['POSITIVE'] - result['NEGATIVE']

            # Calculate engagement metrics
            engagement = df.groupby('ticker').agg({
                'post_score': 'sum',
                'num_comments': 'sum',
                'post_id': 'nunique'
            }).reset_index()

            # Rename post_id to num_posts for clarity
            engagement = engagement.rename(columns={'post_id': 'num_posts'})

            # Merge engagement metrics
            result = result.merge(engagement, how='left', on='ticker')

            # Fill NaN values with 0
            result = result.fillna(0)

            # Find the most upvoted comment for each ticker
            logger.info("Finding top comments for each ticker")
            top_comments = df.groupby('ticker').apply(lambda x: x.loc[x['post_score'].idxmax(), 'text'] if not x.empty else '').reset_index(name='top_comment')
            result = result.merge(top_comments, how='left', on='ticker')

            # Reorder columns
            columns = ['ticker', 'POSITIVE', 'NEGATIVE', 'NEUTRAL', 'sentiment_score', 'num_posts', 'post_score', 'num_comments', 'top_comment']
            result = result[columns]

            logger.info("Successfully generated sentiment summary")
            return result
        else:
            logger.warning("No results found, returning empty DataFrame")
            # Return empty DataFrame with correct columns
            return pd.DataFrame(columns=['ticker', 'POSITIVE', 'NEGATIVE', 'NEUTRAL', 'sentiment_score', 'num_posts', 'post_score', 'num_comments', 'top_comment'])

    def get_comment_sentiment_summary(self, post_id: str) -> Dict:
        """
        Get sentiment summary for comments of a specific post

        Args:
            post_id: ID of the post to analyze comments for

        Returns:
            Dictionary with sentiment summary for comments
        """
        comments = self.fetch_comments(post_id)
        if not comments:
            return {'POSITIVE': 0, 'NEGATIVE': 0, 'NEUTRAL': 0, 'sentiment_score': 0}

        sentiment_counts = {'POSITIVE': 0, 'NEGATIVE': 0, 'NEUTRAL': 0}
        for comment in comments:
            sentiment = self.analyze_sentiment(comment['body'])
            sentiment_counts[sentiment] += 1

        sentiment_score = sentiment_counts['POSITIVE'] - sentiment_counts['NEGATIVE']
        return {**sentiment_counts, 'sentiment_score': sentiment_score}

    def get_sentiment_summary_with_comments(self, watchlist: List[str], time_filter: str = 'day') -> pd.DataFrame:
        """
        Get sentiment summary for all stocks in watchlist, including comment sentiment

        Args:
            watchlist: List of stock tickers to analyze
            time_filter: Time period to analyze ('hour', 'day', 'week', 'month', 'year', 'all')

        Returns:
            DataFrame with sentiment summary including comment sentiment
        """
        post_df = self.get_sentiment_summary(watchlist, time_filter, return_post_level=True)
        if post_df.empty:
            return post_df

        # Add comment sentiment summary for each post
        logger.info("Analyzing comments for each post...")
        comment_sentiments = []
        
        for idx, row in post_df.iterrows():
            post_id = row['post_id']
            ticker = row['ticker']
            logger.debug(f"Processing comments for post {post_id}")
            comments = self.fetch_comments(post_id)
            
            if comments:
                # Analyze sentiment for each comment
                for comment in comments:
                    sentiment = self.analyze_sentiment(comment['body'])
                    comment_sentiments.append({
                        'ticker': ticker,
                        'post_id': post_id,
                        'sentiment': sentiment,
                        'score': comment['score']
                    })
                logger.info(f"Analyzed {len(comments)} comments for post {post_id}")
        
        # Convert comment sentiments to DataFrame
        if comment_sentiments:
            comment_df = pd.DataFrame(comment_sentiments)
            logger.info(f"Total comments analyzed: {len(comment_df)}")
            
            # Group by ticker and sentiment to get counts
            comment_counts = comment_df.groupby(['ticker', 'sentiment']).size().unstack(fill_value=0)
            
            # Calculate comment sentiment scores
            comment_counts['comment_sentiment_score'] = comment_counts.get('POSITIVE', 0) - comment_counts.get('NEGATIVE', 0)
        else:
            # If no comments, create empty DataFrame with expected columns
            comment_counts = pd.DataFrame(0, index=watchlist, columns=['POSITIVE', 'NEGATIVE', 'NEUTRAL', 'comment_sentiment_score'])

        # Now aggregate post-level sentiment up to ticker level
        post_sentiment_counts = post_df.groupby(['ticker', 'sentiment']).size().unstack(fill_value=0)
        post_sentiment_counts['sentiment_score'] = post_sentiment_counts.get('POSITIVE', 0) - post_sentiment_counts.get('NEGATIVE', 0)

        # Engagement metrics
        engagement = post_df.groupby('ticker').agg({
            'post_score': 'sum',
            'num_comments': 'sum',
            'post_id': 'nunique'
        }).reset_index().rename(columns={'post_id': 'num_posts'})

        # Top comment per ticker
        top_comments = post_df.groupby('ticker').apply(lambda x: x.loc[x['post_score'].idxmax(), 'text'] if not x.empty else '').reset_index(name='top_comment')

        # Merge all results
        result = pd.DataFrame({'ticker': watchlist})
        result = result.merge(post_sentiment_counts, how='left', left_on='ticker', right_index=True)
        result = result.merge(comment_counts, how='left', left_on='ticker', right_index=True, suffixes=('_post', '_comment'))
        result = result.merge(engagement, how='left', on='ticker')
        result = result.merge(top_comments, how='left', on='ticker')
        result = result.fillna(0)

        # Calculate total sentiment score
        result['total_sentiment_score'] = result['sentiment_score'] + result['comment_sentiment_score']

        # Reorder columns
        columns = [
            'ticker', 'POSITIVE', 'NEGATIVE', 'NEUTRAL',
            'sentiment_score', 'comment_sentiment_score', 'total_sentiment_score',
            'num_posts', 'post_score', 'num_comments', 'top_comment'
        ]
        result = result[columns]
        return result

def update_social_sentiment_log(watchlist: List[str]):
    """
    Update the social sentiment log with latest data
    
    Args:
        watchlist: List of stock tickers to track
    """
    analyzer = RedditSentimentAnalyzer()
    sentiment_summary = analyzer.get_sentiment_summary_with_comments(watchlist)
    
    if not sentiment_summary.empty:
        # Get the correct output directory
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs')
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'social_sentiment_log.csv')
        
        # Add timestamp with the new format
        sentiment_summary['timestamp'] = datetime.now().strftime('%m/%d/%Y %I:%M:%S %p')
        
        # Ensure columns are in the correct order
        columns = [
            'ticker', 'POSITIVE', 'NEGATIVE', 'NEUTRAL',
            'sentiment_score', 'comment_sentiment_score', 'total_sentiment_score',
            'num_posts', 'post_score', 'num_comments', 'top_comment', 'timestamp'
        ]
        sentiment_summary = sentiment_summary[columns]
        
        try:
            # Try to read existing log
            if os.path.exists(output_file):
                existing_df = pd.read_csv(output_file)
                combined = pd.concat([existing_df, sentiment_summary], ignore_index=True)
            else:
                combined = sentiment_summary
                
            # Save the combined data
            combined.to_csv(output_file, index=False)
            logger.info(f"Social sentiment log updated at {output_file}")
            
        except Exception as e:
            logger.error(f"Error updating social sentiment log: {str(e)}")
            # Try to save just the new data if there was an error
            try:
                sentiment_summary.to_csv(output_file, index=False)
                logger.info(f"Saved new social sentiment data to {output_file}")
            except Exception as e2:
                logger.error(f"Failed to save new social sentiment data: {str(e2)}")
    else:
        logger.warning("No sentiment data to log")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example watchlist
    watchlist = ['AAPL', 'MSFT', 'AMZN', 'NVDA', 'TSLA']
    
    try:
        update_social_sentiment_log(watchlist)
        logger.info("Social sentiment analysis completed successfully")
    except Exception as e:
        logger.error(f"Error during social sentiment analysis: {str(e)}", exc_info=True)
