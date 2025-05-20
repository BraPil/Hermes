from social import RedditSentimentAnalyzer
import pandas as pd
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def test_reddit_connection():
    try:
        logger.info("Testing Reddit API connection...")
        analyzer = RedditSentimentAnalyzer()
        analyzer.rate_limit_delay = 1  # Reduce delay for testing
        # Try to fetch a single post from wallstreetbets
        logger.info("Attempting to fetch a single post from r/wallstreetbets...")
        posts = analyzer.fetch_reddit_posts('wallstreetbets', limit=1)
        
        if posts:
            logger.info("Successfully connected to Reddit API!")
            logger.info(f"First post title: {posts[0]['title']}")
            return True
        else:
            logger.error("Failed to fetch any posts from Reddit")
            return False
            
    except Exception as e:
        logger.error(f"Error connecting to Reddit API: {str(e)}", exc_info=True)
        return False

def test_sentiment_summary():
    try:
        # First test the connection
        if not test_reddit_connection():
            logger.error("Skipping sentiment analysis due to connection failure")
            return
            
        # Initialize the analyzer
        logger.info("Initializing RedditSentimentAnalyzer...")
        analyzer = RedditSentimentAnalyzer()
        analyzer.rate_limit_delay = 1  # Reduce delay for testing
        
        # Test with a small watchlist of popular stocks
        test_watchlist = ['AAPL', 'TSLA', 'NVDA']
        logger.info(f"Testing with watchlist: {test_watchlist}")
        
        # Get sentiment summary with a lower post limit for testing
        logger.info("Fetching sentiment summary...")
        # Patch fetch_reddit_posts to use limit=10
        original_fetch = analyzer.fetch_reddit_posts
        def fetch_with_limit(subreddit, limit=100, time_filter='day'):
            return original_fetch(subreddit, limit=10, time_filter=time_filter)
        analyzer.fetch_reddit_posts = fetch_with_limit
        sentiment_summary = analyzer.get_sentiment_summary_with_comments(test_watchlist, time_filter='day')
        
        # Display results
        logger.info("\nFull Sentiment Summary:")
        print("=" * 80)
        
        # Set display options to show full text
        pd.set_option('display.max_colwidth', None)
        pd.set_option('display.width', 120)
        
        # Show all sentiment columns
        sentiment_columns = [
            'ticker', 
            'post_POSITIVE', 'post_NEGATIVE', 'post_NEUTRAL',
            'comment_POSITIVE', 'comment_NEGATIVE', 'comment_NEUTRAL',
            'sentiment_score', 'comment_sentiment_score', 'total_sentiment_score',
            'num_posts', 'num_comments'
        ]
        print(sentiment_summary[sentiment_columns])
        
        # Show top comments
        logger.info("\nTop Comments:")
        print("=" * 80)
        print(sentiment_summary[['ticker', 'top_comment']])
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    test_sentiment_summary() 