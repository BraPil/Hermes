# Context Engineering Strategy for Hermes

## What is Hermes?

**Hermes** is a multi-dimensional stock analysis engine that integrates:
- 📊 **Fundamental Analysis** (P/E ratios, debt, ROE)
- 😨 **Market Psychology** (VIX, Fear & Greed Index)
- 💬 **Social Sentiment** (Reddit trading communities)
- 🎯 **Composite Scoring** (Weighted algorithm)

**Target Stocks:** AAPL, MSFT, NVDA, TSLA, AMZN

---

## Current State Assessment

### ✅ What's Working
1. Core data ingestion pipeline established
2. Three independent data sources integrated
3. Sentiment analysis framework (with transformer models)
4. Historical data collection systems
5. Basic fundamental scoring logic

### ⚠️ What Needs Attention
1. **Broken imports** - main.py references outputs/report_generator.py but directory doesn't exist in C:\Hermes-1
2. **Missing credentials** - Reddit API credentials not configured
3. **Missing data** - outputs/ directory with historical data exists only in C:\Hermes
4. **Code duplication** - Multiple "Copy" files need cleanup
5. **No error recovery** - Failures in one component halt entire pipeline

### 🎯 Missing Pieces
1. Outputs directory structure
2. Environment configuration (.env)
3. Data persistence layer
4. Robust error handling
5. Comprehensive testing

---

## Context Engineering Phases

### 📋 PHASE 1: FOUNDATION (Days 1-2)
**Goal:** Get the project running end-to-end

#### 1.1 Directory Structure
```bash
# Create missing outputs directory
mkdir C:\Hermes-1\outputs

# Copy historical data from archive
xcopy C:\Hermes\outputs\*.csv C:\Hermes-1\outputs\ /Y

# Copy missing modules
copy C:\Hermes\outputs\report_generator.py C:\Hermes-1\outputs\
copy C:\Hermes\outputs\weighted_score.py C:\Hermes-1\outputs\
```

#### 1.2 Environment Configuration
Create `C:\Hermes-1\.env`:
```
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=your_user_agent_here
```

#### 1.3 Dependency Verification
```bash
# Ensure requirements include all needed packages
pip install -r requirements.txt
pip install yfinance selenium webdriver-manager beautifulsoup4 tabulate

# Verify imports work
python -c "from data_ingestion.fundamentals import fetch_stock_data; print('✓ OK')"
```

#### 1.4 Initial Test Run
```bash
python main.py
```

**Success Criteria:**
- ✓ All data sources fetch successfully
- ✓ CSV files generated in outputs/
- ✓ No import errors
- ✓ Report displays in terminal

---

### 🏗️ PHASE 2: ARCHITECTURE REFINEMENT (Days 3-5)
**Goal:** Create a maintainable, extensible system

#### 2.1 Configuration Management
Create `config.yaml`:
```yaml
watchlist:
  - AAPL
  - MSFT
  - NVDA
  - TSLA
  - AMZN

data_sources:
  fundamentals:
    enabled: true
    provider: yfinance
    timeout: 30
  
  psycho:
    enabled: true
    vix_period: 6mo
    fear_greed_enabled: true
  
  social:
    enabled: true
    subreddits: [wallstreetbets, stocks, investing]
    posts_per_sub: 100
    sentiment_model: distilbert

scoring:
  fundamental:
    pe_threshold: 35
    pb_threshold: 10
    de_threshold: 15
    roe_threshold: 1
  
  weighting:
    fundamental_weight: 0.5
    psychological_weight: 0.3
    social_weight: 0.2
```

#### 2.2 Data Layer Abstraction
```python
# Create abstract data source interface
class DataSource:
    def fetch(self) -> pd.DataFrame:
        pass
    
    def validate(self) -> bool:
        pass

# Implement specific sources
class FundamentalsSource(DataSource):
    pass

class PsychoSource(DataSource):
    pass

class SocialSource(DataSource):
    pass
```

#### 2.3 Error Handling & Logging
```python
# Implement graceful degradation
try:
    fundamentals = fetch_fundamentals()
except APIError:
    logger.warning("Fundamentals fetch failed, using cached data")
    fundamentals = load_cached_fundamentals()

# Add structured logging
logger.info("fetch_start", {
    "source": "reddit",
    "subreddits": 3,
    "timestamp": datetime.now()
})
```

