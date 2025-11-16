# 🚀 PHASES 1, 2, & 3 MASTER IMPLEMENTATION PLAN

**Timeline:** 10-18 days  
**Goal:** Build from working MVP → production-ready architecture → advanced features  
**Status:** 🔴 Starting Phase 1

---

## 📊 Overview

```
PHASE 1 (2-3 days)     PHASE 2 (3-5 days)     PHASE 3 (5-10 days)
─────────────────────  ──────────────────────  ──────────────────────
Foundation Setup       Architecture Refactor   Feature Enhancement
✓ Environment Setup    ✓ Configuration Mgmt    ✓ Technical Indicators
✓ Test Run Success     ✓ Error Handling        ✓ News/Twitter Sentiment
✓ Data Validation      ✓ Caching System       ✓ Visualization
✓ All Imports Work     ✓ Type Hints            ✓ Portfolio Optimizer
                       ✓ Unit Tests
```

---

## 🎯 PHASE 1: FOUNDATION SETUP (2-3 Days)

**Goal:** Get the complete pipeline running end-to-end  
**Success Metric:** `python main.py` runs successfully, generates 5 CSV files

### 1.1 Environment Configuration
```
Deliverables:
□ .env file with Reddit credentials
□ outputs/ directory created
□ requirements.txt validated
□ All imports verified

Time: ~30 minutes
```

**Checklist:**
- [ ] Create `C:\Hermes\.env`
- [ ] Add REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
- [ ] Run: `mkdir C:\Hermes\outputs`
- [ ] Run: `pip install -r requirements.txt`
- [ ] Run: `pip install yfinance selenium webdriver-manager beautifulsoup4 tabulate`

### 1.2 Dependency Verification
```
Deliverables:
□ All imports pass
□ Sentiment model downloads successfully
□ Reddit client initializes
□ Web scraper works

Time: ~15 minutes
```

**Test Commands:**
```bash
python -c "from data_ingestion.fundamentals import fetch_stock_data; print('✓')"
python -c "from data_ingestion.psycho import fetch_vix_and_sp500_data; print('✓')"
python -c "from data_ingestion.social import RedditSentimentAnalyzer; print('✓')"
python -c "from analytics.scoring import calculate_score; print('✓')"
python -c "from outputs.report_generator import generate_report; print('✓')"
```

### 1.3 Test Run
```
Deliverables:
□ Single-stock test passes
□ Full 5-stock run completes
□ All 5 CSV files generated
□ Report displays correctly

Time: ~3-5 minutes per run
```

**Single Stock Test:**
```bash
# Edit main.py: watchlist = ['AAPL'], tickers = ['AAPL']
python main.py
# Expected: 1-2 minutes
```

**Full Run:**
```bash
# Edit main.py: restore full watchlist
python main.py
# Expected: 2-4 minutes
```

### 1.4 Output Validation
```
Deliverables:
□ fundamentals_scored.csv: Valid data, scores 0-70
□ weighted_score.csv: Final scores 0-100
□ social_sentiment_log.csv: Reddit data or empty gracefully
□ fear_greed_log.csv: Index reading appended
□ vix_sp500_data.csv: 6 months market data

Time: ~10 minutes
```

**Validation Script:**
```bash
# Check file sizes and formats
dir C:\Hermes\outputs\*.csv
# Open each file and verify structure
```

### 1.5 Success Checklist
- [x] `.env` file created with credentials
- [x] `outputs/` directory exists
- [x] All dependencies installed
- [x] All imports verify
- [x] `python main.py` runs without errors
- [x] 5 CSV files generated
- [x] Scores are valid (0-100 range)
- [x] Execution time: ~3 min

---

## 🏗️ PHASE 2: ARCHITECTURE REFACTOR (3-5 Days)

**Goal:** Make code production-ready with error handling, configuration, and tests  
**Success Metric:** Code is modular, testable, and resilient

### 2.1 Configuration Management
```
Deliverables:
□ config.yaml file
□ Load config on startup
□ Watchlist configurable
□ Thresholds adjustable
□ API timeouts configurable

Time: ~6-8 hours (1 day)
```

