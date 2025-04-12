# Import required libraries
import yfinance as yf  # For stock market data
import pandas as pd    # For tabular data storage + manipulation

def fetch_stock_data(tickers):
    """
    Fetch financial data for a list of stock tickers using Yahoo Finance.

    Args:
        tickers (list): List of stock ticker symbols as strings.

    Returns:
        pd.DataFrame: DataFrame containing key financial metrics.
    """

    # Create a list to store each stock's data
    data_list = []

    for ticker in tickers:
        stock = yf.Ticker(ticker)

        # Fetch the info dictionary
        info = stock.info

        # Extract the data we care about
        fundamentals = {
            'ticker': ticker,
            'longName': info.get('longName', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'marketCap': info.get('marketCap', None),
            'trailingPE': info.get('trailingPE', None),
            'forwardPE': info.get('forwardPE', None),
            #'pegRatio': info.get('pegRatio', None),
            'priceToBook': info.get('priceToBook', None),
            'debtToEquity': info.get('debtToEquity', None),
            'returnOnEquity': info.get('returnOnEquity', None)
        }

        # Append the stock data to the list
        data_list.append(fundamentals)

    # Convert list of dicts to Pandas DataFrame
    df = pd.DataFrame(data_list)

    return df