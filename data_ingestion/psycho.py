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
import json
import os
import time

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
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        # Wait for the element to load
        time.sleep(5)
        fg_score_tag = driver.find_element(By.CLASS_NAME, 'market-fng-gauge__dial-number-value')
        score_text = fg_score_tag.text.strip()
        try:
            score = int(score_text)
        except ValueError:
            logger.error(f"Could not convert Fear & Greed score to int: {score_text}")
            return None
        logger.info(f"Fetched Fear & Greed Index Score: {score}")
        return {
            'date': datetime.now().strftime('%m/%d/%Y %I:%M:%S %p'),
            'fear_greed_score': score
        }
    except Exception as e:
        logger.error(f"An error occurred while fetching Fear & Greed Index: {e}")
        return None
    finally:
        if 'driver' in locals():
            driver.quit()

### Append Scrape Results to a .csv ###

def update_fear_greed_log():
    """
    Fetch Fear & Greed Index and append to CSV log.
    """
    # Ensure outputs directory exists
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'fear_greed_log.csv')

    data = fetch_fear_greed_index()

    if not data:
        logger.warning("No data fetched for Fear & Greed — Skipping log update.")
        return

    df_new = pd.DataFrame([data])

    try:
        if os.path.exists(output_file):
            existing_df = pd.read_csv(output_file)
            combined = pd.concat([existing_df, df_new], ignore_index=True)
        else:
            combined = df_new

        combined.to_csv(output_file, index=False)
        logger.info(f"Fear & Greed log updated successfully at {output_file}")

    except Exception as e:
        logger.error(f"Error updating Fear & Greed log: {str(e)}")
        # Try to save just the new data if there was an error
        try:
            df_new.to_csv(output_file, index=False)
            logger.info(f"Saved new Fear & Greed data to {output_file}")
        except Exception as e2:
            logger.error(f"Failed to save new Fear & Greed data: {str(e2)}")