**Create `C:\Hermes\config.yaml`:**
```yaml
project:
  name: Hermes
  version: 1.0.0

watchlist:
  - AAPL
  - MSFT
  - NVDA
  - TSLA
  - AMZN

data_sources:
  fundamentals:
    enabled: true
    timeout: 30
  
  psycho:
    enabled: true
    vix_period: 6mo
    fear_greed_enabled: true
  
  social:
    enabled: true
    subreddits: [wallstreetbets, stocks, investing]
    posts_per_sub: 100

scoring:
  fundamental:
    pe_threshold: 35
    pb_threshold: 10
    de_threshold: 15
    roe_threshold: 1
    weights:
      pe: 20
      pb: 15
      de: 20
      roe: 15
  
  psychological_weighting:
    enabled: true
    bullish_multiplier_max: 1.4
    bearish_multiplier_min: 0.6
```

**Update `main.py`:**
```python
import yaml

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

watchlist = config['watchlist']
# Use config throughout
```

### 2.2 Error Handling & Resilience
```
Deliverables:
□ Try/catch for each data source
□ Graceful degradation if APIs fail
□ Retry logic with backoff
□ Meaningful error logging
□ System works with partial data

Time: ~8-10 hours (1-2 days)
```

**Pattern to implement:**
```python
def fetch_with_retry(func, max_retries=3, timeout=30):
    """Retry wrapper with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.warning(f"Attempt {attempt+1} failed, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
            else:
                logger.error(f"All {max_retries} attempts failed: {e}")
                return None
```

**Update `main.py` error handling:**
```python
try:
    fundamentals = fetch_stock_data(tickers)
except Exception as e:
    logger.warning(f"Fundamentals fetch failed: {e}")
    fundamentals = load_cached_data('fundamentals')  # Fallback

try:
    psycho_data = fetch_vix_and_sp500_data()
except Exception as e:
    logger.warning(f"Psycho data fetch failed: {e}")
    psycho_data = None  # Will skip this component
```

### 2.3 Caching System
```
Deliverables:
□ Cache results to disk
□ TTL-based cache expiration
□ Cache invalidation strategy
□ Faster subsequent runs

Time: ~6-8 hours (1 day)
```

**Create `C:\Hermes\utils\cache.py`:**
```python
import json
import time
from pathlib import Path

class FileCache:
    def __init__(self, cache_dir='./cache'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def get(self, key, ttl_seconds=None):
        """Get from cache if exists and not expired"""
        cache_file = self.cache_dir / f"{key}.json"
        if not cache_file.exists():
            return None
        
        data = json.loads(cache_file.read_text())
        if ttl_seconds and time.time() - data['timestamp'] > ttl_seconds:
            cache_file.unlink()
            return None
        
        return data['value']
    
    def set(self, key, value):
        """Save to cache"""
        cache_file = self.cache_dir / f"{key}.json"
        json.dump({'value': value, 'timestamp': time.time()}, cache_file.open('w'))
```

### 2.4 Type Hints
```
Deliverables:
□ All functions have type hints
□ Return types specified
□ Type checking enabled
□ Better IDE support

Time: ~4-6 hours (1 day)
```

**Before:**
```python
def calculate_score(stock):
    # ...
    return score
```

**After:**
```python
from typing import Dict, Optional
import pandas as pd

def calculate_score(stock: Dict[str, float]) -> float:
    """Calculate fundamental score for a stock.
    
    Args:
        stock: Dictionary with stock metrics
    
    Returns:
        Score between 0 and 70
    """
    # ...
    return score
```

### 2.5 Unit Tests
```
Deliverables:
□ Test scoring logic
□ Test sentiment analysis
□ Test data validation
□ Test error handling
□ >80% code coverage

Time: ~8-12 hours (1-2 days)
```

**Create `C:\Hermes\tests\test_scoring.py`:**
```python
import pytest
from analytics.scoring import calculate_score

def test_score_with_good_fundamentals():
    stock = {
        'ticker': 'AAPL',
        'trailingPE': 28,
        'priceToBook': 8,
        'debtToEquity': 1.5,
        'returnOnEquity': 100
    }
    score = calculate_score(stock)
    assert 60 <= score <= 70, "Good stock should score 60-70"

def test_score_with_bad_fundamentals():
    stock = {
        'ticker': 'XYZ',
        'trailingPE': 50,
        'priceToBook': 20,
        'debtToEquity': 50,
        'returnOnEquity': 0.5
    }
    score = calculate_score(stock)
    assert score == 0, "Bad stock should score 0"
```

**Run tests:**
```bash
pip install pytest
pytest tests/ -v --cov=.
```

