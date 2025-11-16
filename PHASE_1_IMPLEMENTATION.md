# 🚀 PHASE 1: FOUNDATION SETUP & LAUNCH

**Duration:** 2-3 days  
**Goal:** Get the project running end-to-end with proper environment setup  
**Status:** 🔴 In Progress

---

## 📋 Phase 1 Checklist

### 1.1 Environment Setup ✅
- [x] Identify working codebase (C:\Hermes-1 → Consolidated to C:\Hermes)
- [x] Create comprehensive documentation (6 guides)
- [ ] Create `.env` file with Reddit credentials
- [ ] Create `outputs/` directory
- [ ] Verify `requirements.txt` has all dependencies

### 1.2 Dependency Verification ⏳
- [ ] Install base requirements: `pip install -r requirements.txt`
- [ ] Install implicit dependencies (yfinance, selenium, webdriver-manager, beautifulsoup4, tabulate)
- [ ] Verify all imports work: `python -c "from data_ingestion.fundamentals import fetch_stock_data"`
- [ ] Test sentiment pipeline initialization

### 1.3 Initial Test Run ⏳
- [ ] Run end-to-end analysis: `python main.py`
- [ ] Check all 5 CSV outputs are created
- [ ] Verify no import errors
- [ ] Verify no runtime errors
- [ ] Display terminal report

### 1.4 Data Validation ⏳
- [ ] Verify fundamentals_scored.csv has valid scores (0-70)
- [ ] Verify weighted_score.csv has valid scores (0-100)
- [ ] Verify social_sentiment_log.csv has sentiment data
- [ ] Verify fear_greed_log.csv has index reading
- [ ] Verify vix_sp500_data.csv has market data

### 1.5 Documentation Update ⏳
- [ ] Update README.md with success confirmation
- [ ] Document any workarounds needed
- [ ] Create troubleshooting notes

---

## 🔧 STEP 1: Create Environment Configuration

### 1.1a Create `.env` File

**Location:** `C:\Hermes\.env`

```
REDDIT_CLIENT_ID=your_reddit_app_id_here
REDDIT_CLIENT_SECRET=your_reddit_app_secret_here
REDDIT_USER_AGENT=YourUsername/1.0 (+http://example.com/r/investing)
```

**How to get credentials:**
1. Visit https://www.reddit.com/prefs/apps
2. Click "Create an application"
3. Fill form:
   - Name: "Hermes Stock Analysis"
   - Type: Select "script"
   - Redirect URI: http://localhost:8000
4. Copy:
   - `client_id` → REDDIT_CLIENT_ID
   - `client_secret` → REDDIT_CLIENT_SECRET
   - Create user agent: `YourUsername/1.0`

**Status:** ⏳ Ready to implement

### 1.1b Create `outputs/` Directory

```bash
cd C:\Hermes
mkdir outputs
```

**Status:** ⏳ Ready to implement

### 1.1c Copy Historical Data (Optional)

If outputs/ already exists in C:\Hermes (from previous runs):
```bash
# Data should already be there - verify:
dir C:\Hermes\outputs\
```

Expected files:
- fear_greed_log.csv
- fundamentals_data.csv
- fundamentals_scored.csv
- social_sentiment_log.csv
- vix_sp500_data.csv
- weighted_score.csv
- report_generator.py
- weighted_score.py

---

## 📦 STEP 2: Dependency Installation

### 2.1 Core Requirements

```bash
cd C:\Hermes
pip install -r requirements.txt
```

**Current requirements.txt:**
```
praw==7.7.1
textblob==0.17.1
pandas==2.1.4
python-dotenv==1.0.0
transformers==4.36.2
torch==2.1.2
```

**Status:** ⏳ Ready to implement

### 2.2 Implicit Dependencies

These are used but not listed. Install them:

```bash
pip install yfinance selenium webdriver-manager beautifulsoup4 tabulate
```

**Versions (recommended):**
```
yfinance==0.2.32
selenium==4.15.2
webdriver-manager==4.0.1
beautifulsoup4==4.12.2
tabulate==0.9.0
```

**Status:** ⏳ Ready to implement

### 2.3 Verify Imports

Test each module imports correctly:

```bash
# Test 1: Fundamentals
python -c "from data_ingestion.fundamentals import fetch_stock_data; print('✓ Fundamentals OK')"

# Test 2: Psycho
python -c "from data_ingestion.psycho import fetch_vix_and_sp500_data, fetch_fear_greed_index; print('✓ Psycho OK')"

# Test 3: Social
python -c "from data_ingestion.social import RedditSentimentAnalyzer; print('✓ Social OK')"

# Test 4: Analytics
python -c "from analytics.scoring import calculate_score; print('✓ Analytics OK')"

# Test 5: Output
python -c "from outputs.report_generator import generate_report; print('✓ Outputs OK')"
```

**Expected output:**
```
✓ Fundamentals OK
✓ Psycho OK
✓ Social OK
✓ Analytics OK
✓ Outputs OK
```

**Status:** ⏳ Ready to implement

---

## 🧪 STEP 3: Initial Test Run

### 3.1 Single Stock Test (Fast)

For faster initial testing, edit `main.py`:

**Before:**
```python
watchlist = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN']
tickers = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN']
```

**After (temporary for testing):**
```python
watchlist = ['AAPL']  # Test with just one stock
tickers = ['AAPL']
```

**Then run:**
```bash
cd C:\Hermes
python main.py
```

**Expected output (streaming):**
```
Scoring AAPL
Adding 20 for trailingPE
Adding 15 for priceToBook
Adding 20 for debtToEquity
Adding 15 for returnOnEquity
Fetched VIX and SP500 data for 6mo
Fetched Fear & Greed Index Score: 65
...
[Final report table]
```

