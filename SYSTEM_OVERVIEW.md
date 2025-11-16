# Hermes System Overview - Visual Architecture

## 🏗️ System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        HERMES ANALYSIS ENGINE                       │
└─────────────────────────────────────────────────────────────────────┘

                    🎯 INPUT: Watchlist (5 stocks)
                              │
                              ▼
         ┌────────────────────────────────────────┐
         │     DATA INGESTION LAYER               │
         └────────────────────────────────────────┘
                    │          │          │
         ┌──────────┴──────────┼──────────┴───────────┐
         │                     │                      │
         ▼                     ▼                      ▼
    ┌─────────┐          ┌─────────┐          ┌─────────┐
    │FUNDAMENT│          │ PSYCHO  │          │ SOCIAL  │
    │   ALS   │          │ LOGIC   │          │SENTIMENT│
    └─────────┘          └─────────┘          └─────────┘
         │                     │                      │
    • P/E Ratio            • VIX Data             • Reddit Posts
    • P/B Ratio            • S&P 500              • Sentiment
    • Debt/Equity          • Fear & Greed         • Mentions
    • ROE                  • Index (0-100)        • Engagement
    • Market Cap                                 • Comments
         │                     │                      │
         └──────────────────────┼──────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  SCORING ENGINE     │
                    │  (analytics/)       │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┴──────────────────────┐
        │                                             │
    ┌───▼────────┐                         ┌─────────▼───┐
    │ FUNDAMENTAL│                         │ WEIGHTING   │
    │    SCORE   │                         │   MODULE    │
    │ (0-70)     │────────────────────────►│  (multiplier)
    └────────────┘                         └──────┬──────┘
                                                   │
                                          ┌────────▼────────┐
                                          │ FINAL COMPOSITE │
                                          │  SCORE (0-100)  │
                                          └────────┬────────┘
                                                   │
                               ┌───────────────────┼───────────────────┐
                               │                   │                   │
                    ┌──────────▼─────────┐        ▼        ┌──────────▼─────────┐
                    │  CSV OUTPUTS       │    CACHE     │  REPORT GENERATOR   │
                    │  (outputs/)        │              │  (Terminal Display) │
                    │                    │              │                     │
                    │ • fundamentals_    │              │ ┌─────────────────┐ │
                    │   scored.csv       │              │ │  TICKER │ SCORE │ │
                    │ • weighted_score   │              │ │ AAPL    │  75   │ │
                    │   .csv             │              │ │ MSFT    │  68   │ │
                    │ • social_sentiment │              │ │ NVDA    │  71   │ │
                    │   _log.csv         │              │ │ TSLA    │  62   │ │
                    │ • fear_greed_log   │              │ │ AMZN    │  64   │ │
                    │   .csv             │              │ └─────────────────┘ │
                    │ • vix_sp500_data   │              └─────────────────────┘
                    │   .csv             │
                    └────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  DATA PERSISTENCE   │
                    │  (Historical Log)   │
                    │                     │
                    │ • Track over time   │
                    │ • Analyze trends    │
                    │ • Backtesting       │
                    └─────────────────────┘
```

---

## 🔄 Data Flow Pipeline

```
SCHEDULE/TRIGGER
    │
    ▼
┌─────────────────────────────┐
│ 1. FETCH FUNDAMENTALS       │
│    yfinance.download()      │
│    → 5 stocks × 9 metrics   │
└──────────┬──────────────────┘
           │
    ┌──────▼────────┐
    │    ✓ OK       │ (avg 2-3 sec)
    │  OR ✗ FAIL    │ (use cached)
    └──────┬────────┘
           │
           ▼
┌─────────────────────────────┐
│ 2. CALCULATE SCORES         │
│    Points-based system      │
│    Max: 70 points           │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ 3. FETCH VIX & S&P500       │
│    yfinance.download()      │
│    period: 6mo (history)    │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ 4. SCRAPE FEAR & GREED      │
│    Selenium + CNN           │
│    0-100 sentiment index     │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ 5. ANALYZE REDDIT           │
│    PRAW API                 │
│    3 subreddits × 100 posts │
│    Sentiment + Engagement   │
│    (Slowest: 2-3 min)       │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ 6. CALCULATE WEIGHTS        │
│    fear_greed_score → 0.8-1.2x
│    Apply to base scores     │
│    Final: 0-100 scale       │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ 7. GENERATE REPORT          │
│    Terminal output          │
│    CSV saved                │
│    Log appended              │
└──────────┬──────────────────┘
           │
    ┌──────▼────────┐
    │   COMPLETED   │
    │   ✓ 5 mins    │
    └───────────────┘
