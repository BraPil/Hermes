from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .interfaces import ExecutedTrade, FeedbackAgent as FeedbackAgentBase


@dataclass
class FeedbackConfig:
    """Placeholder configuration for the feedback agent."""

    symbol: str = "BTC-USD"


class SimpleFeedbackAgent(FeedbackAgentBase):
    """
    First-pass feedback agent.

    It currently:
      - Computes simple realised PnL and basic diagnostics (MAE/MFE)
      - Logs or stores them for later analysis

    Future versions will:
      - Update the parameters or models for the layers and decision policy
      - Implement online learning or scheduled retraining
    """

    def __init__(self, config: FeedbackConfig):
        self.symbol = config.symbol
        self.config = config

    def update_from_trade(
        self,
        executed_trade: ExecutedTrade,
        price_path: pd.Series,
    ) -> None:
        if price_path.empty:
            return

        side = executed_trade.plan.side
        entry_price = executed_trade.filled_price
        exit_price = price_path.iloc[-1]

        if side == "long":
            pnl = exit_price - entry_price
            mae = (price_path.min() - entry_price)
            mfe = (price_path.max() - entry_price)
        else:
            pnl = entry_price - exit_price
            mae = (entry_price - price_path.max())
            mfe = (entry_price - price_path.min())

        # In a later phase this should send metrics to a proper logger or DB.
        diagnostics = {
            "symbol": self.symbol,
            "pnl": pnl,
            "mae": mae,
            "mfe": mfe,
            "start": price_path.index[0].isoformat(),
            "end": price_path.index[-1].isoformat(),
        }
        # For now, we simply print the diagnostics to keep the skeleton lightweight.
        print(f"[Feedback] Trade diagnostics: {diagnostics}")