#### 2.4 Module Organization
```
C:\Hermes-1\
├── config/
│   ├── config.yaml
│   └── __init__.py
├── data_ingestion/
│   ├── __init__.py
│   ├── base.py           # Abstract DataSource
│   ├── fundamentals.py
│   ├── psycho.py
│   └── social.py
├── analytics/
│   ├── __init__.py
│   ├── scoring.py
│   ├── weighting.py      # NEW
│   └── validators.py     # NEW
├── outputs/
│   ├── reporter.py
│   ├── cache.py          # NEW
│   └── data/
│       └── *.csv
├── tests/
│   ├── __init__.py
│   ├── test_scoring.py
│   ├── test_social.py
│   └── fixtures/
├── utils/
│   ├── __init__.py
│   └── decorators.py     # Retry, timing, caching
├── main.py
├── config.yaml
├── requirements.txt
└── .env
```

---

### 🚀 PHASE 3: ENHANCED FEATURES (Days 6-10)
**Goal:** Add sophisticated analysis capabilities

#### 3.1 Technical Indicators
```python
# Add to analytics/
def calculate_rsi(prices, period=14) -> float:
    """Relative Strength Index"""
    pass

def calculate_macd(prices) -> dict:
    """Moving Average Convergence Divergence"""
    pass

def calculate_bollinger_bands(prices, period=20) -> dict:
    """Bollinger Bands"""
    pass
```

#### 3.2 Alternative Sentiment Sources
```python
# data_ingestion/news.py
class NewsAPISource(DataSource):
    """Financial news from NewsAPI, AlphaVantage, etc."""
    pass

# data_ingestion/twitter.py
class TwitterSentimentSource(DataSource):
    """X/Twitter sentiment analysis"""
    pass
```

#### 3.3 Visualization Dashboard
```python
# outputs/dashboard.py
import plotly.graph_objects as go

def create_dashboard():
    """Generate interactive HTML dashboard with:
    - Score breakdown by component
    - Historical trends
    - Sentiment heatmaps
    - Correlation matrices
    """
    pass
```

#### 3.4 Portfolio Recommendations
```python
# analytics/portfolio.py
def recommend_portfolio(scores: pd.DataFrame, 
                       budget: float,
                       risk_tolerance: str) -> pd.DataFrame:
    """Generate allocation recommendations"""
    pass
```

---

### 📊 PHASE 4: DATA & PERSISTENCE (Days 11-14)
**Goal:** Build enterprise-grade data infrastructure

#### 4.1 Database Integration
```python
# data_ingestion/persistence.py
class DataStore:
    def save_fundamentals(self, df: pd.DataFrame):
        # SQLAlchemy + PostgreSQL
        pass
    
    def load_historical(self, ticker: str, days: int):
        # Query time-series data
        pass
    
    def get_statistics(self, ticker: str, metric: str):
        # Aggregations and analytics
        pass
```

#### 4.2 Caching Strategy
```python
# utils/cache.py
@cache_result(ttl_minutes=60)
def fetch_fear_greed_index():
    """Cache for 1 hour"""
    pass

@cache_result(ttl_minutes=1440)  # 24 hours
def fetch_fundamentals(tickers):
    """Cache fundamental data daily"""
    pass
```

#### 4.3 Data Validation Pipeline
```python
# analytics/validators.py
def validate_score(score: float) -> bool:
    """Ensure score is 0-100"""
    return 0 <= score <= 100

def validate_sentiment(sentiment_data: dict) -> bool:
    """Validate sentiment counts"""
    return all(v >= 0 for v in sentiment_data.values())
```

---

### ⚙️ PHASE 5: AUTOMATION & DEPLOYMENT (Days 15-20)
**Goal:** Production-ready system with monitoring

#### 5.1 Scheduled Execution
```python
# jobs/scheduler.py
import schedule

# Run analyses on schedule
schedule.every().day.at("09:30").do(run_analysis)      # Morning
schedule.every().day.at("16:00").do(run_analysis)      # Close
schedule.every().week.monday.at("20:00").do(weekly_report)

while True:
    schedule.run_pending()
    time.sleep(60)
```

#### 5.2 Alerting System
```python
# notifications/alerts.py
def send_alert(ticker: str, alert_type: str, value: float):
    """Send alerts via:
    - Email
    - Slack
    - Discord
    - SMS (Twilio)
    """
    pass
```

