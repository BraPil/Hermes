from logger import get_logger
import yfinance as yf
import pandas as pd
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import logging
import time
import os

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
    logger.info("Starting Fear & Greed Index scraping...")
    
    # Set up Selenium WebDriver with more comprehensive options
    options = Options()
    options.add_argument("--headless=new")  # Use new headless mode
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--enable-javascript")
    options.add_argument("--enable-logging")
    options.add_argument("--log-level=0")
    options.add_argument("--v=99")
    options.add_argument("--enable-unsafe-swiftshader")  # Enable software rendering
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # Set longer timeouts
        driver.set_page_load_timeout(60)  # Increase to 60 seconds
        driver.implicitly_wait(20)  # Increase implicit wait
        
        # Try to load the page with retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempt {attempt + 1} of {max_retries}: Loading page...")
                driver.get(url)
                
                # Wait for the page to be in a ready state
                WebDriverWait(driver, 20).until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )
                
                logger.info("Page loaded successfully!")
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"All attempts failed. Last error: {str(e)}")
                    raise e
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                logger.info("Waiting 5 seconds before retrying...")
                time.sleep(5)  # Increase wait time between retries
        
        # Wait for the page to load completely
        logger.info("Waiting for market content to appear...")
        wait = WebDriverWait(driver, 30)  # Increase wait time
        
        # First try to find the main container
        main_container = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'market-fng')]")))
        logger.info("Main container found!")
        
        # Take a screenshot for debugging
        driver.save_screenshot("fear_greed_debug.png")
        logger.info("Screenshot saved as fear_greed_debug.png")
        
        # Try multiple possible selectors for the score
        selectors = [
            "//div[contains(@class, 'market-fng-gauge__dial-number-value')]",
            "//div[contains(@class, 'market-fng-gauge__score')]",
            "//div[contains(@class, 'market-fng-gauge')]//span[contains(@class, 'number')]",
            "//div[contains(@class, 'market-fng-gauge')]//div[contains(@class, 'value')]",
            "//div[contains(@class, 'market-fng-gauge')]//div[contains(@class, 'score')]",
            "//div[contains(@class, 'market-fng-gauge')]//div[contains(@class, 'dial')]//span"
        ]
        
        logger.info("Searching for score element...")
        score_element = None
        for selector in selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    logger.info(f"Found {len(elements)} elements with selector: {selector}")
                    for element in elements:
                        text = element.text.strip()
                        logger.info(f"Element text: '{text}'")
                        if any(c.isdigit() for c in text):
                            score_element = element
                            logger.info(f"Found potential score element with text: '{text}'")
                            break
                    if score_element:
                        break
            except Exception as e:
                logger.warning(f"Error with selector {selector}: {str(e)}")
                continue
        
        if not score_element:
            logger.info("Trying alternative method to find score...")
            # Try to find any number within the main container
            all_elements = main_container.find_elements(By.XPATH, ".//*[text()[contains(., '0') or contains(., '1') or contains(., '2') or contains(., '3') or contains(., '4') or contains(., '5') or contains(., '6') or contains(., '7') or contains(., '8') or contains(., '9')]]")
            logger.info(f"Found {len(all_elements)} elements containing numbers")
            for element in all_elements:
                text = element.text.strip()
                if text.isdigit() and 0 <= int(text) <= 100:
                    score_element = element
                    logger.info(f"Found score element with text: '{text}'")
                    break
        
        if not score_element:
            logger.error("Could not find Fear & Greed score element on the page")
            return None
            
        # Get the text and clean it
        score_text = score_element.text.strip()
        logger.info(f"Raw score text: '{score_text}'")
        
        # Extract numbers from the text
        import re
        numbers = re.findall(r'\d+', score_text)
        if not numbers:
            logger.error(f"Could not extract number from score text: '{score_text}'")
            return None
            
        try:
            score = int(numbers[0])
            if not (0 <= score <= 100):
                logger.error(f"Score {score} is not within valid range (0-100)")
                return None
                
            logger.info(f"Successfully extracted Fear & Greed score: {score}")
            
            result = {
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'fear_greed_score': score
            }
            logger.info(f"Returning result: {result}")
            return result
            
        except ValueError:
            logger.error(f"Could not convert extracted number to int: {numbers[0]}")
            return None
            
    except Exception as e:
        logger.error(f"An error occurred while fetching Fear & Greed Index: {str(e)}")
        return None
    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                logger.error(f"Error closing browser: {str(e)}")

### Append Scrape Results to a .csv ###

def update_fear_greed_log():
    """
    Fetch Fear & Greed Index and append to CSV log.
    """
    # Get the correct output directory
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'fear_greed_log.csv')

    data = fetch_fear_greed_index()

    if not data:
        logger.warning("No data fetched for Fear & Greed — Skipping log update.")
        return

    df_new = pd.DataFrame([data])

    try:
        # Try to read existing log
        if os.path.exists(output_file):
            existing_df = pd.read_csv(output_file)
            combined = pd.concat([existing_df, df_new], ignore_index=True)
        else:
            combined = df_new
            
        # Save the combined data
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

def create_browser_session():
    """Create a reusable browser session with improved configuration"""
    options = Options()
    # Add existing options...
    
    # Add new options for better stability
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-features=NetworkService")
    options.add_argument("--disable-features=NetworkServiceInProcess")
    options.add_argument("--disable-features=IsolateOrigins")
    options.add_argument("--disable-site-isolation-trials")
    
    # Add SSL-specific options
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")
    options.add_argument("--ssl-version-max=tls1.2")
    options.add_argument("--ssl-version-min=tls1.2")
    
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def exponential_backoff(max_retries=5, base_delay=1):
    """Implement exponential backoff for retries"""
    for attempt in range(max_retries):
        try:
            yield
            return
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            logger.warning(f"Attempt {attempt + 1} failed. Retrying in {delay} seconds...")
            time.sleep(delay)
