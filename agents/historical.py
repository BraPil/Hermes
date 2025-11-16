#Historical performance agent implementation for Hermes.

#Provides a YFinance-backed HistoricalPerformanceAgent that computes
#multi-horizon performance metrics for each symbol.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Sequence

import numpy as np
import pandas as pd
import yfinance as yf

from .interfaces import Event, FeatureVector, HistoricalPerformanceAgent


def _ensure_datetime(value: datetime | str) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)


def _compute_drawdown(returns: pd.Series) -> float:
    cumulative = (1 + returns).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    return float(drawdown.min())


@dataclass
class YFinanceHistoricalPerformanceAgent(HistoricalPerformanceAgent):
    
    #Historical performance agent based on yfinance price data.

    #Features per horizon (all/12m/4w/7d/24h):
    #    - cumulative_return
    #    - annualized_volatility
    #    - max_drawdown
    #    - sharpe_ratio
    #    - trend_slope (log-price regression)
    

    min_history_days: int = 365 * 5
    cache_days: int = 5

    def __post_init__(self) -> None:
        self._price_cache: Dict[str, pd.DataFrame] = {}
        self._cache_ts: Dict[str, datetime] = {}

    # -- HistoricalPerformanceAgent interface ----------------------------------

    def handle_event(self, event: Event) -> None:  # pragma: no cover - no RT events yet
        return

    def tick(self, as_of: datetime) -> None:  # pragma: no cover
        return

    def compute_features(
        self,
        symbol: str,
        as_of: datetime,
        horizons: Sequence[str] = ("all", "12m", "4w", "7d", "24h"),
    ) -> List[FeatureVector]:
        as_of = _ensure_datetime(as_of)
        price_df = self._get_price_history(symbol, as_of)
        if price_df.empty:
            return []

        outputs: List[FeatureVector] = []
        for horizon in horizons:
            window = self._select_window(price_df, as_of, horizon)
            if window is None or len(window) < 3:
                continue

            stats = self._compute_window_features(window)
            features = {
                f"{horizon}_cumulative_return": stats["cumulative_return"],
                f"{horizon}_annualized_vol": stats["annualized_volatility"],
                f"{horizon}_max_drawdown": stats["max_drawdown"],
                f"{horizon}_sharpe": stats["sharpe_ratio"],
                f"{horizon}_trend_slope": stats["trend_slope"],
            }
            outputs.append(
                FeatureVector(symbol=symbol, ts=as_of, features=features, meta={"horizon": horizon, "rows": len(window)})
            )

        return outputs

    # -- Helpers ----------------------------------------------------------------

    def _get_price_history(self, symbol: str, as_of: datetime) -> pd.DataFrame:
        key = symbol.upper()
        cached_df = self._price_cache.get(key)
        cache_ts = self._cache_ts.get(key)
        if cached_df is not None and cache_ts is not None and (as_of - cache_ts).days < self.cache_days:
            return cached_df[cached_df.index <= as_of]

        start = as_of - timedelta(days=self.min_history_days)
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

    def _select_window(self, price_df: pd.DataFrame, as_of: datetime, horizon: str) -> pd.Series | None:
        if horizon == "all":
            window = price_df["Close"]
        elif horizon.endswith("m"):
            months = int(horizon[:-1])
            cutoff = as_of - timedelta(days=30 * months)
            window = price_df.loc[price_df.index >= cutoff, "Close"]
        elif horizon.endswith("w"):
            weeks = int(horizon[:-1])
            cutoff = as_of - timedelta(weeks=weeks)
            window = price_df.loc[price_df.index >= cutoff, "Close"]
        elif horizon.endswith("d"):
            days = int(horizon[:-1])
            cutoff = as_of - timedelta(days=days)
            window = price_df.loc[price_df.index >= cutoff, "Close"]
        else:
            return None

        return window if len(window) else None

    def _compute_window_features(self, prices: pd.Series) -> Dict[str, float]:
        returns = prices.pct_change().dropna()
        if returns.empty:
            return dict.fromkeys(
                ["cumulative_return", "annualized_volatility", "max_drawdown", "sharpe_ratio", "trend_slope"], 0.0
            )

        cumulative = float((prices.iloc[-1] / prices.iloc[0]) - 1)
        vol = float(returns.std() * np.sqrt(252))
        max_dd = _compute_drawdown(returns)
        sharpe = float((returns.mean() * 252) / (returns.std() * np.sqrt(252))) if returns.std() > 0 else 0.0

        log_prices = np.log(prices)
        x = np.arange(len(log_prices))
        slope = np.polyfit(x, log_prices, 1)[0]

        return {
            "cumulative_return": cumulative,
            "annualized_volatility": vol,
            "max_drawdown": max_dd,
            "sharpe_ratio": sharpe,
            "trend_slope": float(slope),
        }


#Historical performance agent implementation for Hermes.

#This provides a concrete HistoricalPerformanceAgent that uses yfinance
#to pull price history and compute rolling performance features
#(returns, volatility, drawdown, etc.) over multiple horizons.


from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Sequence

import numpy as np
import pandas as pd
import yfinance as yf

from .interfaces import Event, FeatureVector, HistoricalPerformanceAgent


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


def _ensure_datetime(value: datetime | str) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)


def _compute_drawdown(series: pd.Series) -> float:
    
    #Compute max drawdown for a price/return series.
    
    cumulative = (1 + series).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    return drawdown.min()


