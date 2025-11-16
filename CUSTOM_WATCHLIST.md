# 🎯 Custom Watchlist Configuration

**Updated:** November 14, 2025  
**Total Assets:** 16  
**Portfolio Type:** Diversified (Tech, Quantum, Inverse ETFs, Commodities, Crypto)

---

## 📊 Asset Breakdown

### Inverse ETFs (3) - Hedging/Bearish Plays
```
SQQQ    Inverse Nasdaq-100 (3x leverage)
UVXY    Inverse VIX / Volatility ETF  
SPXU    Inverse S&P 500 (3x leverage)
```
**Purpose:** Hedge against market downturns  
**Behavior:** Negative correlation to market - score high when markets fall

### Technology (4) - Blue Chip Growth
```
MSFT    Microsoft
GOOGL   Google/Alphabet
INTC    Intel
AMD     Advanced Micro Devices
```
**Purpose:** Core tech exposure  
**Behavior:** Fundamentals-driven, typically higher PE ratios

### Quantum Computing (5) - Speculative/Emerging
```
RGTI    Rigetti Computing
QBTS    D-Wave Systems
IONQ    IonQ
QUBT    Quantum Computing Inc.
QMCO    Quantum Computing
```
**Purpose:** Exposure to emerging quantum technology  
**Behavior:** Highly volatile, small cap, may have limited historical data

### Other (4)
```
RNA     Moderna (Biotech/Pharma)
DYN     Dynamics
GLD     Gold ETF (Commodity)
BTC-USD Bitcoin (Cryptocurrency)
```

---

## ⚠️ Special Considerations

### 1. **Inverse ETFs (SQQQ, UVXY, SPXU)**
These move opposite to market direction:
- **SQQQ & SPXU:** 3x inverse leverage = multiplied movements
- **May have decay** on sideways/up markets
- **Scoring note:** When market UP, these score LOW (expected)
- **Use case:** Portfolio hedging, not long-term holds

### 2. **Quantum Computing Stocks (RGTI, QBTS, IONQ, QUBT, QMCO)**
Emerging/speculative sector:
- **Limited financial history** → Some metrics may be N/A
- **High volatility** → Larger score swings
- **Reddit sentiment critical** → Key indicator for these
- **Fundamental scoring may be unreliable** for early-stage companies

### 3. **BTC-USD**
Cryptocurrency, different asset class:
- **No fundamentals** (no P/E, ROE, D/E) → Scoring may be limited
- **24/7 trading** → Different market dynamics
- **Highly volatile** → Large sentiment swings
- **Reddit mentions abundant** → Good social signal

### 4. **GLD (Gold ETF)**
Commodity exposure:
- **Limited fundamentals** → Different valuation approach
- **Safe haven asset** → Often inverse to equity risk appetite
- **Lower volatility** → Steady scores

### 5. **DYN & RNA**
- **DYN:** Lesser-known stock → May have limited data
- **RNA:** Biotech/Pharma → Results-driven, binary events

---

## 🧮 Scoring Implications

### Expected Score Ranges by Asset Type

| Type | Expected Score | Note |
|------|---|---|
| Quantum (RGTI, QBTS, etc.) | 20-60 | Volatile, early stage |
| Tech (MSFT, GOOGL, etc.) | 40-80 | Stable, high PE likely |
| Inverse ETFs (SQQQ, etc.) | 10-50 | Opposite market correlation |
| Biotech (RNA) | 30-70 | Binary outcomes |
| Commodity (GLD) | 40-70 | Steady valuation |
| Crypto (BTC-USD) | Varies | Limited fundamentals |

### Scoring Modifications Needed

Some scores may be unreliable due to missing data:
- **Quantum companies:** May lack historical earnings
- **BTC-USD:** No P/E ratio exists
- **Inverse ETFs:** Different valuation logic

**Recommendation:** Weights should be adjusted in Phase 2 based on asset type.

---

## 🔄 Reddit Sentiment Expectations

### Stocks with High Reddit Mentions
- ✅ Quantum Computing (QBTS, IONQ, etc.) - Very active
- ✅ MSFT, GOOGL, AMD - Tech subreddits
- ✅ BTC-USD - Major crypto communities
- ⚠️ RNA - Biotech subreddits
- ⚠️ GLD - Less discussed

### Stocks with Low Reddit Mentions
- ⚠️ UVXY - Technical/volatility traders only
- ⚠️ SPXU, SQQQ - Hedging positions, less discussed
- ⚠️ DYN - May have minimal discussion

**Impact:** Social sentiment may be missing for some assets → Graceful degradation

---

## 📈 Analysis Performance

### Expected Execution Times

```
Fundamentals fetch:   5 sec   (16 tickers = slightly longer)
VIX/S&P fetch:        8 sec
Fear & Greed scrape:  15 sec
Reddit analysis:      120+ sec  (16 tickers = proportionally longer)
Scoring:              5 sec
Reporting:            5 sec
────────────────────────────
Total:                3-5 min (slightly longer than 5-stock baseline)
```

### CSV Output Expectations

