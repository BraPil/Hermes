# Quick Start Guide - Hermes Stock Analysis

## 🚀 Get Running in 5 Minutes

### Step 1: Set Up Environment
```bash
cd C:\Hermes-1

# Create outputs directory for data
mkdir outputs

# Copy historical data (if you want to start with existing data)
# xcopy C:\Hermes\outputs\*.csv outputs\ /Y
```

### Step 2: Create .env File
Create a file named `.env` in `C:\Hermes-1\`:
```
REDDIT_CLIENT_ID=your_reddit_app_id
REDDIT_CLIENT_SECRET=your_reddit_app_secret
REDDIT_USER_AGENT=YourUsername/1.0 (+http://example.com/r/investing)
```

**How to get Reddit credentials:**
1. Go to https://www.reddit.com/prefs/apps
2. Create a new application ("script")
3. Copy the client ID and secret

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt

# If any import fails, install individually:
pip install yfinance selenium webdriver-manager beautifulsoup4 tabulate
```

### Step 4: Run Analysis
```bash
python main.py
```

### Step 5: Check Results
```bash
# View generated files
dir outputs\

# Open any CSV to see data:
# - fundamentals_scored.csv
# - social_sentiment_log.csv
# - fear_greed_log.csv
# - vix_sp500_data.csv
# - weighted_score.csv
```

---

## 📊 What Each Component Does

### `fundamentals.py`
Fetches stock metrics from Yahoo Finance
```
TICKER | P/E RATIO | PRICE/BOOK | DEBT/EQUITY | ROE
AAPL   |    28.5   |     45.2   |     2.1     | 120%
```

### `psycho.py`
Scrapes market sentiment indicators
- VIX (volatility index)
- S&P 500 price
- CNN Fear & Greed Index (0-100)

### `social.py`
Analyzes Reddit sentiment from 3 major subreddits
- Count of positive/negative mentions
- Engagement metrics
- Top comments

---

## 🎯 Your Custom Watchlist

Your portfolio includes 16 assets:

**Inverse ETFs (Bearish hedges):**
- SQQQ (Inverse Nasdaq-100)
- UVXY (Inverse VIX/Volatility)
- SPXU (Inverse S&P 500)

**Technology (Growth):**
- MSFT (Microsoft)
- GOOGL (Google)
- INTC (Intel)
- AMD (AMD Semiconductors)

**Quantum Computing (Speculative):**
- RGTI (Rigetti Computing)
- QBTS (D-Wave Systems)
- IONQ (IonQ)
- QUBT (Quantum Computing Inc.)
- QMCO (Quantum Computing)

**Other:**
- RNA (Moderna - Biotech)
- DYN (Dynamics)
- GLD (Gold ETF - Commodity)
- BTC-USD (Bitcoin - Cryptocurrency)

### `scoring.py`
Calculates composite scores
```
Base Score = Sum of points from metrics

Final Score = Base Score × Fear/Greed Multiplier
```

---

## 🛠️ Troubleshooting

### Error: "ModuleNotFoundError: No module named 'outputs'"
**Fix:**
```bash
mkdir outputs
copy C:\Hermes\outputs\report_generator.py outputs\
```

### Error: "REDDIT_CLIENT_ID not found"
**Fix:** Create `.env` file with Reddit credentials (see Step 2 above)

### Error: "ChromeDriver not found"
**Fix:** 
```bash
pip install webdriver-manager
python -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"
```

### Error: "Connection timeout"
**Fix:** Check internet connection. If Reddit/Yahoo Finance is down, try again later.

### Error: "Invalid sentiment score"
**Fix:** May happen if Reddit post text is empty. This is normal and will retry next run.

---

## 📈 Understanding the Output

### fundamentals_scored.csv
Shows raw fundamental scores (0-70 max)
```
ticker,score
AAPL,65
MSFT,62
NVDA,58
```

### weighted_score.csv
Shows final scores adjusted for market psychology
```
ticker,weighted_score
AAPL,72.5      (66 base × 1.10 multiplier when bullish)
MSFT,54.0      (60 base × 0.90 multiplier when bearish)
```

### social_sentiment_log.csv
Reddit community sentiment on each stock
```
ticker,POSITIVE,NEGATIVE,NEUTRAL,sentiment_score
AAPL,45,12,23,33
MSFT,38,18,19,20
```

### fear_greed_log.csv
Historical Fear & Greed Index
```
date,fear_greed_score
11/14/2025 2:30:00 PM,65
11/13/2025 3:45:00 PM,58
```

### vix_sp500_data.csv
Market volatility and performance
```
date,VIX_Close,SP500_Close
2025-11-14,14.5,5890.23
2025-11-13,15.2,5845.67
```

---

## 🔄 Running Regularly

### Option 1: Manual (For Testing)
```bash
python main.py
```

### Option 2: Windows Task Scheduler (Automated)
1. Press `Win+R`, type `taskschd.msc`
2. Click "Create Basic Task"
3. Name: "Hermes Stock Analysis"
4. Trigger: Daily at 9:30 AM
5. Action: Run program `python.exe`
6. Arguments: `C:\Hermes-1\main.py`

### Option 3: Windows Batch File (Simple)
Create `run_analysis.bat`:
```batch
@echo off
cd C:\Hermes-1
python main.py
pause
```

Then schedule `run_analysis.bat` in Task Scheduler

---

## 💡 Tips & Tricks

### Monitor One Stock Only (Faster Testing)
Edit `main.py` line 14-16:
```python
# Single stock for testing
watchlist = ['AAPL']
tickers = ['AAPL']
```

### Skip Reddit Analysis (If No Credentials)
Comment out `main.py` lines 36-37:
```python
# analyzer = RedditSentimentAnalyzer()
# update_social_sentiment_log(watchlist)
```

### Use Cached Data Instead of Live
Replace `main.py` with:
```python
import pandas as pd

# Load last successful run
df = pd.read_csv('outputs/fundamentals_scored.csv')
print(df.sort_values('score', ascending=False))
```

### View Latest Scores in Terminal
```bash
python -c "import pandas as pd; df = pd.read_csv('outputs/weighted_score.csv'); print(df.sort_values('weighted_score', ascending=False))"
```

---

## 📚 Directory Structure

```
C:\Hermes-1\
├── main.py                 ← Run this to analyze stocks
├── requirements.txt        ← Python dependencies
├── .env                    ← Your Reddit credentials (create this)
│
├── data_ingestion/         ← How we get data
│   ├── fundamentals.py     ├─ Stock metrics
│   ├── psycho.py           ├─ VIX & Fear/Greed
│   └── social.py           └─ Reddit sentiment
│
├── analytics/              ← How we score stocks
│   └── scoring.py          └─ Scoring algorithm
│
└── outputs/                ← Results
    ├── fundamentals_scored.csv
    ├── weighted_score.csv
    ├── social_sentiment_log.csv
    ├── fear_greed_log.csv
    ├── vix_sp500_data.csv
    └── report_generator.py
```

---

## 🎯 Next Steps

After first successful run:

1. **Monitor & Verify**
   - Check output CSVs look reasonable
   - Verify stock scores make sense

2. **Customize Watchlist**
   - Edit `main.py` to track different stocks
   - Add/remove from `watchlist` variable

3. **Adjust Weights**
   - Edit `outputs/weighted_score.py` to change Fear/Greed impact
   - Or modify `scoring.py` thresholds

4. **Automate**
   - Set up Task Scheduler for daily runs
   - Or use `schedule` library for more control

5. **Integrate**
   - Build dashboard with historical data
   - Connect to trading algorithms
   - Send alerts for big score changes

---

## 🐛 Debug Mode

Add this to top of `main.py` for verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Then check console output for detailed execution trace.

---

## ⚡ Performance Tips

- **First run:** ~3-5 minutes (downloads all data)
- **Subsequent runs:** ~2-3 minutes (cached data)
- **Reddit analysis:** Takes longest (50+ API calls)
  - Can disable if you want just fundamentals + VIX

To speed up:
```python
# Skip Reddit (add to main.py after line 37)
# Comment these out:
# analyzer = RedditSentimentAnalyzer()
# update_social_sentiment_log(watchlist)

# Results will be faster but less complete
```

---

## 📞 Common Questions

**Q: Can I use different stocks?**
A: Yes! Edit `watchlist` in `main.py`:
```python
watchlist = ['GOOGL', 'META', 'AMZN']  # etc.
```

**Q: Why does Reddit sentiment sometimes fail?**
A: May hit rate limits. Just re-run in 5 minutes.

**Q: Can I run this on my phone?**
A: No, requires Python and Windows. But you can:
- Export CSVs to cloud
- Build web dashboard
- Create mobile app that reads data

**Q: Is this financial advice?**
A: No! Hermes is a tool to help analysis. Always do your own research.

**Q: Can I share my results?**
A: Sure! But don't share the `.env` file (has API credentials).

---

## 🎓 Learning More

### Project Docs:
- `DIRECTORY_ANALYSIS.md` - Deep dive into architecture
- `CONTEXT_ENGINEERING_STRATEGY.md` - Advanced features roadmap

### External Resources:
- Yahoo Finance API: https://yfinance.readthedocs.io/
- PRAW Reddit API: https://praw.readthedocs.io/
- Transformers/BERT: https://huggingface.co/

### Example Scripts:
```python
# Just fundamentals
from data_ingestion.fundamentals import fetch_stock_data
df = fetch_stock_data(['AAPL', 'MSFT'])
print(df)

# Just VIX/S&P
from data_ingestion.psycho import fetch_vix_and_sp500_data
vix_data = fetch_vix_and_sp500_data()
print(vix_data.tail())

# Just Reddit
from data_ingestion.social import RedditSentimentAnalyzer
analyzer = RedditSentimentAnalyzer()
sentiment = analyzer.get_sentiment_summary(['AAPL', 'MSFT'])
print(sentiment)
```

---

## ✅ Checklist Before First Run

- [ ] `.env` file created with Reddit credentials
- [ ] `outputs/` directory exists
- [ ] All requirements installed: `pip install -r requirements.txt`
- [ ] Internet connection active
- [ ] No VPN blocking Reddit API
- [ ] Sufficient disk space (~100MB for data)
- [ ] Python 3.9+ installed

**Ready?** Run it:
```bash
python main.py
```

Good luck! 🚀


