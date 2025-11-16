# 🚀 Hermes - Multi-Factor Stock Analysis Engine

**Hermes** is an intelligent stock analysis system that combines fundamentals, market psychology, and social sentiment to generate composite investment scores for a watchlist of stocks.

## 📊 What Does Hermes Do?

Analyzes 16 custom assets across three dimensions:
- **Inverse ETFs:** SQQQ, UVXY, SPXU
- **Tech:** MSFT, GOOGL, INTC, AMD
- **Quantum Computing:** RGTI, QBTS, IONQ, QUBT, QMCO
- **Other:** RNA, DYN, GLD, BTC-USD

| Dimension | Source | Metric | Update |
|-----------|--------|--------|--------|
| **Fundamentals** | Yahoo Finance | P/E, P/B, D/E, ROE ratios | Daily |
| **Psychology** | CNN + yfinance | Fear & Greed Index, VIX | Real-time |
| **Social** | Reddit | Sentiment + Engagement | Real-time |
| **Composite** | Custom Algorithm | Weighted Score 0-100 | Triggered |

**Output:** Ranked list of stocks with scores, updated to `outputs/` directory.

---

## 🎯 Quick Start

### 1️⃣ Prerequisites
- Python 3.9+
- Reddit API credentials (free at reddit.com/prefs/apps)
- Internet connection

### 2️⃣ Setup (5 minutes)
```bash
# Navigate to project
cd C:\Hermes-1

# Create outputs directory
mkdir outputs

# Install dependencies
pip install -r requirements.txt

# Create .env file with Reddit credentials
# (see .env.example or QUICK_START.md)
```

### 3️⃣ Run Analysis
```bash
python main.py
```

### 4️⃣ Check Results
```bash
# View generated files
dir outputs\

# View latest scores
cat outputs\weighted_score.csv
```

**Expected Runtime:** 2-4 minutes

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **QUICK_START.md** | Get up and running in 5 minutes |
| **DIRECTORY_ANALYSIS.md** | Deep dive into architecture and codebase |
| **CONTEXT_ENGINEERING_STRATEGY.md** | Roadmap for 5 phases of development |
| **SYSTEM_OVERVIEW.md** | Visual diagrams and technical details |

**Start here:** 👉 `QUICK_START.md` if you want to run it now  
**Deep dive:** 👉 `DIRECTORY_ANALYSIS.md` if you want to understand everything

---

## 🏗️ Project Structure

```
C:\Hermes-1\
├── main.py                              Main entry point
├── requirements.txt                     Python dependencies
├── .env                                 Credentials (create this)
├── README.md                            This file
│
├── data_ingestion/                      How we fetch data
│   ├── fundamentals.py                  Stock metrics (P/E, etc.)
│   ├── psycho.py                        VIX, Fear & Greed Index
│   └── social.py                        Reddit sentiment analysis
│
├── analytics/                           How we score stocks
│   └── scoring.py                       Scoring algorithm
│
├── outputs/                             Results & data
│   ├── fundamentals_scored.csv          Stock metrics + scores
│   ├── weighted_score.csv               Final composite scores ⭐
│   ├── social_sentiment_log.csv         Reddit sentiment
│   ├── fear_greed_log.csv               Historical index
│   ├── vix_sp500_data.csv               Market volatility data
│   ├── report_generator.py              Display results
│   └── weighted_score.py                Apply psychology weighting
│
└── docs/                                Documentation
    ├── QUICK_START.md
    ├── DIRECTORY_ANALYSIS.md
    ├── CONTEXT_ENGINEERING_STRATEGY.md
    └── SYSTEM_OVERVIEW.md
```

---

## 🧮 How Scoring Works

### Fundamental Score (Base: 0-70 points)
```
+20 points if P/E < 35
+15 points if Price/Book < 10
+20 points if Debt/Equity < 15
+15 points if ROE > 1
──────────────────────────
MAX: 70 points
```

### Psychological Weighting
```
Fear & Greed Index (0-100) → Multiplier
  > 50 (Bullish)   → Boost scores (×1.0 to ×1.40)
  < 50 (Bearish)   → Reduce scores (×0.60 to ×1.0)
  = 50 (Neutral)   → No change (×1.0)

Final Score = Base Score × Multiplier → 0-100 scale
```

### Sentiment Component
- **Reddit posts**: Positive vs. Negative sentiment
- **Comments**: Sub-sentiment on posts
- **Engagement**: Upvotes and discussion volume
- **Mentions**: How often stock mentioned

---

## 🔄 Data Pipeline

```
📥 INPUT                 ⚙️ PROCESSING              📤 OUTPUT
─────────────────────────────────────────────────────────────

Watchlist          Fundamentals.py            CSV Files
[5 stocks]    →    [Score calculation]   →   [Ranked results]
              
              Psycho.py
              [Fear & Greed weighting]
              
              Social.py
              [Reddit sentiment analysis]
              
              Report Generator
              [Terminal output]
```

**Duration:** 2-4 minutes (Reddit analysis is slowest)

---

## 📊 Example Output

