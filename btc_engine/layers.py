from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import pandas as pd

from .interfaces import BaseLayer, LayerOutput
from .market_data import MarketDataClient


@dataclass
class LayerConfig:
    """Placeholder configuration for each layer."""

    symbol: str = "BTC-USD"
    horizon_minutes: int = 60
    market_data_client: Optional[MarketDataClient] = None


class HistoricalPerformanceLayer(BaseLayer):
    """
    Layer A: historical performance learner.

    For now this is a placeholder that returns a neutral signal.
    In future iterations it will:
      - Load BTC-USD OHLCV history
      - Engineer features
      - Run a predictive model for future returns and risk
    """

    def __init__(self, config: LayerConfig):
        self.symbol = config.symbol
        self.horizon_minutes = config.horizon_minutes
        self._md = config.market_data_client

    def run(self) -> LayerOutput:
        now = pd.Timestamp.utcnow()

        # If no market data client is available, stay neutral.
        if self._md is None:
            return LayerOutput(
                timestamp=now,
                horizon_minutes=self.horizon_minutes,
                direction=0,
                confidence=0.0,
                risk=0.0,
                extras={"layer": "A", "reason": "no_market_data_client"},
            )

        # Simple prototype: SMA-based trend detection on hourly candles
        df = self._md.get_recent_ohlcv(self.symbol, interval="1h", limit=100)
        closes = df["close"]
        if closes.size < 50:
            return LayerOutput(
                timestamp=now,
                horizon_minutes=self.horizon_minutes,
                direction=0,
                confidence=0.0,
                risk=0.0,
                extras={"layer": "A", "reason": "insufficient_history"},
            )

        sma_fast = closes.rolling(20).mean().iloc[-1]
        sma_slow = closes.rolling(50).mean().iloc[-1]
        direction = 0
        if sma_fast > sma_slow:
            direction = 1
        elif sma_fast < sma_slow:
            direction = -1

        # Confidence grows with the absolute distance between SMAs
        distance = abs(sma_fast - sma_slow) / max(sma_slow, 1e-9)
        confidence = float(max(min(distance * 10, 1.0), 0.0))  # scale heuristically into [0, 1]

        # Risk proxy: recent realised volatility
        returns = closes.pct_change().dropna()
        risk = float(returns.tail(50).std())

        return LayerOutput(
            timestamp=now,
            horizon_minutes=self.horizon_minutes,
            direction=direction,
            confidence=confidence,
            risk=risk,
            extras={
                "layer": "A",
                "sma_fast": sma_fast,
                "sma_slow": sma_slow,
            },
        )


class LivePatternLayer(BaseLayer):
    """
    Layer B: live pattern opportunity identifier.

    Initially returns a neutral signal; will later use intraday patterns,
    order book micro-structure and anomaly detection.
    """

    def __init__(self, config: LayerConfig):
        self.symbol = config.symbol
        self.horizon_minutes = config.horizon_minutes
        self._md = config.market_data_client

    def run(self) -> LayerOutput:
        now = pd.Timestamp.utcnow()

        if self._md is None:
            return LayerOutput(
                timestamp=now,
                horizon_minutes=self.horizon_minutes,
                direction=0,
                confidence=0.0,
                risk=0.0,
                extras={"layer": "B", "reason": "no_market_data_client"},
            )

        # Prototype: short-term momentum on 5-minute bars
        df = self._md.get_recent_ohlcv(self.symbol, interval="5m", limit=50)
        closes = df["close"]
        if closes.size < 10:
            return LayerOutput(
                timestamp=now,
                horizon_minutes=self.horizon_minutes,
                direction=0,
                confidence=0.0,
                risk=0.0,
                extras={"layer": "B", "reason": "insufficient_history"},
            )

        recent_returns = closes.pct_change().dropna().tail(5)
        momentum = recent_returns.mean()
        direction = 0
        if momentum > 0:
            direction = 1
        elif momentum < 0:
            direction = -1

        confidence = float(min(max(abs(momentum) * 1000, 0.0), 1.0))
        risk = float(recent_returns.std())

        return LayerOutput(
            timestamp=now,
            horizon_minutes=self.horizon_minutes,
            direction=direction,
            confidence=confidence,
            risk=risk,
            extras={
                "layer": "B",
                "momentum": momentum,
            },
        )


class GeoPoliticalLayer(BaseLayer):
    """
    Layer C: geo-political and macro pattern learner.

    Currently a stub that encodes no directional bias but will later ingest
    macro and regulatory events, mapping them to BTC drift/vol regimes.
    """

    def __init__(self, config: LayerConfig):
        self.symbol = config.symbol
        self.horizon_minutes = config.horizon_minutes

    def run(self) -> LayerOutput:
        now = pd.Timestamp.utcnow()
        return LayerOutput(
            timestamp=now,
            horizon_minutes=self.horizon_minutes,
            direction=0,
            confidence=0.0,
            risk=0.0,
            extras={"layer": "C"},
        )


class SentimentLayer(BaseLayer):
    """
    Layer D: sentiment and fear/greed learner.

    For now this is a placeholder that returns neutral sentiment.
    Future work will:
      - Ingest crypto fear/greed indices
      - Pull social and on-chain sentiment proxies
      - Map extremes to risk scaling factors
    """

    def __init__(self, config: LayerConfig):
        self.symbol = config.symbol
        self.horizon_minutes = config.horizon_minutes

    def run(self) -> LayerOutput:
        now = pd.Timestamp.utcnow()
        return LayerOutput(
            timestamp=now,
            horizon_minutes=self.horizon_minutes,
            direction=0,
            confidence=0.0,
            risk=0.0,
            extras={"layer": "D"},
        )


def run_all_layers(config: LayerConfig) -> Dict[str, LayerOutput]:
    """
    Convenience helper to run all four layers for the given symbol.
    This is used by the orchestrator to keep the first version simple.
    """

    layers = {
        "A": HistoricalPerformanceLayer(config),
        "B": LivePatternLayer(config),
        "C": GeoPoliticalLayer(config),
        "D": SentimentLayer(config),
    }
    return {name: layer.run() for name, layer in layers.items()}