---

## 🚀 PHASE 3: FEATURE ENHANCEMENT (5-10 Days)

**Goal:** Add sophisticated analysis capabilities  
**Success Metric:** System provides deeper insights and visualizations

### 3.1 Technical Indicators
```
Deliverables:
□ RSI (Relative Strength Index)
□ MACD (Moving Average Convergence Divergence)
□ Bollinger Bands
□ Moving averages (20, 50, 200-day)
□ Store in new CSV: technical_indicators.csv

Time: ~8-10 hours (1-2 days)
```

**Create `C:\Hermes\analytics\technical_indicators.py`:**
```python
import numpy as np
import pandas as pd

def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
    """Calculate Relative Strength Index"""
    deltas = np.diff(prices)
    seed = deltas[:period+1]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = 100. - 100. / (1. + rs)
    return rsi

def calculate_macd(prices: pd.Series) -> Dict[str, float]:
    """Calculate MACD"""
    exp1 = prices.ewm(span=12, adjust=False).mean()
    exp2 = prices.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    return {
        'macd': macd.iloc[-1],
        'signal': signal.iloc[-1],
        'histogram': (macd - signal).iloc[-1]
    }

def calculate_bollinger_bands(prices: pd.Series, period: int = 20) -> Dict[str, float]:
    """Calculate Bollinger Bands"""
    sma = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    return {
        'upper': sma.iloc[-1] + (std.iloc[-1] * 2),
        'middle': sma.iloc[-1],
        'lower': sma.iloc[-1] - (std.iloc[-1] * 2)
    }
```

### 3.2 Alternative Sentiment Sources
```
Deliverables:
□ Financial news API integration
□ Twitter/X sentiment analysis
□ Aggregate multiple sources
□ Weight by recency & reliability

Time: ~10-12 hours (1-2 days)
```

**Create `C:\Hermes\data_ingestion\news.py`:**
```python
import requests
from typing import List, Dict
import pandas as pd

class NewsAPISource:
    """Fetch financial news from NewsAPI"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2/everything"
    
    def fetch_news(self, ticker: str, days: int = 7) -> List[Dict]:
        """Fetch recent news about stock"""
        query = f"{ticker} stock market"
        params = {
            'q': query,
            'sortBy': 'relevancy',
            'language': 'en',
            'apiKey': self.api_key
        }
        response = requests.get(self.base_url, params=params)
        return response.json().get('articles', [])
```

### 3.3 Visualization Dashboard
```
Deliverables:
□ HTML dashboard with multiple charts
□ Score breakdown by component
□ Historical trends over time
□ Heatmaps for correlations
□ Portfolio performance chart

Time: ~12-16 hours (2-3 days)
```

**Create `C:\Hermes\outputs\dashboard.py`:**
```python
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def create_dashboard(fundamentals_df, sentiment_df, fear_greed_history):
    """Generate interactive HTML dashboard"""
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Score Distribution", "Sentiment Breakdown", 
                       "Fear & Greed History", "Technical Indicators")
    )
    
    # Score distribution
    fig.add_trace(
        go.Bar(x=fundamentals_df['ticker'], y=fundamentals_df['score']),
        row=1, col=1
    )
    
    # Sentiment heatmap
    fig.add_trace(
        go.Heatmap(z=sentiment_df[['POSITIVE', 'NEGATIVE', 'NEUTRAL']].values),
        row=1, col=2
    )
    
    # Fear & Greed trend
    fig.add_trace(
        go.Scatter(x=fear_greed_history['date'], 
                   y=fear_greed_history['fear_greed_score']),
        row=2, col=1
    )
    
    fig.update_layout(height=800, showlegend=False)
    fig.write_html("outputs/dashboard.html")
    print("Dashboard saved to outputs/dashboard.html")
```

### 3.4 Portfolio Recommendation Engine
```
Deliverables:
□ Portfolio allocation algorithm
□ Risk-return optimization
□ Diversification scoring
□ Generate buy/hold/sell signals

Time: ~10-12 hours (1-2 days)
```

