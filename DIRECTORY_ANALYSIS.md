# Hermes Project - Directory Analysis & Context Engineering Plan

## Executive Summary

After thorough analysis of both `C:\Hermes-1` and `C:\Hermes`, here's what was found:

**Key Finding:** `C:\Hermes-1` contains the most recent files (modified **11/14/2025 5:13 PM today**), while `C:\Hermes` has older versions (main.py from **5/19/2025**, logger.py from **4/13/2025**).

### Recommendation
**Use `C:\Hermes-1` as the primary working directory** - it's up-to-date and contains the active development code.

---

## Directory Comparison

### C:\Hermes-1 (ACTIVE/CURRENT)
**Status:** Most recent, currently in use
**Last Modified:** 11/14/2025 5:13:12 PM

```
C:\Hermes-1\
├── main.py                          (ACTIVE - 11/14/2025)
├── logger.py                        (ACTIVE - 11/14/2025)
├── README.md                        (Empty)
├── requirements.txt                 (Latest dependencies)
├── fear_greed_debug.png             (Debug artifact)
├── analytics/
│   └── scoring.py                   (Stock scoring logic)
└── data_ingestion/
    ├── fundamentals.py              (Yahoo Finance data fetch)
    ├── psycho.py                    (VIX, S&P500, Fear & Greed)
    ├── social.py                    (Reddit sentiment analysis)
    ├── test_social.py               (Tests)
    └── psycho - Copy.py             (Backup file)
```

### C:\Hermes (OLDER/ARCHIVED)
**Status:** Contains older code + additional outputs directory
**Last Modified:** main.py (5/19/2025), logger.py (4/13/2025)

```
C:\Hermes\
├── main.py                          (OLDER - 5/19/2025)
├── logger.py                        (OLDER - 4/13/2025)
├── README.md                        (Empty)
├── requirements.txt                 (Same dependencies)
├── fear_greed_debug.png
├── __pycache__/                     (Compiled Python)
├── analytics/
│   ├── __pycache__/
│   └── scoring.py
├── data_ingestion/
│   ├── __pycache__/
│   ├── chromedriver.exe             (Selenium driver)
│   ├── fundamentals.py
│   ├── psycho.py
│   ├── psycho - Copy.py
│   ├── social.py
│   └── test_social.py
└── outputs/                         (IMPORTANT DATA!)
    ├── fear_greed_log.csv           (Historical Fear & Greed Index)
    ├── fundamentals_data.csv        (Stock fundamentals)
    ├── fundamentals_scored.csv      (Scored fundamentals)
    ├── social_sentiment_log.csv     (Reddit sentiment history)
    ├── vix_sp500_data.csv           (VIX & S&P 500 data)
    ├── weighted_score.csv           (Final weighted scores)
    ├── weighted_score.py            (Scoring script)
    ├── report_generator.py          (Report generation)
    └── logger.py                    (Output-specific logger)
```

---

## Project Overview

### Project Name
**Hermes** - A multi-factor stock analysis system that combines:

1. **Fundamentals Analysis** (Yahoo Finance)
2. **Psychological/Market Indicators** (VIX, S&P 500, Fear & Greed Index)
3. **Social Sentiment Analysis** (Reddit: WSB, stocks, investing subreddits)
4. **Composite Scoring** (Weighted algorithm)

### Current Watchlist
```python
['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN']
```

---

## Data Pipeline & Architecture

### 1. **Data Ingestion Layer** (`data_ingestion/`)

#### `fundamentals.py`
- **Input:** Stock tickers (AAPL, MSFT, NVDA, TSLA, AMZN)
- **Source:** Yahoo Finance via `yfinance`
- **Metrics Fetched:**
  - `ticker`, `longName`, `sector`
  - `marketCap`, `trailingPE`, `forwardPE`
  - `pegRatio`, `priceToBook`, `debtToEquity`, `returnOnEquity`
- **Output:** DataFrame with fundamental metrics

#### `psycho.py` (Psychological/Market Indicators)
- **VIX & S&P 500 Fetching:**
  - Downloads historical data via `yfinance`
  - Default period: 6 months, daily intervals
  - Combines VIX (volatility index) with S&P 500 close prices
  
