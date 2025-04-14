from data_ingestion.fundamentals import fetch_stock_data
from data_ingestion.psycho import fetch_vix_and_sp500_data
from data_ingestion.psycho import update_fear_greed_log
from analytics.scoring import calculate_score
from outputs.report_generator import generate_report
import pandas as pd

# Social
from data_ingestion.social import fetch_reddit_posts, clean_reddit_text, extract_stock_mentions, analyze_sentiment
import pandas as pd

watchlist = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN']

tickers = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN']

# Fundamentals
df = fetch_stock_data(tickers)
df['score'] = df.apply(calculate_score, axis=1)
df.to_csv('C:/Hermes/Hermes/outputs/fundamentals_scored.csv', index=False)

print("Scored data saved to outputs/fundamentals_scored.csv")

# Psycho
df_psycho = fetch_vix_and_sp500_data(period='6mo')
df_psycho.to_csv('C:/Hermes/Hermes/outputs/vix_sp500_data.csv')

print(df_psycho.tail())
print("Pysch data saved to outputs/vix_sp500_data.csv")

# Fear and Greed Index
update_fear_greed_log()

# Report
generate_report(df)

# Social
# # Fetch Reddit posts
df_reddit = fetch_reddit_posts('stocks', limit=100)

results = []

for _, row in df_reddit.iterrows():
    clean_text = clean_reddit_text(row['title'] + " " + row['selftext'])
    mentions = extract_stock_mentions(clean_text, watchlist)

    for ticker in mentions:
        sentiment = analyze_sentiment(clean_text)
        results.append({'ticker': ticker, 'sentiment': sentiment})

df_sentiment = pd.DataFrame(results)

print(df_sentiment.head())

sentiment_summary = df_sentiment.groupby(['ticker', 'sentiment']).size().unstack(fill_value=0)

sentiment_summary['sentiment_score'] = sentiment_summary.get('POSITIVE', 0) - sentiment_summary.get('NEGATIVE', 0)

print(sentiment_summary.sort_values(by='sentiment_score', ascending=False))

sentiment_summary.to_csv('C:/Hermes/Hermes/outputs/social_sentiment_scores.csv')