**Create `C:\Hermes\analytics\portfolio.py`:**
```python
from typing import Dict, List
import pandas as pd
import numpy as np

def recommend_portfolio(
    scores: pd.DataFrame,
    budget: float = 10000,
    risk_tolerance: str = 'moderate'
) -> pd.DataFrame:
    """Generate portfolio allocation recommendations
    
    Args:
        scores: DataFrame with ticker and weighted_score
        budget: Total investment amount
        risk_tolerance: 'conservative', 'moderate', 'aggressive'
    
    Returns:
        DataFrame with ticker, allocation%, and dollar amount
    """
    
    # Normalize scores to allocation percentages
    scores['allocation_pct'] = scores['weighted_score'] / scores['weighted_score'].sum()
    
    # Apply risk tolerance adjustment
    if risk_tolerance == 'conservative':
        scores['allocation_pct'] *= 0.7  # Reduce volatility
    elif risk_tolerance == 'aggressive':
        scores['allocation_pct'] *= 1.2  # Increase exposure
    
    # Normalize again to sum to 100%
    scores['allocation_pct'] /= scores['allocation_pct'].sum()
    
    # Calculate dollar amounts
    scores['amount'] = scores['allocation_pct'] * budget
    
    return scores[['ticker', 'allocation_pct', 'amount']]
```

---

## 📅 IMPLEMENTATION SCHEDULE

### Week 1: Phase 1 (Foundation)
```
Day 1: Environment Setup
  ├─ Create .env file
  ├─ Create outputs/ directory
  ├─ Install dependencies
  └─ Verify imports

Day 2: Test Run
  ├─ Single-stock test
  ├─ Full 5-stock run
  └─ Validate outputs

Day 3 (Optional): Troubleshooting & Optimization
  ├─ Fix any issues
  ├─ Optimize performance
  └─ Document setup process
```

### Week 1-2: Phase 2 (Architecture)
```
Day 4: Configuration
  ├─ Create config.yaml
  ├─ Update main.py to use config
  └─ Test with different configurations

Day 5-6: Error Handling & Caching
  ├─ Implement try/catch blocks
  ├─ Add caching system
  ├─ Add retry logic
  └─ Test failure scenarios

Day 7-8: Type Hints & Testing
  ├─ Add type hints to all functions
  ├─ Create unit tests
  ├─ Achieve >80% code coverage
  └─ Document test cases
```

### Week 2-3: Phase 3 (Features)
```
Day 9-10: Technical Indicators
  ├─ Implement RSI, MACD, Bollinger Bands
  ├─ Calculate moving averages
  ├─ Add to scoring algorithm
  └─ Generate technical_indicators.csv

Day 11-12: Alternative Sentiment
  ├─ Integrate news API
  ├─ Add Twitter sentiment (if available)
  ├─ Combine with Reddit sentiment
  └─ Test with multiple sources

Day 13-15: Dashboard & Portfolio
  ├─ Create visualization dashboard
  ├─ Add portfolio recommendation engine
  ├─ Generate HTML report
  └─ Test with sample portfolios
```

---

## 🎯 Success Metrics

### Phase 1 Success
- ✅ System runs end-to-end
- ✅ All 5 stocks analyzed
- ✅ 5 CSV files generated
- ✅ Scores valid (0-100)
- ✅ Execution: ~3 minutes

### Phase 2 Success
- ✅ Code is modular and testable
- ✅ Configuration file working
- ✅ Error handling + graceful degradation
- ✅ Caching working (2nd run faster)
- ✅ >80% test coverage
- ✅ Type hints on all functions

### Phase 3 Success
- ✅ Technical indicators calculated
- ✅ Multiple sentiment sources integrated
- ✅ Interactive dashboard generated
- ✅ Portfolio recommendations provided
- ✅ New CSV files: technical_indicators.csv, portfolio_recommendations.csv

---

## 🚀 Getting Started

**Start Phase 1 now:**

```bash
cd C:\Hermes

# Step 1: Create .env (manual editor needed)
# Add: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT

# Step 2: Create outputs directory
mkdir outputs

# Step 3: Install dependencies
pip install -r requirements.txt
pip install yfinance selenium webdriver-manager beautifulsoup4 tabulate

# Step 4: Test single stock
python main.py

# Step 5: Check outputs
dir outputs\
```

**Phase 1 Complete When:** ✓ All 5 CSV files generated successfully

---

## 📝 Progress Tracking

Update these docs as you complete each phase:
- [ ] Phase 1 Complete: Date ___________
- [ ] Phase 2 Complete: Date ___________
- [ ] Phase 3 Complete: Date ___________

---

**Next Action:** Start Phase 1 implementation! 🚀


