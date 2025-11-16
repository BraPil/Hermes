from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import pandas as pd

from .interfaces import DecisionLayer as DecisionLayerBase
from .interfaces import LayerOutput, TradePlan
from .strategies import Strategy, default_strategies


@dataclass
class DecisionConfig:
    symbol: str = "BTC-USD"
    max_position_size: float = 1.0  # in BTC, for now a simple cap
    default_horizon_minutes: int = 60
    # If provided, restricts the set of strategies used by the decision layer.
    strategy_names: Optional[List[str]] = None


class SimpleDecisionLayer(DecisionLayerBase):
    """
    First-pass decision layer that combines layer outputs in a simple,
    interpretable way.

    For now it:
      - Requires at least one non-zero directional suggestion to trade
      - Averages directions and confidences across layers
      - Scales position size with aggregate confidence
    This is intentionally conservative and will be replaced by a learned
    meta-model once we have enough data.
    """

    def __init__(self, config: DecisionConfig):
        self.symbol = config.symbol
        self.config = config
        strategies = default_strategies()
        if config.strategy_names:
            strategies = {name: s for name, s in strategies.items() if name in config.strategy_names}
        self._strategies: Dict[str, Strategy] = strategies

    def decide(
        self,
        layer_outputs: Dict[str, LayerOutput],
    ) -> Optional[TradePlan]:
        # Aggregate directions and confidences
        total_weight = 0.0
        weighted_direction = 0.0
        avg_horizon = 0.0

        for layer_name, out in layer_outputs.items():
            weight = max(out.confidence, 0.0)
            total_weight += weight
            weighted_direction += out.direction * weight
            avg_horizon += out.horizon_minutes

        if not layer_outputs:
            return None

        avg_horizon = avg_horizon / max(len(layer_outputs), 1)

        if total_weight == 0.0:
            # Nobody has a confident opinion – stay flat
            return None

        agg_direction = 1 if weighted_direction > 0 else -1
        agg_confidence = min(max(total_weight / len(layer_outputs), 0.0), 1.0)

        if agg_confidence == 0.0:
            return None

        # Simple position sizing: proportional to aggregate confidence
        size = self.config.max_position_size * agg_confidence

        # For now we do not know the live price; we leave price fields as 0.0
        # and expect future versions to integrate a market data client.
        now = pd.Timestamp.utcnow()
        base_plan = TradePlan(
            timestamp=now,
            symbol=self.symbol,
            side="long" if agg_direction > 0 else "short",
            size=size,
            entry_price=0.0,
            stop_loss=0.0,
            take_profit=0.0,
            time_horizon_minutes=int(avg_horizon or self.config.default_horizon_minutes),
            metadata={
                "agg_confidence": agg_confidence,
                "layers_used": list(layer_outputs.keys()),
            },
        )

        # Let strategies refine the base trade plan and annotate it.
        eligible_strategies = [
            strategy for strategy in self._strategies.values() if strategy.should_trade(layer_outputs)
        ]

        plan = base_plan
        for strategy in eligible_strategies:
            plan = strategy.build_trade_plan(plan, layer_outputs)

        # If no strategies are eligible, we still return the base plan so the
        # orchestrator can see that a trade was intended.
        return plan