- **Fear & Greed Index Scraping:**
  - Uses Selenium to scrape CNN's Fear & Greed Index
  - Headless browser + WebDriverManager for ChromeDriver
  - Extracts fear_greed_score (0-100 scale)
  - Appends to `outputs/fear_greed_log.csv` with timestamp

#### `social.py` (Reddit Sentiment Analysis)
- **Class:** `RedditSentimentAnalyzer`
- **API:** PRAW (Python Reddit API Wrapper)
- **Credentials:** Loaded from `.env` file
  - `REDDIT_CLIENT_ID`
  - `REDDIT_CLIENT_SECRET`
  - `REDDIT_USER_AGENT`
  
- **Features:**
  - Monitors 3 subreddits: `wallstreetbets`, `stocks`, `investing`
  - Fetches top 100 posts per subreddit (daily time filter)
  - Sentiment analysis via:
    - **TextBlob** (basic polarity scoring)
    - **DistilBERT** (transformer-based sentiment model)
  - Stock mention extraction (handles variations: $AAPL, APPLE, APPLE INC, etc.)
  - Comment-level sentiment analysis (recursive tree traversal)
  - Engagement metrics: post scores, comment counts
  
- **Output:** Multi-level sentiment scores (posts + comments)

### 2. **Analytics Layer** (`analytics/`)

#### `scoring.py`
**Fundamental Score Calculation** (Points-based system):
```
Base Score = 0

+ 20 points if trailing P/E < 35
+ 15 points if price-to-book < 10
+ 20 points if debt-to-equity < 15
+ 15 points if ROE > 1

Max Score: ~70 points
```

**Psycho-adjusted Scoring** (`outputs/weighted_score.py`):
- Takes Fear & Greed Index (latest value)
- Calculates multiplier: `1 + ((fear_greed_score - 50) * 0.02)`
  - Bull market (>50): increases score
  - Bear market (<50): decreases score
- Applies multiplier to fundamental scores

### 3. **Output Generation** (`outputs/`)

#### Data Files Generated
- `fundamentals_scored.csv` - Stocks with fundamental scores
- `fear_greed_log.csv` - Historical Fear & Greed Index readings
- `vix_sp500_data.csv` - Historical VIX and S&P 500 data
- `social_sentiment_log.csv` - Reddit sentiment history
- `weighted_score.csv` - Final composite scores

#### Report Generation
- `report_generator.py` - CLI table display using `tabulate`
- Displays: ticker, company name, sector, composite score
- Sorted by score (descending)

---

## Main Execution Flow (`main.py`)

```python
1. Fetch fundamental data (Yahoo Finance)
   ↓
2. Calculate fundamental scores
   ↓
3. Fetch VIX/S&P 500 data (6-month history)
   ↓
4. Scrape Fear & Greed Index
   ↓
5. Analyze Reddit sentiment for watchlist
   ↓
6. Apply psychological weighting to scores
   ↓
7. Generate composite report
   ↓
8. Git LFS operations (sync with remote)
```

---

## Dependencies & Environment

### Key Libraries (from `requirements.txt`)
```
praw==7.7.1              # Reddit API
textblob==0.17.1         # Basic NLP sentiment
pandas==2.1.4            # Data manipulation
python-dotenv==1.0.0     # Environment variables
transformers==4.36.2     # DistilBERT sentiment model
torch==2.1.2             # Deep learning framework
```

### Additional Tools
- `yfinance` - Stock data (implied dependency)
- `selenium` - Web scraping (implied)
- `webdriver-manager` - ChromeDriver management (implied)
- `beautifulsoup4` - HTML parsing (implied)
- `tabulate` - Pretty CLI tables (implied)

### Environment Variables Required
```
REDDIT_CLIENT_ID=<your_reddit_app_id>
REDDIT_CLIENT_SECRET=<your_reddit_app_secret>
REDDIT_USER_AGENT=<your_reddit_user_agent>
```

---

## Data Model Schema

### Stock Fundamentals
```
ticker | longName | sector | marketCap | trailingPE | forwardPE | pegRatio | priceToBook | debtToEquity | returnOnEquity | score
```

