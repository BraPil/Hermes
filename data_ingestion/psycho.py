from logger import get_logger
import yfinance as yf
import pandas as pd

import requests
from bs4 import BeautifulSoup
from datetime import datetime

logger = get_logger(__name__)

def fetch_vix_and_sp500_data(period='1y', interval='1d'):
    """
    Fetch VIX and S&P 500 historical data.

    Args:
        period (str): Data range (e.g., '1y' = 1 year).
        interval (str): Data frequency ('1d' = daily).

    Returns:
        pd.DataFrame: Combined DataFrame with VIX and SP500 data.
    """

    vix = yf.download('^VIX', period=period, interval=interval)
    sp500 = yf.download('^GSPC', period=period, interval=interval)

    vix = vix[['Close']].rename(columns={'Close': 'VIX_Close'})
    sp500 = sp500[['Close']].rename(columns={'Close': 'SP500_Close'})

    combined = pd.concat([vix, sp500], axis=1)

    logger.info(f"Fetched VIX and SP500 data for {period}")

    return combined

### Create data_ingestion/psycho.py Scraper Function ###

def fetch_fear_greed_index():
    """
    Scrapes CNN Fear & Greed Index from their website.

    Returns:
        dict: Dictionary with date and fear_greed_score
    """

    url = "https://edition.cnn.com/markets/fear-and-greed"

    response = requests.get(url)

    if response.status_code != 200:
        logger.error(f"Failed to fetch Fear & Greed Index — Status Code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    # CNN has the score inside a <div> tag with data-testid="FearGreedMeter"
    fg_score_tag = soup.find('div', {'data-testid': 'FearGreedMeter'})

    if not fg_score_tag:
        logger.error("Fear & Greed score tag not found!")
        return None

    score_text = fg_score_tag.text.strip()

    try:
        score = int(score_text)
    except ValueError:
        logger.error(f"Could not convert Fear & Greed score to int: {score_text}")
        return None

    logger.info(f"Fetched Fear & Greed Index Score: {score}")

    return {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'fear_greed_score': score
    }

### Append Scrape Results to a .csv ###

def update_fear_greed_log():
    """
    Fetch Fear & Greed Index and append to CSV log.
    """

    data = fetch_fear_greed_index()

    if not data:
        logger.warning("No data fetched for Fear & Greed — Skipping log update.")
        return

    df_new = pd.DataFrame([data])

    try:
        existing_df = pd.read_csv('outputs/fear_greed_log.csv')
        combined = pd.concat([existing_df, df_new], ignore_index=True)
    except FileNotFoundError:
        combined = df_new

    combined.to_csv('outputs/fear_greed_log.csv', index=False)

    logger.info("Fear & Greed log updated successfully.")
