from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import pandas as pd


@dataclass
class LayerOutput:
    """
    Generic output structure for a layer.

    Each layer can extend this via the `extras` dict if it needs more detail.
    """

    timestamp: pd.Timestamp
    horizon_minutes: int
    # Directional signal, e.g. -1 short, 0 flat, +1 long
    direction: int
    # Confidence in [0, 1]
    confidence: float
    # Risk or volatility estimate (annualised or per-horizon, layer-specific)
    risk: float
    # Free-form payload for layer-specific diagnostics
    extras: Dict[str, Any]


@dataclass
class TradePlan:
    """Structured representation of a planned BTC-USD trade."""

    timestamp: pd.Timestamp
    symbol: str
    side: str  # "long" or "short"
    size: float  # notional size in base currency units
    entry_price: float
    stop_loss: float
    take_profit: float
    time_horizon_minutes: int
    metadata: Dict[str, Any]


@dataclass
class ExecutedTrade:
    """Minimal representation of an executed trade on the broker/paper account."""

    broker_trade_id: str
    plan: TradePlan
    filled_price: float
    filled_size: float
    status: str  # "filled", "partially_filled", "rejected", "cancelled"
    fees: float
    extras: Dict[str, Any]


class BaseLayer(ABC):
    """Abstract base class for all signal-generating layers (A, B, C, D)."""

    symbol: str

    @abstractmethod
    def run(self) -> LayerOutput:
        """Run the layer and return its latest output for the configured symbol."""


class DecisionLayer(ABC):
    """Combines outputs from Layers A–D into a single trade plan."""

    symbol: str

    @abstractmethod
    def decide(
        self,
        layer_outputs: Dict[str, LayerOutput],
    ) -> Optional[TradePlan]:
        """
        Take the latest outputs from each layer and produce a TradePlan,
        or None if no trade should be placed.
        """


class ExecutionAgent(ABC):
    """Responsible for translating a TradePlan into broker API calls."""

    symbol: str

    @abstractmethod
    def execute(self, plan: TradePlan) -> ExecutedTrade:
        """Send the trade to the (paper) broker and return the execution result."""


class FeedbackAgent(ABC):
    """
    Consumes realised outcomes and feeds them back to the learning components.
    For now this is a skeleton; learning logic will be plugged in later.
    """

    symbol: str

    @abstractmethod
    def update_from_trade(
        self,
        executed_trade: ExecutedTrade,
        price_path: pd.Series,
    ) -> None:
        """
        Update internal state / models based on how a particular trade performed.

        `price_path` is a time series of BTC-USD prices from entry to (at least)
        the intended horizon, so we can compute MAE/MFE and realised PnL.
        """


class Orchestrator(ABC):
    """
    High-level entity that coordinates layers, decision logic,
    execution and feedback for a single symbol (BTC-USD in this phase).
    """

    symbol: str

    @abstractmethod
    def run_cycle(self) -> Optional[ExecutedTrade]:
        """
        Run a full decision cycle:
          1. Invoke all layers A–D
          2. Call the decision layer to produce a TradePlan (if any)
          3. Execute the plan
          4. Feed back realised information to the learning components
        """