### Reddit Sentiment Summary
```
ticker | POSITIVE | NEGATIVE | NEUTRAL | sentiment_score | comment_sentiment_score | total_sentiment_score | num_posts | post_score | num_comments | top_comment | timestamp
```

### Fear & Greed Log
```
date | fear_greed_score
```

### Weighted Score Output
```
ticker | weighted_score
```

---

## Current Issues & Observations

### 1. **Code Duplication**
- `psycho - Copy.py` files in both directories (backup/legacy)
- Consider removing these cleanup files

### 2. **Missing .env Credentials**
- Reddit API credentials not committed
- Essential for `social.py` functionality
- **Action:** Create `.env` with REDDIT_* variables

### 3. **Missing outputs/ Directory in C:\Hermes-1**
- Historical data exists in `C:\Hermes\outputs/`
- Recent code in `C:\Hermes-1/` won't find outputs directory
- **Action:** Create `C:\Hermes-1\outputs/` directory OR migrate data

### 4. **Git Operations in main.py**
- Lines 42-47 perform git LFS operations
- Requires git credentials and SSH setup
- May fail in non-git environments

### 5. **Redundant Logger**
- `logger.py` exists in root and `outputs/`
- Import path references root version

### 6. **Module Import Issues**
- Main imports from `outputs.report_generator`
- But `C:\Hermes-1` doesn't have `outputs/` directory yet
- Will fail on execution

---

## Context Engineering Plan

### Phase 1: Environment Setup & Consolidation
- [ ] Create `.env` file with Reddit API credentials
- [ ] Create `C:\Hermes-1\outputs/` directory
- [ ] Copy historical data from `C:\Hermes\outputs/` to `C:\Hermes-1\outputs/`
- [ ] Create `C:\Hermes-1\outputs\report_generator.py` (copy from C:\Hermes)
- [ ] Verify `requirements.txt` has all implicit dependencies (yfinance, selenium, etc.)
- [ ] Set working directory to `C:\Hermes-1`

### Phase 2: Code Quality & Testing
- [ ] Add type hints to functions
- [ ] Implement error handling for API failures
- [ ] Create unit tests for scoring logic
- [ ] Test Reddit sentiment analyzer with mocked data
- [ ] Add logging configuration to main.py

### Phase 3: Architecture Improvements
- [ ] Extract scoring configuration to YAML/JSON
- [ ] Create data validation layer
- [ ] Implement caching for repeated API calls
- [ ] Add retry logic with exponential backoff
- [ ] Separate concerns: move weighted scoring to analytics layer

### Phase 4: Enhanced Features
- [ ] Add more technical indicators (RSI, MACD, moving averages)
- [ ] Implement alternative sentiment sources (news APIs, Twitter)
- [ ] Create visualization dashboard
- [ ] Add portfolio recommendation engine
- [ ] Implement backtesting framework

### Phase 5: Deployment & Monitoring
- [ ] Create automated scheduled runs (daily/hourly)
- [ ] Implement data persistence layer (database)
- [ ] Add alerting system for score changes
- [ ] Create CI/CD pipeline
- [ ] Document API rate limits and throttling

---

## Quick Start Instructions

### To Run the Project Now:
```bash
cd C:\Hermes-1

# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up credentials
# Create .env file with:
# REDDIT_CLIENT_ID=your_id
# REDDIT_CLIENT_SECRET=your_secret
# REDDIT_USER_AGENT=your_agent

# 3. Create outputs directory
mkdir outputs

# 4. Run the analysis
python main.py
```

### Output Locations:
```
C:\Hermes-1\outputs\
├── fundamentals_scored.csv
├── vix_sp500_data.csv
├── fear_greed_log.csv
├── social_sentiment_log.csv
└── weighted_score.csv
```

---

## Next Steps

Would you like to proceed with:
1. **Phase 1 (Environment Setup)** - Get everything running
2. **Phase 2 (Code Quality)** - Improve existing code
3. **Phase 3 (Architecture)** - Refactor for maintainability
4. **Phase 4 (Features)** - Add new capabilities
5. **Specific Issue** - Fix the identified problems first

**Recommendation:** Start with Phase 1 to get the project running successfully, then move to Phase 2 for robustness.