```

---

## 🧩 Component Interaction Matrix

```
                 │ Fundamental │ Psycho │ Social │ Scoring │ Output
─────────────────┼─────────────┼────────┼────────┼─────────┼────────
Fundamentals.py  │     ✓       │   -    │   -    │    ✓    │   ✓
Psycho.py        │     -       │   ✓    │   -    │    ✓    │   ✓
Social.py        │     -       │   -    │   ✓    │    ✓    │   ✓
Scoring.py       │     ✓       │   ✓    │   ✓    │    ✓    │   ✓
Report Gen.      │     ✓       │   ✓    │   ✓    │    ✓    │   ✓
Cache            │     ✓       │   ✓    │   ✓    │    -    │   -
─────────────────┴─────────────┴────────┴────────┴─────────┴────────

✓ = Direct interaction
- = No direct interaction
```

---

## 📊 Scoring Algorithm

```
FUNDAMENTALS SCORE (Base Score)
───────────────────────────────

For each stock, calculate:

    PE_SCORE = stock.trailingPE < 35 ? 20 : 0
    PB_SCORE = stock.priceToBook < 10 ? 15 : 0
    DE_SCORE = stock.debtToEquity < 15 ? 20 : 0
    ROE_SCORE = stock.returnOnEquity > 1 ? 15 : 0
    ─────────────────────────────────────────
    BASE_SCORE = PE + PB + DE + ROE
              (0-70 max)


PSYCHOLOGICAL WEIGHTING
──────────────────────

    fear_greed_score (0-100) → multiplier calculation

    IF score > 50 (Bullish):
        multiplier = 1 + ((score - 50) × 0.02)
        range: [1.00 - 1.20] (boost)

    IF score < 50 (Bearish):
        multiplier = 1 + ((score - 50) × 0.02)
        range: [0.80 - 1.00] (reduction)

    IF score = 50 (Neutral):
        multiplier = 1.00


FINAL SCORE CALCULATION
──────────────────────

    weighted_score = base_score × multiplier
    normalized = weighted_score / 0.70  (scale to 0-100)

Example:
    AAPL base score: 65
    Fear & Greed: 70 (bullish)
    Multiplier: 1 + ((70-50) × 0.02) = 1.40
    Weighted: 65 × 1.40 = 91.0  ← HIGH SCORE!

    MSFT base score: 45
    Fear & Greed: 30 (bearish)
    Multiplier: 1 + ((30-50) × 0.02) = 0.60
    Weighted: 45 × 0.60 = 27.0  ← LOW SCORE!
```

---

## 🎯 Sentiment Scoring Breakdown

```
SOCIAL SENTIMENT (Reddit)
─────────────────────────

Per Stock Analysis:
    │
    ├─ Post Sentiment
    │  ├─ POSITIVE count
    │  ├─ NEGATIVE count
    │  └─ NEUTRAL count
    │  → sentiment_score = POSITIVE - NEGATIVE
    │
    ├─ Comment Sentiment (recursively analyzed)
    │  ├─ POSITIVE count
    │  ├─ NEGATIVE count
    │  └─ NEUTRAL count
    │  → comment_sentiment_score = POSITIVE - NEGATIVE
    │
    ├─ Total Sentiment
    │  └─ total_score = posts + comments
    │
    └─ Engagement
       ├─ Total mentions (num_posts)
       ├─ Upvotes on posts (post_score)
       └─ Total comments (num_comments)
         → High engagement = more reliable signal


EXAMPLE OUTPUT:
┌─────────┬──────────┬──────────┬────────┬─────────────┬────────┐
│ TICKER  │ POSITIVE │ NEGATIVE │ NEUTRAL│ SENT_SCORE  │ POSTS  │
├─────────┼──────────┼──────────┼────────┼─────────────┼────────┤
│ AAPL    │    45    │    12    │   23   │     +33     │   80   │ ✓
│ TSLA    │    28    │    35    │   17   │     -7      │   68   │ ✗
│ NVDA    │    52    │     8    │   20   │     +44     │   95   │ ✓✓
└─────────┴──────────┴──────────┴────────┴─────────────┴────────┘

Higher positive sentiment + more posts = more bullish signal
```

---

## ⏱️ Timing & Performance

```
EXECUTION TIMELINE
──────────────────

