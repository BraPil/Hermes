# 🎯 Watchlist Update Summary

**Updated:** November 14, 2025  
**Change Type:** Customization - Phase 1 Preparation  
**Status:** ✅ Complete

---

## 📊 Watchlist Changes

### Before
```
5 Assets (Default):
  AAPL
  MSFT
  NVDA
  TSLA
  AMZN
```

### After
```
16 Assets (Custom Portfolio):
  SQQQ    (Inverse Nasdaq-100)
  UVXY    (Inverse VIX)
  SPXU    (Inverse S&P 500)
  RNA     (Moderna - Biotech)
  DYN     (Dynamics)
  MSFT    (Microsoft)
  GOOGL   (Google)
  INTC    (Intel)
  AMD     (AMD)
  GLD     (Gold ETF)
  RGTI    (Rigetti Computing)
  QBTS    (D-Wave Systems)
  IONQ    (IonQ)
  QUBT    (Quantum Computing)
  QMCO    (Quantum Computing)
  BTC-USD (Bitcoin)
```

---

## 📁 Files Updated

### 1. **main.py** ✅
**Location:** `C:\Hermes\main.py`  
**Changes:**
- Lines 14-39: Updated `watchlist` and `tickers` lists
- Added comments describing each asset
- Maintained all functionality

**Before:**
```python
watchlist = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN']
tickers = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN']
```

**After:**
```python
# Custom watchlist: Quantum, inverse ETFs, tech, and BTC
watchlist = [
    'SQQQ', 'UVXY', 'SPXU', 'RNA', 'DYN',
    'MSFT', 'GOOGL', 'INTC', 'AMD', 'GLD',
    'RGTI', 'QBTS', 'IONQ', 'QUBT', 'QMCO',
    'BTC-USD'
]

tickers = [
    'SQQQ', 'UVXY', 'SPXU', 'RNA', 'DYN',
    'MSFT', 'GOOGL', 'INTC', 'AMD', 'GLD',
    'RGTI', 'QBTS', 'IONQ', 'QUBT', 'QMCO',
    'BTC-USD'
]
```

### 2. **README.md** ✅
**Location:** `C:\Hermes\README.md`  
**Changes:**
- Updated project description with new asset classes
- Reorganized by asset type (Inverse ETFs, Tech, Quantum, Other)

### 3. **QUICK_START.md** ✅
**Location:** `C:\Hermes\QUICK_START.md`  
**Changes:**
- Added new section: "Your Custom Watchlist"
- Documented all 16 assets with categories
- Added categorization and brief descriptions

### 4. **CUSTOM_WATCHLIST.md** ✅ (NEW)
**Location:** `C:\Hermes\CUSTOM_WATCHLIST.md`  
**Content:**
- Complete asset breakdown
- Special considerations for each asset type
- Scoring implications
- Reddit sentiment expectations
- Expected performance metrics
- Phase 1 execution notes

---

## 🎯 Asset Categories

### Inverse ETFs (3 assets) - Hedging
- SQQQ: 3x Inverse Nasdaq-100
- UVXY: Inverse VIX (Volatility)
- SPXU: 3x Inverse S&P 500

**Characteristics:**
- Negative correlation to markets
- Score HIGH when market DOWN
- Suitable for hedging positions

### Technology (4 assets) - Core Holdings
- MSFT: Microsoft
- GOOGL: Google/Alphabet
- INTC: Intel
- AMD: Advanced Micro Devices

**Characteristics:**
- Strong fundamentals
- High PE ratios (growth)
- Excellent Reddit sentiment

### Quantum Computing (5 assets) - Speculative/Emerging
- RGTI: Rigetti Computing
- QBTS: D-Wave Systems
- IONQ: IonQ
- QUBT: Quantum Computing Inc.
- QMCO: Quantum Computing

**Characteristics:**
- Early-stage companies
- Limited financial history
- High volatility
- Strong Reddit sentiment
- Scoring may be unreliable

### Other (4 assets) - Diversification
- RNA: Moderna (Biotech)
- DYN: Dynamics
- GLD: Gold ETF (Commodity)
- BTC-USD: Bitcoin (Crypto)

**Characteristics:**
- Different valuation logics
- Limited traditional metrics
- Diverse market exposure

---

## 📊 Expected Execution Changes

### Execution Time
| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Total Run Time | ~3 min | ~4-5 min | +33% |
| Fundamentals | 5 sec | 8 sec | +3 sec |
| Reddit Analysis | 90 sec | 140 sec | +50 sec |
| Other Components | 25 sec | 25 sec | No change |

**Reason:** 16 assets vs 5 assets = 3.2x more tickers to process

### Output Changes
| File | Before | After | Change |
|------|--------|-------|--------|
| fundamentals_scored.csv | 5 rows | 16 rows | +11 rows |
| weighted_score.csv | 5 rows | 16 rows | +11 rows |
| social_sentiment_log.csv | 5 rows | 16 rows | +11 rows |
| fear_greed_log.csv | 1 entry | 1 entry | No change |
| vix_sp500_data.csv | 1 dataset | 1 dataset | No change |

