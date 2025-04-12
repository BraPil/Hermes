# Import required libraries
from logger import get_logger
import yfinance as yf
import pandas as pd

logger = get_logger(__name__)

def fetch_stock_data(tickers):
    """
    Fetch financial data for a list of stock tickers using Yahoo Finance.
    """

    data_list = []

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # Check if info dict is empty
            if not info:
                logger.warning(f"No data found for ticker: {ticker}")
                continue

            fundamentals = {
                'ticker': ticker,
                'longName': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'marketCap': info.get('marketCap', None),
                'trailingPE': info.get('trailingPE', None),
                'forwardPE': info.get('forwardPE', None),
                'pegRatio': info.get('pegRatio', None),
                'priceToBook': info.get('priceToBook', None),
                'debtToEquity': info.get('debtToEquity', None),
                'returnOnEquity': info.get('returnOnEquity', None)
            }

            data_list.append(fundamentals)

            logger.info(f"Fetched data for {ticker}")

        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")

    df = pd.DataFrame(data_list)
    return df