Time    Component              Duration    Status
────    ─────────────────────  ──────────  ──────
0:00    Start                  -           ▓
0:05    Fundamentals           5 sec       ▓ ✓
0:10    Calculate Scores       1 sec       ▓ ✓
0:15    VIX/S&P500             8 sec       ▓ ✓
0:30    Fear & Greed Scrape    15 sec      ▓ ✓ (Selenium)
1:00    Reddit Analysis        90 sec      ▓▓▓▓▓ ✓ (Slowest!)
2:30    Weighted Scoring       5 sec       ▓ ✓
2:35    Report & Cache         5 sec       ▓ ✓
3:00    END                    3 min       ✓ ✓ ✓

Total Expected: 2-4 minutes
- First run: 3-5 min (initial model download)
- Subsequent: 2-3 min (cached)
```

---

## 🔐 Data Flow Security

```
SENSITIVE DATA HANDLING
───────────────────────

.env (Protected)
├─ REDDIT_CLIENT_ID
├─ REDDIT_CLIENT_SECRET
└─ REDDIT_USER_AGENT
   │
   └─► Loaded via dotenv (never logged)
       Used only for API auth
       ✓ Not stored in git
       ✓ Not in output files
       ✓ Not in logs


OUTPUT FILES (Safe to Share)
├─ fundamentals_scored.csv
│  └─ Public stock data + our analysis
│
├─ social_sentiment_log.csv
│  └─ Aggregated Reddit sentiment (no IDs)
│
├─ weighted_score.csv
│  └─ Our scoring results
│
└─ fear_greed_log.csv
   └─ CNN public data (historical record)


DO NOT SHARE:
├─ .env (API credentials)
├─ __pycache__/ (compiled code)
├─ .git/ (local history)
└─ Any logs with error tracebacks
```

---

## 🎨 Class Hierarchy

```
┌─────────────────────────────────────┐
│      RedditSentimentAnalyzer        │
│     (data_ingestion/social.py)      │
└──────────────┬──────────────────────┘
               │
        ┌──────┴─────────┐
        │                │
    Methods:         Attributes:
        │                │
    ├─ __init__         ├─ reddit (PRAW client)
    ├─ fetch_reddit_    ├─ subreddits (list)
    │  posts()          └─ rate_limit_delay
    │
    ├─ fetch_comments()
    │
    ├─ clean_reddit_
    │  text()
    │
    ├─ extract_stock_
    │  mentions()
    │
    ├─ analyze_
    │  sentiment()
    │
    ├─ get_sentiment_
    │  summary()
    │
    ├─ get_comment_
    │  sentiment_summary()
    │
    └─ get_sentiment_
       summary_with_
       comments()


EXECUTION FLOW:
get_sentiment_summary() → for each subreddit:
    ↓
fetch_reddit_posts()
    ↓ (100 posts × 3 subreddits)
    │
    ├─→ for each post:
    │   ├─ clean_reddit_text()
    │   ├─ extract_stock_mentions()
    │   ├─ analyze_sentiment()
    │   └─ store result
    │
    └─→ aggregate by ticker
        return DataFrame
```

---

## 📈 Data Transformation Pipeline

```
RAW INPUT                 PROCESSING                  OUTPUT
─────────────────────────────────────────────────────────────────

Yahoo Finance             Fundamentals.py             CSV
(yfinance)            ─────────────────────►    fundamentals_
  │ 5 tickers              │                    scored.csv
  └─ 9 metrics each    Extract & Clean          (with scores)
     per stock         Validate
                       → DataFrame
                       
                       
VIX Index             Psycho.py              CSV
S&P 500           ─────────────────────►  vix_sp500_
(yfinance)            │                  data.csv
  │ 6mo history   Fetch historical
  └─ daily        Combine series
                  → DataFrame
                  
                  
CNN Website           Psycho.py              CSV
(Selenium)        ─────────────────────►  fear_greed_
  │ Fear & Greed      │                  log.csv
  │ Index (0-100)     Scrape & Extract   (with timestamp)
  └─ Real-time        Parse JavaScript
                      Append to log
                      → CSV updated
                      
                      
Reddit              Social.py              CSV
(PRAW API)        ─────────────────────►  social_
  │ 3 subreddits       │                  sentiment_
  │ 100 posts each    Fetch posts/comments
  │ Post metadata     Clean text           log.csv
  └─ Comments         Detect mentions     (sentiment +
     & engagement    Analyze sentiment     engagement)
                     Aggregate
                     → DataFrame
                     → CSV appended
                     
                     