---

## ⚠️ Important Notes

### 1. **Inverse ETFs Behavior**
These assets are designed to move opposite to the market:
- When market UP, they score LOW (expected)
- When market DOWN, they score HIGH (expected)
- 3x leverage means multiplied movements
- May experience decay on sideways markets

### 2. **BTC-USD Has No Fundamentals**
Bitcoin scoring will be limited because:
- No P/E ratio (not a company)
- No D/E ratio (no debt)
- No ROE (not a company)
- Fundamentals score will be artificially low
- Reddit sentiment becomes primary signal

### 3. **Quantum Stocks May Have Missing Data**
Early-stage companies may lack:
- Historical earnings data
- Complete financial metrics
- Established fundamentals
- System will degrade gracefully (skip missing metrics)

### 4. **More Reddit Mentions = More Sentiment Data**
- ✅ Quantum stocks: Very active subreddits
- ✅ BTC-USD: Massive crypto community
- ✅ Tech stocks: Popular on r/stocks, r/technology
- ⚠️ Inverse ETFs: Minimal discussion
- ⚠️ DYN: Possibly sparse data

---

## ✅ Verification Checklist

After Phase 1 runs with custom watchlist:

- [ ] All 16 assets processed without errors
- [ ] 5 CSV files generated
- [ ] fundamentals_scored.csv has 16 rows
- [ ] weighted_score.csv has 16 rows
- [ ] Scores range: 0-100
- [ ] Tech stocks (MSFT, GOOGL) score 60-80
- [ ] Inverse ETFs score LOW (when market up)
- [ ] Quantum stocks have mixed scores
- [ ] BTC-USD has sentiment data
- [ ] No catastrophic errors (graceful degradation)

---

## 🔄 How to Modify Watchlist Further

### To Add More Assets
Edit `C:\Hermes\main.py` lines 15-39:

```python
watchlist = [
    'SQQQ', 'UVXY', 'SPXU',
    'RNA', 'DYN', 'MSFT', 'GOOGL', 'INTC', 'AMD',
    'GLD', 'RGTI', 'QBTS', 'IONQ', 'QUBT', 'QMCO',
    'BTC-USD',
    'NEW_TICKER'  # Add here
]

tickers = [
    'SQQQ', 'UVXY', 'SPXU',
    'RNA', 'DYN', 'MSFT', 'GOOGL', 'INTC', 'AMD',
    'GLD', 'RGTI', 'QBTS', 'IONQ', 'QUBT', 'QMCO',
    'BTC-USD',
    'NEW_TICKER'  # Add here
]
```

### To Remove Assets
Simply delete the ticker from both lists.

### To Revert to Defaults
```python
watchlist = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN']
tickers = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN']
```

---

## 📋 Phase 1 with Custom Watchlist

You're now ready to proceed with Phase 1 using your custom portfolio:

### Quick Start (Same as Before)
```bash
cd C:\Hermes

# Step 1: Create .env file (manual)
# Step 2: Create outputs directory
mkdir outputs

# Step 3: Install dependencies
pip install -r requirements.txt
pip install yfinance selenium webdriver-manager beautifulsoup4 tabulate

# Step 4: Run analysis with 16 assets
python main.py

# Step 5: Check results
dir outputs\
type outputs\weighted_score.csv
```

### Expected Output
```
MSFT,72.5       ← Tech, strong
GOOGL,70.1      ← Tech, strong
BTC-USD,65.2    ← Crypto, sentiment
AMD,68.4        ← Tech, good
INTC,62.3       ← Tech, decent
IONQ,58.3       ← Quantum, sentiment
QBTS,52.1       ← Quantum
RNA,55.7        ← Biotech
GLD,48.2        ← Commodity
RGTI,45.0       ← Quantum early-stage
QUBT,42.8       ← Quantum early-stage
QMCO,40.1       ← Quantum early-stage
DYN,35.4        ← Limited data
SQQQ,32.1       ← Inverse (scores low by design)
UVXY,28.5       ← Inverse VIX
SPXU,25.3       ← Inverse S&P
```

---

## 🎯 Next Steps

1. ✅ Watchlist customized
2. ⏳ Phase 1.1: Create `.env` file
3. ⏳ Phase 1.2: Create `outputs/` directory
4. ⏳ Phase 1.3: Install dependencies
5. ⏳ Phase 1.4: Verify imports
6. ⏳ Phase 1.5: Run analysis
7. ⏳ Phase 1.6: Validate outputs

---

**Status:** ✅ Ready for Phase 1 Execution  
**Total Assets:** 16 (from 5)  
**Execution Time:** ~4-5 min (from ~3 min)  
**Complexity:** High (diverse asset classes)  

Let's proceed! 🚀


