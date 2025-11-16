from __future__ import annotations

# Technical indicator agent implementation for Hermes.
# Computes Bollinger Bands, RSI, MACD, support/resistance, and trend metrics
# using yfinance data.

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict

import numpy as np
import pandas as pd
import yfinance as yf

from .interfaces import Event, FeatureVector, TechnicalIndicatorAgent


@dataclass
class YFinanceTechnicalIndicatorAgent(TechnicalIndicatorAgent):
    # Technical indicator agent backed by yfinance price data.
    # Indicators:
    #   - Bollinger Bands (20-day, 2 std)
    #   - RSI (14)
    #   - MACD (12/26/9)
    #   - Support/Resistance (recent highs/lows)
    #   - Trend strength (slope of 20-day MA)

    lookback_days: int = 90
    cache_minutes: int = 30

    def __post_init__(self) -> None:
        self._price_cache: Dict[str, pd.DataFrame] = {}
        self._cache_ts: Dict[str, datetime] = {}

    def handle_event(self, event: Event) -> None:  # pragma: no cover
        return

    def tick(self, as_of: datetime) -> None:  # pragma: no cover
        return

    def compute_features(self, symbol: str, as_of: datetime) -> FeatureVector:
        price_df = self._get_price_history(symbol, as_of)
        if price_df.empty:
            return FeatureVector(symbol, as_of, features={}, meta={"rows": 0})

        closes = price_df["Close"]
        features: Dict[str, float] = {}

        # Bollinger Bands
        bb_mean = closes.rolling(window=20).mean()
        bb_std = closes.rolling(window=20).std()
        if len(bb_mean.dropna()) == 0:
            features["bb_upper"] = features["bb_lower"] = features["bb_pct"] = np.nan
        else:
            upper = bb_mean.iloc[-1] + 2 * bb_std.iloc[-1]
            lower = bb_mean.iloc[-1] - 2 * bb_std.iloc[-1]
            features["bb_upper"] = float(upper)
            features["bb_lower"] = float(lower)
            features["bb_pct"] = float((closes.iloc[-1] - lower) / (upper - lower)) if upper != lower else np.nan

        # RSI (14)
        delta = closes.diff()
        up = delta.clip(lower=0).rolling(window=14).mean()
        down = -delta.clip(upper=0).rolling(window=14).mean()
        rs = up / down
        features["rsi_14"] = float(100 - (100 / (1 + rs.iloc[-1]))) if rs.iloc[-1] > 0 else 0.0

        # MACD
        ema12 = closes.ewm(span=12, adjust=False).mean()
        ema26 = closes.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        features["macd"] = float(macd.iloc[-1])
        features["macd_signal"] = float(signal.iloc[-1])
        features["macd_hist"] = float(macd.iloc[-1] - signal.iloc[-1])

        # Support / Resistance
        window_lookback = closes.last(f"{min(30, len(closes))}D")
        features["recent_support"] = float(window_lookback.min()) if not window_lookback.empty else np.nan
        features["recent_resistance"] = float(window_lookback.max()) if not window_lookback.empty else np.nan

        # Trend strength (slope of 20-day MA)
        ma20 = closes.rolling(window=20).mean().dropna()
        if len(ma20) >= 2:
            x = np.arange(len(ma20))
            slope = np.polyfit(x, ma20.values, 1)[0]
            features["trend_strength"] = float(slope)
        else:
            features["trend_strength"] = 0.0

        return FeatureVector(symbol=symbol, ts=as_of, features=features, meta={"rows": len(closes)})

    def _get_price_history(self, symbol: str, as_of: datetime) -> pd.DataFrame:
        key = symbol.upper()
        cached_df = self._price_cache.get(key)
        cache_ts = self._cache_ts.get(key)
        if cached_df is not None and cache_ts is not None:
            if (as_of - cache_ts).total_seconds() < self.cache_minutes * 60:
                return cached_df[cached_df.index <= as_of]

        start = as_of - timedelta(days=self.lookback_days)
        data = yf.download(
            symbol,
            start=start.strftime("%Y-%m-%d"),
            end=(as_of + timedelta(days=1)).strftime("%Y-%m-%d"),
            progress=False,
            auto_adjust=True,
        )
        if data.empty:
            return pd.DataFrame()

        df = data[["Close"]].copy()
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        self._price_cache[key] = df
        self._cache_ts[key] = as_of
        return df[df.index <= as_of]

