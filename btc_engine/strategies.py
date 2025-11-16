from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict

from .interfaces import LayerOutput, TradePlan


class Strategy(ABC):
    """
    Base class for trading strategies.

    Each concrete strategy:
      - Looks at the latest layer outputs (A–D)
      - Decides whether its pattern is present
      - Builds a TradePlan consistent with its logic
    """

    name: str

    @abstractmethod
    def should_trade(self, layers: Dict[str, LayerOutput]) -> bool:
        """Return True if this strategy sees an opportunity in the current context."""

    @abstractmethod
    def build_trade_plan(self, base_plan: TradePlan, layers: Dict[str, LayerOutput]) -> TradePlan:
        """
        Given a base TradePlan (direction, size, horizon) and the layer outputs,
        return a possibly refined TradePlan (e.g. different horizon, metadata).
        """


@dataclass
class TrendFollowingStrategy(Strategy):
    """
    High-level trend-following strategy.

    Intended to align with outputs from:
      - Layer A (historical trend/regime)
      - Layer B (recent price action)
    For now it simply tags the trade with its name; later it will
    customise horizon, stops and position sizing based on trend signals.
    """

    name: str = "trend_following"

    def should_trade(self, layers: Dict[str, LayerOutput]) -> bool:
        # Placeholder: always eligible; future logic will inspect layer outputs.
        return True

    def build_trade_plan(self, base_plan: TradePlan, layers: Dict[str, LayerOutput]) -> TradePlan:
        base_plan.metadata.setdefault("strategies", []).append(self.name)
        return base_plan


@dataclass
class MeanReversionStrategy(Strategy):
    """
    Mean-reversion strategy.

    Will later rely on overbought/oversold signals and volatility regimes
    derived from the layers. Currently only annotates the trade.
    """

    name: str = "mean_reversion"

    def should_trade(self, layers: Dict[str, LayerOutput]) -> bool:
        # Placeholder: strategy is available but does not veto trades yet.
        return True

    def build_trade_plan(self, base_plan: TradePlan, layers: Dict[str, LayerOutput]) -> TradePlan:
        base_plan.metadata.setdefault("strategies", []).append(self.name)
        return base_plan


@dataclass
class BreakoutStrategy(Strategy):
    """
    Breakout / volatility expansion strategy.

    This will be especially tied to Layer B (pattern opportunity identifier),
    focusing on range breaks and volatility spikes.
    """

    name: str = "breakout"

    def should_trade(self, layers: Dict[str, LayerOutput]) -> bool:
        # Placeholder implementation; later will react to Layer B signals.
        return True

    def build_trade_plan(self, base_plan: TradePlan, layers: Dict[str, LayerOutput]) -> TradePlan:
        base_plan.metadata.setdefault("strategies", []).append(self.name)
        return base_plan


def default_strategies() -> Dict[str, Strategy]:
    """
    Convenience factory returning a set of named strategies that broadly
    reflects common classes discussed in the algo-trading community
    (trend following, mean reversion, breakout).
    """

    strategies: Dict[str, Strategy] = {
        "trend": TrendFollowingStrategy(),
        "mean_reversion": MeanReversionStrategy(),
        "breakout": BreakoutStrategy(),
    }
    return strategies