# ---------------------------------------------------------------------------
# Concrete HistoricalPerformanceAgent
# ---------------------------------------------------------------------------


@dataclass
class YFinanceHistoricalPerformanceAgent(HistoricalPerformanceAgent):
    
    #Historical performance agent based on yfinance price data.

    #Features computed per horizon (all/12m/4w/7d/24h):
    #    - cumulative_return
    #    - annualized_volatility
    #    - max_drawdown
    #    - sharpe_ratio (using simple std dev)
    #    - trend_slope (linear regression on log prices)
    

    min_history_days: int = 365 * 5  # required history for "all-time"
    cache_days: int = 5              # refresh cache every N days

    def __post_init__(self) -> None:
        self._price_cache: Dict[str, pd.DataFrame] = {}
        self._cache_ts: Dict[str, datetime] = {}

    # --- HistoricalPerformanceAgent overrides ---------------------------------

    def handle_event(self, event: Event) -> None:
        # This agent does not consume real-time events;
        # data fetching happens on-demand in compute_features().
        return

    def tick(self, as_of: datetime) -> None:
        # Nothing periodic; cache invalidation handled in compute_features().
        return

    def compute_features(
        self,
        symbol: str,
        as_of: datetime,
        horizons: Sequence[str] = ("all", "12m", "4w", "7d", "24h"),
    ) -> List[FeatureVector]:
        as_of = _ensure_datetime(as_of)
        price_df = self._get_price_history(symbol, as_of)
        if price_df.empty:
            return []

        outputs: List[FeatureVector] = []
        for horizon in horizons:
            window = self._select_window(price_df, as_of, horizon)
            if window is None or len(window) < 3:
                continue

            feature_dict = self._compute_window_features(window)
            outputs.append(
                FeatureVector(
                    symbol=symbol,
                    ts=as_of,
                    features={
                        f"{horizon}_cumulative_return": feature_dict["cumulative_return"],
                        f"{horizon}_annualized_vol": feature_dict["annualized_volatility"],
                        f"{horizon}_max_drawdown": feature_dict["max_drawdown"],
                        f"{horizon}_sharpe": feature_dict["sharpe_ratio"],
                        f"{horizon}_trend_slope": feature_dict["trend_slope"],
                    },
                    meta={"horizon": horizon, "rows": len(window)},
                )
            )

        return outputs

    # --- Internal helpers ------------------------------------------------------

    def _get_price_history(self, symbol: str, as_of: datetime) -> pd.DataFrame:
        
        #Fetch price history up to `as_of`, with caching.
        
        cache_key = symbol.upper()
        if (
            cache_key in self._price_cache
            and cache_key in self._cache_ts
            and (as_of - self._cache_ts[cache_key]).days < self.cache_days
        ):
            df = self._price_cache[cache_key]
            return df[df.index <= as_of]

        period_start = as_of - timedelta(days=self.min_history_days)
        data = yf.download(
            symbol,
            start=period_start.strftime("%Y-%m-%d"),
            end=(as_of + timedelta(days=1)).strftime("%Y-%m-%d"),
            progress=False,
            auto_adjust=True,
        )
        if data.empty:
            return pd.DataFrame()

        df = data[["Close"]].copy()
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()

        # Cache results
        self._price_cache[cache_key] = df
        self._cache_ts[cache_key] = as_of
        return df[df.index <= as_of]

    def _select_window(
        self, price_df: pd.DataFrame, as_of: datetime, horizon: str
    ) -> pd.Series | None:
        
        #Slice price history for the requested horizon.
        
        if horizon == "all":
            window = price_df["Close"]
        elif horizon.endswith("m"):
            months = int(horizon[:-1])
            cutoff = as_of - timedelta(days=30 * months)
            window = price_df.loc[price_df.index >= cutoff, "Close"]
        elif horizon.endswith("w"):
            weeks = int(horizon[:-1])
            cutoff = as_of - timedelta(weeks=weeks)
            window = price_df.loc[price_df.index >= cutoff, "Close"]
        elif horizon.endswith("d"):
            days = int(horizon[:-1])
            cutoff = as_of - timedelta(days=days)
            window = price_df.loc[price_df.index >= cutoff, "Close"]
        else:
            return None

        return window if len(window) > 0 else None

    def _compute_window_features(self, prices: pd.Series) -> Dict[str, float]:
        
        #Compute rolling performance stats for a price window.
        
        returns = prices.pct_change().dropna()
        if returns.empty:
            return {
                "cumulative_return": 0.0,
                "annualized_volatility": 0.0,
                "max_drawdown": 0.0,
                "sharpe_ratio": 0.0,
                "trend_slope": 0.0,
            }

        cumulative_return = float((prices.iloc[-1] / prices.iloc[0]) - 1)
        vol = float(returns.std() * np.sqrt(252))
        max_drawdown = float(_compute_drawdown(returns))
        sharpe = float((returns.mean() * 252) / (returns.std() * np.sqrt(252))) if returns.std() > 0 else 0.0

        # Trend slope via linear regression on log prices
        log_prices = np.log(prices)
        x = np.arange(len(log_prices))
        slope = np.polyfit(x, log_prices, 1)[0]

        return {
            "cumulative_return": cumulative_return,
            "annualized_volatility": vol,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe,
            "trend_slope": float(slope),
        }