#### 5.3 API Exposure
```python
# api/endpoints.py (FastAPI)
from fastapi import FastAPI

app = FastAPI()

@app.get("/scores")
def get_scores():
    """GET /scores -> Latest composite scores"""
    pass

@app.get("/ticker/{symbol}")
def get_ticker_data(symbol: str):
    """GET /ticker/AAPL -> Full ticker analysis"""
    pass

@app.get("/sentiment/{symbol}")
def get_sentiment(symbol: str):
    """GET /sentiment/AAPL -> Social sentiment breakdown"""
    pass
```

#### 5.4 CI/CD Pipeline
```yaml
# .github/workflows/analysis.yml
name: Daily Analysis
on:
  schedule:
    - cron: '0 9 * * MON-FRI'  # 9 AM weekdays

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run analysis
        run: python main.py
      - name: Upload results
        run: git push
```

---

## Implementation Roadmap

```
START (Week 1)
│
├─→ PHASE 1: Foundation Setup
│   ├─ Setup directories & config
│   ├─ Verify all imports work
│   └─ First successful end-to-end run
│
├─→ PHASE 2: Architecture Refactor
│   ├─ Extract configuration
│   ├─ Create abstractions
│   ├─ Improve error handling
│   └─ Add logging framework
│
├─→ PHASE 3: Feature Enhancement
│   ├─ Add technical indicators
│   ├─ New sentiment sources
│   ├─ Dashboard creation
│   └─ Portfolio recommendations
│
├─→ PHASE 4: Data Infrastructure
│   ├─ Database integration
│   ├─ Caching system
│   ├─ Validation layer
│   └─ Historical analytics
│
├─→ PHASE 5: Production Deployment
│   ├─ Scheduling system
│   ├─ Alerting framework
│   ├─ API exposure
│   └─ CI/CD pipeline
│
END (Week 5)
```

---

## Key Metrics to Optimize

### 1. **Score Accuracy**
- Historical backtesting
- Compare vs. actual stock performance
- Calibrate weights based on results

### 2. **Data Freshness**
- Update frequency (daily/hourly)
- Cache hit ratio
- API response times

### 3. **Sentiment Quality**
- Compare transformer vs. TextBlob
- Reddit post relevance filtering
- False positive rate

### 4. **System Reliability**
- Uptime % (target: 99.5%)
- Error rate < 1%
- API retry success rate > 95%

### 5. **Performance**
- Analysis runtime < 5 minutes
- Memory usage < 1GB
- Database query < 100ms

---

## Success Criteria by Phase

| Phase | Metric | Target |
|-------|--------|--------|
| 1 | Project runs end-to-end | ✓ First successful run |
| 2 | Code maintainability | 90%+ readable, documented |
| 3 | Feature coverage | All 5 data sources integrated |
| 4 | Data reliability | 99%+ availability |
| 5 | Deployment | Automated daily execution |

---

## Technical Stack Summary

### Languages & Frameworks
- **Python 3.9+** - Core language
- **FastAPI** - API layer (Phase 5)
- **Plotly** - Visualizations (Phase 3)
- **SQLAlchemy** - Database ORM (Phase 4)

### Data & APIs
- **yfinance** - Stock data
- **PRAW** - Reddit API
- **NewsAPI** - Financial news (Phase 3)
- **Selenium** - Web scraping
- **transformers** - NLP models

### Infrastructure
- **PostgreSQL** - Time-series data (Phase 4)
- **Redis** - Caching (Phase 4)
- **GitHub Actions** - CI/CD (Phase 5)
- **Docker** - Containerization (Phase 5)

---

## Questions for You

1. **Immediate Priority:** Start with Phase 1 (get it running) or Phase 2 (refactor structure)?

2. **Data Storage:** Prefer CSV files or database?

3. **API Credentials:** Do you have Reddit API credentials ready?

4. **Deployment Target:** Local machine, cloud (AWS/GCP), or both?

5. **Stakeholders:** Who will use this? (Personal, team, clients)

6. **Timeline:** Any deadline constraints?

---

## Next Action: Choose Your Path

Select one:

```
A) "Let's start Phase 1 - get everything running"
B) "Skip to Phase 2 - refactor the architecture" 
C) "Focus on Phase 3 - add more features"
D) "Jump to Phase 5 - automate and deploy"
E) "Fix specific issue X first"
```

Which path interests you most? 🚀


