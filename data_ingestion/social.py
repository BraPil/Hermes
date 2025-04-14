import re

from transformers import pipeline

# Load HuggingFace Sentiment Model once (global)
sentiment_pipeline = pipeline("sentiment-analysis")

def clean_reddit_text(text):
    """
    Clean Reddit post text for sentiment analysis.

    Args:
        text (str): Raw Reddit post text.

    Returns:
        str: Cleaned text.
    """

    # Lowercase everything
    text = text.lower()

    # Remove URLs
    text = re.sub(r'http\S+|www.\S+', '', text)

    # Remove special characters
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)

    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text

def extract_stock_mentions(text, watchlist):
    """
    Find tickers from the watchlist mentioned in a Reddit post.

    Args:
        text (str): Reddit post text.
        watchlist (list): List of stock tickers to look for.

    Returns:
        list: List of mentioned tickers.
    """

    mentions = []

    for ticker in watchlist:
        pattern = r'\b' + re.escape(ticker.lower()) + r'\b'

        if re.search(pattern, text.lower()):
            mentions.append(ticker)

    return mentions

def analyze_sentiment(text):
    """
    Run sentiment analysis on text.

    Returns:
        str: 'POSITIVE' or 'NEGATIVE'
    """

    result = sentiment_pipeline(text[:512])[0]  # Truncate for model limits

    return result['label']