```
WEIGHTED SCORES - Latest Results

ticker │ weighted_score
───────┼────────────────
NVDA   │ 78.5
AAPL   │ 72.3
MSFT   │ 68.1
AMZN   │ 55.4
TSLA   │ 48.9
```

---

## 🛠️ Configuration

### Change Watchlist
Edit `main.py` (lines 14-16):
```python
watchlist = ['GOOGL', 'META', 'AMZN']  # Your stocks
```

### Adjust Scoring Thresholds
Edit `analytics/scoring.py` (lines 5-23):
```python
if stock['trailingPE'] and stock['trailingPE'] < 30:  # Changed from 35
    score += 25  # Changed from 20
```

### Skip Components
Comment out in `main.py`:
```python
# analyzer = RedditSentimentAnalyzer()  # Skip Reddit
# update_social_sentiment_log(watchlist)
```

---

## 🔗 Dependencies

### Required Libraries
- **praw** (Reddit API)
- **textblob** (Sentiment analysis)
- **transformers** (BERT models)
- **yfinance** (Stock data)
- **selenium** (Web scraping)
- **pandas** (Data manipulation)

See `requirements.txt` for full list and versions.

---

## 🚨 Troubleshooting

### "ModuleNotFoundError: No module named 'outputs'"
**Fix:** Create outputs directory and copy files from `C:\Hermes\outputs\`

### "REDDIT_CLIENT_ID not found"
**Fix:** Create `.env` file with credentials (see QUICK_START.md)

### "Connection timeout"
**Fix:** Check internet. If Reddit/Yahoo down, try again in 5 min.

### "Sentiment score failed"
**Fix:** Normal occasionally. Just re-run. Reddit might hit rate limits.

See **QUICK_START.md** for more troubleshooting.

---

## 🗂️ Two Directories?

You have:
- **C:\Hermes-1** (ACTIVE - use this)
  - Most recent code (11/14/2025)
  - Missing outputs/ directory
  
- **C:\Hermes** (ARCHIVE)
  - Older code (May 2025)
  - Contains historical data in outputs/

**Recommendation:** Copy data from `C:\Hermes\outputs\` to `C:\Hermes-1\outputs\`, then use `C:\Hermes-1` for all future work.

---

## 🎯 Next Steps

**Option 1: Get It Running Now** (30 min)
1. Read `QUICK_START.md`
2. Follow setup steps
3. Run `python main.py`

**Option 2: Understand the System** (1 hour)
1. Read `DIRECTORY_ANALYSIS.md` 
2. Understand each component
3. Review data pipeline

**Option 3: Plan Improvements** (30 min)
1. Read `CONTEXT_ENGINEERING_STRATEGY.md`
2. Choose development phase
3. Start with Phase 1

---

## 📈 Development Roadmap

### ✅ Phase 1: Foundation (Days 1-2)
Setup environment, verify all imports work, first successful run.

### 🔨 Phase 2: Architecture (Days 3-5)
Refactor code, improve error handling, add logging.

### 🚀 Phase 3: Features (Days 6-10)
Add technical indicators, more sentiment sources, dashboard.

### 💾 Phase 4: Data (Days 11-14)
Database integration, caching, validation layer.

### 🌐 Phase 5: Deployment (Days 15-20)
Automation, scheduling, API exposure, CI/CD.

See `CONTEXT_ENGINEERING_STRATEGY.md` for full roadmap.

---

## ⚖️ Limitations & Assumptions

### ✓ Strengths
- Combines 3 independent signals (fundamentals, psychology, sentiment)
- Modular design (each source independent)
- Automated historical logging
- Reddit captures retail sentiment

### ⚠️ Limitations
- Scores are current state, not predictive
- P/E thresholds somewhat arbitrary
- Reddit skewed toward small-cap/retail traders
- External API dependencies
- Fear & Greed Index updates infrequently

### 🎯 Not Financial Advice
This tool helps with analysis. Always do your own research before investing.

---

## 👨‍💻 Technical Stack

| Layer | Technology |
|-------|------------|
| **Language** | Python 3.9+ |
| **Data** | pandas, numpy |
| **APIs** | yfinance, PRAW, Selenium |
| **ML** | transformers (DistilBERT) |
| **Visualization** | tabulate, plotly (future) |
| **Database** | CSV (PostgreSQL in Phase 4) |

---

## 📞 Support

### Documentation
- `QUICK_START.md` - Get running in 5 minutes
- `DIRECTORY_ANALYSIS.md` - Architecture overview
- `CONTEXT_ENGINEERING_STRATEGY.md` - Development roadmap
- `SYSTEM_OVERVIEW.md` - Visual diagrams

### External Resources
- [yfinance docs](https://yfinance.readthedocs.io/)
- [PRAW docs](https://praw.readthedocs.io/)
- [Transformers docs](https://huggingface.co/)

### Common Issues
See troubleshooting section above or `QUICK_START.md`.

---

## 📜 License

Not specified. Use at your own discretion.

---

## 🎉 Ready?

```bash
cd C:\Hermes-1
python main.py
```

Good luck! 🚀

---

**Last Updated:** November 14, 2025  
**Status:** ✅ Ready to Deploy  
**Maintainer:** You!

