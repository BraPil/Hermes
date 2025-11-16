from data_ingestion.fundamentals import fetch_stock_data
from data_ingestion.psycho import fetch_vix_and_sp500_data
from data_ingestion.psycho import update_fear_greed_log
from data_ingestion.social import RedditSentimentAnalyzer, update_social_sentiment_log
from analytics.scoring import calculate_score
from outputs.report_generator import generate_report
import pandas as pd
import os

# Ensure outputs directory exists
outputs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outputs')
os.makedirs(outputs_dir, exist_ok=True)

# Custom watchlist: Quantum, inverse ETFs, tech, and BTC
watchlist = [
    'SQQQ',    # Inverse Nasdaq-100
    'UVXY',    # Inverse VIX (volatility play)
    'SPXU',    # Inverse S&P 500
    'RNA',     # Moderna (biotech)
    'DYN',     # Dynamics
    'MSFT',    # Microsoft (tech)
    'GOOGL',   # Google (tech)
    'INTC',    # Intel (semiconductor)
    'AMD',     # AMD (semiconductor)
    'GLD',     # Gold ETF (commodity)
    'RGTI',    # Rigetti Computing (quantum)
    'QBTS',    # D-Wave Systems (quantum)
    'IONQ',    # IonQ (quantum)
    'QUBT',    # Quantum Computing (quantum)
    'QMCO',    # Quantum Computing (quantum)
    'BTC-USD'  # Bitcoin (cryptocurrency)
]

tickers = [
    'SQQQ', 'UVXY', 'SPXU', 'RNA', 'DYN',
    'MSFT', 'GOOGL', 'INTC', 'AMD', 'GLD',
    'RGTI', 'QBTS', 'IONQ', 'QUBT', 'QMCO',
    'BTC-USD'
]

# Fundamentals
df = fetch_stock_data(tickers)
df['score'] = df.apply(calculate_score, axis=1)
df.to_csv(os.path.join(outputs_dir, 'fundamentals_scored.csv'), index=False)

print("Scored data saved to outputs/fundamentals_scored.csv")

# Psycho
df_psycho = fetch_vix_and_sp500_data(period='6mo')
df_psycho.to_csv(os.path.join(outputs_dir, 'vix_sp500_data.csv'))

print(df_psycho.tail())
print("Pysch data saved to outputs/vix_sp500_data.csv")

# Fear and Greed Index
update_fear_greed_log()

# Social
analyzer = RedditSentimentAnalyzer()
update_social_sentiment_log(watchlist)

# Report
generate_report(df)

# Git LFS
os.system('git lfs install')
os.system('git lfs pull')
os.system('git fetch origin')
os.system('git merge origin/main --allow-unrelated-histories')
os.system('git push --force-with-lease origin main')

