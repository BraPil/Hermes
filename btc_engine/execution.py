from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import pandas as pd

from .interfaces import ExecutedTrade, ExecutionAgent as ExecutionAgentBase
from .interfaces import TradePlan


@dataclass
class ExecutionConfig:
    """
    Placeholder configuration for the execution agent.

    In future this will include:
      - API keys / connection details for the paper trading environment
      - Slippage and fee models
      - Safety limits for orders
    """

    symbol: str = "BTC-USD"


class NoOpExecutionAgent(ExecutionAgentBase):
    """
    Execution agent that does *not* talk to a real broker yet.

    It simulates instant fills at the plan's entry price (currently 0.0)
    so that the rest of the orchestration and feedback pipeline can be
    developed without external dependencies.
    """

    def __init__(self, config: ExecutionConfig):
        self.symbol = config.symbol
        self.config = config
        self._trade_counter = 0

    def execute(self, plan: TradePlan) -> ExecutedTrade:
        self._trade_counter += 1
        broker_trade_id = f"SIM-{self._trade_counter}"
        # For now we assume full fill at the specified entry_price
        return ExecutedTrade(
            broker_trade_id=broker_trade_id,
            plan=plan,
            filled_price=plan.entry_price,
            filled_size=plan.size,
            status="filled",
            fees=0.0,
            extras={
                "simulated": True,
                "executed_at": pd.Timestamp.utcnow().isoformat(),
            },
        )


class IBKRExecutionAgent(ExecutionAgentBase):
    """
    Placeholder for a production-grade execution agent that talks to IBKR
    via ib_insync.

    Responsibilities will include:
      - Mapping TradePlan into IBKR order objects
      - Submitting and monitoring orders
      - Handling partial fills, rejections and cancellations
    """

    def __init__(self, config: ExecutionConfig):
        self.symbol = config.symbol
        self.config = config
        raise NotImplementedError("IBKRExecutionAgent is not implemented yet.")

    def execute(self, plan: TradePlan) -> ExecutedTrade:
        raise NotImplementedError