**Execution time:** ~1-2 minutes (Reddit is skipped for social sentiment)

**Status:** ⏳ Ready to implement

### 3.2 Full Run (All 5 Stocks + Reddit)

**Restore main.py:**
```python
watchlist = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN']
tickers = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN']
```

**Then run:**
```bash
cd C:\Hermes
python main.py
```

**Expected time:** 2-4 minutes

**Expected output files:**
```
C:\Hermes\outputs\
├── fundamentals_scored.csv
├── vix_sp500_data.csv
├── fear_greed_log.csv
├── social_sentiment_log.csv
├── weighted_score.csv
└── [Terminal report output]
```

**Status:** ⏳ Ready to implement

---

## ✅ STEP 4: Validation

### 4.1 CSV File Validation

**fundamentals_scored.csv**
- [ ] Contains 5 rows (one per stock)
- [ ] Columns: ticker, longName, sector, marketCap, trailingPE, forwardPE, pegRatio, priceToBook, debtToEquity, returnOnEquity, score
- [ ] Score column: All values 0-70
- [ ] Example: AAPL should have score ~60-70 (good fundamentals)

**weighted_score.csv**
- [ ] Contains 5 rows
- [ ] Columns: ticker, weighted_score
- [ ] Scores: 0-100 range
- [ ] Multiplier applied based on Fear & Greed Index

**social_sentiment_log.csv**
- [ ] Contains data for stocks mentioned
- [ ] Columns: ticker, POSITIVE, NEGATIVE, NEUTRAL, sentiment_score, etc.
- [ ] Timestamp shows current date/time

**fear_greed_log.csv**
- [ ] New row appended (or new file if first run)
- [ ] Columns: date, fear_greed_score
- [ ] Score: 0-100 scale
- [ ] Date: Today's date/time

**vix_sp500_data.csv**
- [ ] Multiple rows (6 months of daily data)
- [ ] Columns: Date, VIX_Close, SP500_Close
- [ ] Values reasonable (VIX: 10-50, SP500: 4000-6000)

**Status:** ⏳ Ready to implement

### 4.2 Performance Metrics

Track these:
- [ ] Total execution time (target: 2-4 min)
- [ ] Components breakdown:
  - [ ] Fundamentals: ~5 sec
  - [ ] VIX/S&P: ~8 sec
  - [ ] Fear & Greed: ~15 sec
  - [ ] Reddit: ~90-120 sec
  - [ ] Scoring: ~5 sec
  - [ ] Report: ~5 sec

**Status:** ⏳ Ready to implement

---

## 🐛 STEP 5: Troubleshooting

### Expected Issues & Solutions

**Issue:** ModuleNotFoundError: No module named 'outputs'
```
Solution: 
- Copy report_generator.py from outputs/ directory
- If not present, create outputs/report_generator.py with report display logic
```

**Issue:** REDDIT_CLIENT_ID not found
```
Solution:
- Create .env file with Reddit credentials
- Ensure it's in C:\Hermes\ directory
- Restart Python environment to reload env vars
```

**Issue:** ChromeDriver not found
```
Solution:
- pip install webdriver-manager
- This auto-downloads ChromeDriver
```

**Issue:** Connection timeout (yfinance/Reddit)
```
Solution:
- Check internet connection
- If APIs are down, retry later
- System has retry logic built-in
```

**Issue:** Reddit rate limit hit
```
Solution:
- Wait 5 minutes
- Retry later
- System gracefully degrades without Reddit data
```

---

## 📊 Success Criteria

Phase 1 is complete when:

✅ `.env` file created with Reddit credentials  
✅ `outputs/` directory created  
✅ All requirements installed  
✅ All imports verified successfully  
✅ `python main.py` runs without errors  
✅ 5 CSV files generated in `outputs/`  
✅ Terminal report displays properly  
✅ Scores are reasonable (0-100 range)  
✅ Execution time documented (~3 min)  

---

## 📝 Implementation Instructions

### To Start Phase 1:

1. **Create .env file**
   - Follow section 1.1a above
   - Add your Reddit credentials

2. **Create outputs directory**
   ```bash
   mkdir C:\Hermes\outputs
   ```

3. **Install dependencies**
   ```bash
   cd C:\Hermes
   pip install -r requirements.txt
   pip install yfinance selenium webdriver-manager beautifulsoup4 tabulate
   ```

4. **Verify imports**
   ```bash
   python -c "from data_ingestion.fundamentals import fetch_stock_data; print('✓ OK')"
   ```

5. **Run initial test**
   ```bash
   python main.py
   ```

6. **Validate outputs**
   - Check outputs/ directory for 5 CSV files
   - Verify content matches expected format
   - Document any issues

---

## 🎯 Next: After Phase 1

Once Phase 1 is complete and system is running:

**Phase 2 Goals:**
- Add error handling for API failures
- Implement caching for repeated calls
- Create configuration file (config.yaml)
- Add type hints to functions
- Create unit tests

**Timeline:** 3-5 days

---

## 📌 Notes

- Reddit sentiment analysis is optional - system works without it
- First run will download sentiment models (may take extra time)
- Historical data in outputs/ persists across runs
- System gracefully degrades if one data source fails

---

## ✨ You're Ready!

**Start implementing Phase 1 now:**

```bash
cd C:\Hermes
# 1. Create .env (manual)
# 2. Create outputs directory
mkdir outputs
# 3. Install dependencies
pip install -r requirements.txt
pip install yfinance selenium webdriver-manager beautifulsoup4 tabulate
# 4. Run analysis
python main.py
```

Let me know when Phase 1 is complete! 🚀


