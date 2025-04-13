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
    options.add_argument("--headless")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(url)
        logger.info("Page loaded, waiting for content...")
        
        # Wait for the page to load completely
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        # First wait for any element with 'market' in the class name to appear
        wait = WebDriverWait(driver, 20)  # Wait up to 20 seconds
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'market')]")))
        
        # Log the page source for debugging
        logger.info("Page source length: " + str(len(driver.page_source)))
        
        # Try multiple possible selectors for the score
        selectors = [
            "//div[contains(@class, 'market-fng-gauge__dial-number-value')]",
            "//div[contains(@class, 'fear-greed-score')]",
            "//div[contains(@class, 'market-fng-gauge__score')]",
            "//div[contains(@class, 'fear-greed-index')]",
            "//div[contains(@class, 'market-fng')]//span",
            "//div[contains(@class, 'market-fng')]//div"
        ]
        
        score_element = None
        for selector in selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    logger.info(f"Found elements with selector {selector}: {len(elements)}")
                    for element in elements:
                        logger.info(f"Element text: {element.text}")
                        if any(c.isdigit() for c in element.text):
                            score_element = element
                            break
                    if score_element:
                        break
            except Exception as e:
                logger.warning(f"Error with selector {selector}: {str(e)}")
                continue
        
        if not score_element:
            # Try to find any number on the page that might be the score
            all_elements = driver.find_elements(By.XPATH, "//*[text()[contains(., '0') or contains(., '1') or contains(., '2') or contains(., '3') or contains(., '4') or contains(., '5') or contains(., '6') or contains(., '7') or contains(., '8') or contains(., '9')]]")
            for element in all_elements:
                text = element.text.strip()
                if text.isdigit() and 0 <= int(text) <= 100:
                    score_element = element
                    break
        
        if not score_element:
            logger.error("Could not find Fear & Greed score element on the page")
            return None
            
        # Get the text and clean it
        score_text = score_element.text.strip()
        logger.info(f"Raw score text: {score_text}")
        
        # Extract numbers from the text
        import re
        numbers = re.findall(r'\d+', score_text)
        if not numbers:
            logger.error(f"Could not extract number from score text: {score_text}")
            return None
            
        try:
            score = int(numbers[0])
            if not (0 <= score <= 100):
                logger.error(f"Score {score} is not within valid range (0-100)")
                return None
                
            logger.info(f"Extracted Fear & Greed score: {score}")
            
            return {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'fear_greed_score': score
            }
            
        except ValueError:
            logger.error(f"Could not convert extracted number to int: {numbers[0]}")
            return None
            
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
