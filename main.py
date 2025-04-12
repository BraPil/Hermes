from data_ingestion.fundamentals import fetch_stock_data
from analytics.scoring import calculate_score
from outputs.report_generator import generate_report
import pandas as pd

tickers = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN']

df = fetch_stock_data(tickers)

df['score'] = df.apply(calculate_score, axis=1)

df.to_csv('C:/Hermes/Hermes/outputs/fundamentals_scored.csv', index=False)

print("Scored data saved to outputs/fundamentals_scored.csv")

generate_report(df)