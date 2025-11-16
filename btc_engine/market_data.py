from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd


class MarketDataClient(ABC):
    """
    Abstract interface for BTC-USD market data.

    Implementations may use:
      - Direct exchange APIs (e.g. Binance/Bybit/Deribit WebSockets + REST)
      - Third-party aggregators (e.g. CoinAPI)
      - Local simulations or recorded data
    """

    @abstractmethod
    def get_recent_ohlcv(
        self,
        symbol: str,
        interval: str,
        limit: int,
    ) -> pd.DataFrame:
        """
        Return a DataFrame with columns: ['open', 'high', 'low', 'close', 'volume']
        indexed by timestamp, ordered oldest → newest.
        """

    @abstractmethod
    def get_latest_price(self, symbol: str) -> float:
        """Return the latest traded price for the given symbol."""


@dataclass
class SimulatedMarketDataClient(MarketDataClient):
    """
    Simple local simulator for development.

    It generates a synthetic random walk price series around a configurable
    anchor price, so that layers can produce non-zero signals without
    contacting external APIs.
    """

    anchor_price: float = 50000.0
    seed: Optional[int] = 42

    def _generate_series(self, limit: int, interval_minutes: int) -> pd.Series:
        rng = np.random.default_rng(self.seed)
        # Random walk in log-space for mild realism
        steps = rng.normal(loc=0.0, scale=0.001, size=limit)
        log_prices = np.log(self.anchor_price) + np.cumsum(steps)
        prices = np.exp(log_prices)

        index = pd.date_range(
            end=pd.Timestamp.utcnow(),
            periods=limit,
            freq=f"{interval_minutes}min",
        )
        return pd.Series(prices, index=index)

    def get_recent_ohlcv(
        self,
        symbol: str,
        interval: str,
        limit: int,
    ) -> pd.DataFrame:
        # Map a few common interval strings to minutes
        interval_map = {
            "1m": 1,
            "5m": 5,
            "15m": 15,
            "1h": 60,
        }
        interval_minutes = interval_map.get(interval, 60)
        prices = self._generate_series(limit=limit, interval_minutes=interval_minutes)

        df = pd.DataFrame(
            {
                "open": prices.shift(1).fillna(prices.iloc[0]),
                "high": prices.rolling(2, min_periods=1).max(),
                "low": prices.rolling(2, min_periods=1).min(),
                "close": prices,
                "volume": 1.0,  # placeholder
            },
            index=prices.index,
        )
        return df

    def get_latest_price(self, symbol: str) -> float:
        # Latest price from a short series
        series = self._generate_series(limit=1, interval_minutes=1)
        return float(series.iloc[-1])


class BinanceMarketDataClient(MarketDataClient):
    """
    Placeholder for a future Binance-backed market data client.

    This class will eventually:
      - Maintain a WebSocket connection for real-time BTCUSDT trades/klines
      - Provide low-latency updates to the layers
      - Fall back to REST if needed for history backfill

    For now only the interface is sketched; methods raise NotImplementedError.
    """

    def __init__(self) -> None:
        raise NotImplementedError("BinanceMarketDataClient is not implemented yet.")

    def get_recent_ohlcv(
        self,
        symbol: str,
        interval: str,
        limit: int,
    ) -> pd.DataFrame:
        raise NotImplementedError

    def get_latest_price(self, symbol: str) -> float:
        raise NotImplementedError


class QuantConnectMarketDataClient(MarketDataClient):
    """
    Placeholder for a QuantConnect-backed market data client.

    In practice, when running inside the Lean engine, Hermes will most likely
    be called *from* a QuantConnect algorithm, with data passed in directly,
    rather than pulling data itself. This class exists to document the intended
    interface and to support potential standalone UAT harnesses.
    """

    def __init__(self) -> None:
        raise NotImplementedError("QuantConnectMarketDataClient is not implemented yet.")

    def get_recent_ohlcv(
        self,
        symbol: str,
        interval: str,
        limit: int,
    ) -> pd.DataFrame:
        raise NotImplementedError

    def get_latest_price(self, symbol: str) -> float:
        raise NotImplementedError


class IBKRMarketDataClient(MarketDataClient):
    """
    Placeholder for an Interactive Brokers market data client using ib_insync.

    This will eventually:
      - Connect to TWS or IB Gateway
      - Request historical candles for BTC-related instruments
      - Stream live quotes for low-latency updates
    """

    def __init__(self) -> None:
        raise NotImplementedError("IBKRMarketDataClient is not implemented yet.")

    def get_recent_ohlcv(
        self,
        symbol: str,
        interval: str,
        limit: int,
    ) -> pd.DataFrame:
        raise NotImplementedError

    def get_latest_price(self, symbol: str) -> float:
        raise NotImplementedError