Base Scores        Scoring.py             CSV
+ F/G Index    ─────────────────────►  weighted_
(from above)       │                  score.csv
                Apply multiplier        (final scores)
                Calculate weights
                Normalize 0-100
                → DataFrame
                
                
All CSVs           Report Gen.         STDOUT
              ─────────────────────►   Terminal
                Display table           Report
                Format nicely
                → Print
```

---

## 🔄 State Management

```
SESSION STATE
─────────────

        ┌──────────────┐
        │  INITIALIZE  │
        │ (main.py)    │
        └───────┬──────┘
                │
    ┌───────────▼───────────┐
    │   LOAD/SET CONFIG     │
    │ • Watchlist           │
    │ • Thresholds          │
    │ • Output paths        │
    └───────────┬───────────┘
                │
    ┌───────────▼───────────┐
    │   LOAD CREDENTIALS    │
    │ • .env file           │
    │ • Reddit client       │
    └───────────┬───────────┘
                │
    ┌───────────▼───────────┐
    │  FETCH DATA           │
    │ (All 3 sources)       │
    │ Each stores:          │
    │ • Results in memory   │
    │ • Cache on disk       │
    └───────────┬───────────┘
                │
    ┌───────────▼───────────┐
    │  CALCULATE SCORES     │
    │ • Transform data      │
    │ • Apply algorithms    │
    │ • Generate outputs    │
    └───────────┬───────────┘
                │
    ┌───────────▼───────────┐
    │  PERSIST RESULTS      │
    │ • Write CSV files     │
    │ • Append to logs      │
    │ • Print report        │
    └───────────┬───────────┘
                │
        ┌───────▼────────┐
        │  CLEANUP       │
        │  END           │
        └────────────────┘
```

---

## 🚨 Error Handling Strategy

```
TRY/CATCH FLOW
──────────────

main.py
  │
  ├─► Fundamentals.fetch_stock_data()
  │   ├─ On SUCCESS: continue with scores
  │   └─ On FAIL: 
  │       ├─ Log error
  │       ├─ Try cached data
  │       └─ Continue (graceful degradation)
  │
  ├─► Psycho.fetch_vix_and_sp500_data()
  │   └─ On FAIL:
  │       ├─ Log error
  │       └─ Use last known values
  │
  ├─► Psycho.fetch_fear_greed_index()
  │   └─ On FAIL:
  │       ├─ Log error
  │       ├─ Default multiplier = 1.0
  │       └─ Continue with unweighted scores
  │
  ├─► Social.get_sentiment_summary()
  │   └─ On FAIL:
  │       ├─ Log warning
  │       ├─ Return empty sentiment
  │       └─ Continue without social signal
  │
  └─► Report.generate_report()
      └─ On FAIL:
          ├─ Still save CSVs
          └─ Print error to console


RESILIENCE LEVELS:
✓✓✓ = System still works
✓✓  = Degraded functionality
✓   = Minimal output
✗   = Complete failure

Fundamentals fail:     ✓✓  (try cache)
Psycho fails:          ✓✓✓ (use defaults)
Social fails:          ✓✓✓ (skip sentiment)
Report fails:          ✓✓✓ (save raw CSVs)
```

---

## 🎓 Key Insights

### Strengths ✓
- **Multi-source validation**: Combines 3 independent signals
- **Psychological indicator**: Fear/Greed weighting is unique
- **Crowd-sourced**: Reddit sentiment captures retail sentiment
- **Modular design**: Each data source is independent
- **Automated logging**: Historical tracking enables backtesting

### Limitations ⚠️
- **Points-based scoring**: Somewhat arbitrary thresholds
- **Reddit bias**: Retail/small-cap skewed (not institutional view)
- **API dependencies**: Multiple external APIs = multiple failure points
- **Real-time issues**: Fear & Greed updates infrequently
- **No prediction**: Scores are current state, not predictive

### Enhancement Opportunities 🚀
- Add machine learning for dynamic weighting
- Integrate institutional sentiment (SEC filings, hedge fund positions)
- Add technical analysis (RSI, MACD, Bollinger Bands)
- Implement portfolio optimization
- Add backtesting framework
- Create alert system for score changes

---

This system is designed to be **modular, extensible, and resilient**. Each component can fail independently without crashing the whole system.