**fundamentals_scored.csv:**
- 16 rows (one per asset)
- Some rows may have missing data (inverse ETFs, BTC-USD)
- Scores should still generate (0-70 max)

**weighted_score.csv:**
- 16 rows
- Scores 0-100 after Fear & Greed weighting
- May see unusual patterns for inverse ETFs

**social_sentiment_log.csv:**
- 16 rows
- Quantum stocks likely to have high sentiment data
- BTC-USD to have abundant mentions
- Inverse ETFs may have minimal sentiment

---

## 💡 Phase 1 Notes

### What Will Work Well
✅ Tech stocks (MSFT, GOOGL, etc.) - Strong fundamentals  
✅ Reddit sentiment analysis - All 16 will have some data  
✅ VIX/Market data - Works for all  
✅ Fear & Greed weighting - Universal  

### What May Have Issues
⚠️ Quantum stocks - Missing historical data  
⚠️ BTC-USD - No fundamental ratios  
⚠️ Inverse ETFs - Different valuation logic  
⚠️ DYN & RNA - Potentially sparse data  

### Recommendations for Phase 1
1. **Run as-is** - See what works
2. **Document missing data** - Which assets lack metrics
3. **Plan Phase 2** - Asset-type-specific scoring
4. **Handle gracefully** - Missing data should not crash system

---

## 🚀 Phase 1 Execution Plan

### Custom Watchlist Test Run

```bash
cd C:\Hermes
python main.py
```

**Expected output:**
```
Processing 16 assets...
✓ SQQQ - Inverse Nasdaq
✓ UVXY - Inverse VIX
✓ SPXU - Inverse S&P500
✓ RNA - Moderna
✓ DYN - Dynamics
✓ MSFT - Microsoft
✓ GOOGL - Google
✓ INTC - Intel
✓ AMD - AMD
✓ GLD - Gold ETF
✓ RGTI - Rigetti
✓ QBTS - D-Wave
✓ IONQ - IonQ
✓ QUBT - Quantum Computing
✓ QMCO - Quantum Computing
✓ BTC-USD - Bitcoin

4 files generated:
  fundamentals_scored.csv
  weighted_score.csv
  social_sentiment_log.csv
  fear_greed_log.csv
  vix_sp500_data.csv
```

### Expected Scores Example
```
ticker,weighted_score
BTC-USD,65.2      ← High due to strong sentiment
IONQ,58.3         ← Quantum sentiment positive
QBTS,52.1         ← Quantum, moderate sentiment
MSFT,72.5         ← Tech, strong fundamentals
GOOGL,70.1        ← Tech, strong fundamentals
AMD,68.4          ← Tech, good fundamentals
INTC,62.3         ← Tech, decent fundamentals
RNA,55.7          ← Biotech, mid-tier
GLD,48.2          ← Commodity, steady
RGTI,45.0         ← Quantum early-stage
QUBT,42.8         ← Quantum early-stage
QMCO,40.1         ← Quantum early-stage
DYN,35.4          ← Limited data
SQQQ,32.1         ← Inverse ETF (scores low by design)
UVXY,28.5         ← Inverse VIX
SPXU,25.3         ← Inverse S&P (scores low by design)
```

---

## 🔧 Configuration Commands

### To Run Phase 1 with Custom Watchlist

```bash
cd C:\Hermes
mkdir outputs
pip install -r requirements.txt
pip install yfinance selenium webdriver-manager beautifulsoup4 tabulate
python main.py
```

### To Switch Watchlists (Temporary)

Edit `main.py` lines 15-39 and replace with different assets.

### To Add More Assets

Simply add to both `watchlist` and `tickers` lists in `main.py`:

```python
watchlist = [
    # existing assets...
    'NEW_TICKER'  # Add here
]

tickers = [
    # existing...
    'NEW_TICKER'  # And here
]
```

---

## 📊 Monitoring Your Portfolio

After Phase 1 runs successfully:

```bash
# View final scores
type C:\Hermes\outputs\weighted_score.csv

# View sentiment
type C:\Hermes\outputs\social_sentiment_log.csv

# View market data
type C:\Hermes\outputs\vix_sp500_data.csv
```

### Key Metrics to Watch

1. **Tech stocks (MSFT, GOOGL)** - Should score 60-80
2. **Quantum stocks (QBTS, IONQ)** - Reddit sentiment key indicator
3. **Inverse ETFs (SQQQ)** - Should score low when market is up
4. **BTC-USD** - Strong Reddit sentiment likely
5. **Overall portfolio score** - Mix of bullish/bearish exposure

---

## ✅ Next Steps

**Phase 1 with Custom Watchlist:**
1. Create `.env` file ← You're here!
2. Create outputs/ directory
3. Install dependencies
4. Run: `python main.py`
5. Analyze 16-asset output

**Expected result:** 16 assets scored across fundamentals + sentiment

---

## 📝 Notes

- **Diversified portfolio** - Different asset classes, behaviors
- **Higher complexity** - More assets = longer execution
- **Good test** - Will stress-test error handling with edge cases
- **Real-world scenario** - Handles missing data gracefully

---

Ready for Phase 1! 🚀


