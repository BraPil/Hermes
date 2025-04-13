from logger import get_logger
import yfinance as yf
import pandas as pd
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import logging

#logger = get_logger(__name__)
logger = logging.getLogger(__name__)

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
    Scrapes CNN Fear & Greed Index from their website using Selenium.

    Returns:
        dict: Dictionary with date and fear_greed_score
    """
    url = "https://edition.cnn.com/markets/fear-and-greed"

    # Set up Selenium WebDriver
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        # Locate the Fear & Greed score using the updated class
        fg_score_tag = driver.find_element(By.CLASS_NAME, 'market-fng-gauge__dial-number-value')
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

    except Exception as e:
        logger.error(f"An error occurred while fetching Fear & Greed Index: {e}")
        return None

    finally:
        driver.quit()

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
