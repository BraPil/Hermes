from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import os
import pandas as pd

from .decision import DecisionConfig, SimpleDecisionLayer
from .execution import ExecutionConfig, NoOpExecutionAgent, IBKRExecutionAgent
from .feedback import FeedbackConfig, SimpleFeedbackAgent
from .interfaces import ExecutedTrade, Orchestrator as OrchestratorBase
from .layers import LayerConfig, run_all_layers
from .market_data import IBKRMarketDataClient, SimulatedMarketDataClient


@dataclass
class OrchestratorConfig:
    """Top-level configuration for the BTC orchestrator."""

    symbol: str = "BTC-USD"
    horizon_minutes: int = 60
    # Environment selection:
    #   - "dev": local simulation, no real broker/data
    #   - "uat": QuantConnect / Lean-based environment (planned)
    #   - "prod": IBKR-backed live or paper trading
    env: str = "dev"


class BTCOrchestrator(OrchestratorBase):
    """
    Coordinates the BTC-only multi-layer engine:
      - Runs Layers A–D
      - Uses the decision layer to generate a TradePlan
      - Executes the plan via the execution agent
      - Feeds back realised outcomes to the feedback agent
    """

    def __init__(self, config: OrchestratorConfig):
        self.symbol = config.symbol
        self.config = config

        # Determine environment (allow override via HERMES_ENV)
        env = (config.env or os.getenv("HERMES_ENV", "dev")).lower()

        # Choose market data client and execution agent based on environment.
        if env == "dev":
            md_client = SimulatedMarketDataClient()
            execution_agent = NoOpExecutionAgent(ExecutionConfig(symbol=config.symbol))
        elif env == "uat":
            # QuantConnect integration will typically host Hermes inside Lean,
            # so we keep simulated clients here for now.
            md_client = SimulatedMarketDataClient()
            execution_agent = NoOpExecutionAgent(ExecutionConfig(symbol=config.symbol))
        elif env == "prod":
            # Placeholders for future IBKR integration. Instantiation will raise
            # NotImplementedError until wiring is complete.
            md_client = IBKRMarketDataClient()
            execution_agent = IBKRExecutionAgent(ExecutionConfig(symbol=config.symbol))
        else:
            raise ValueError(f"Unknown Hermes environment: {env}")

        layer_config = LayerConfig(
            symbol=config.symbol,
            horizon_minutes=config.horizon_minutes,
            market_data_client=md_client,
        )
        self._layer_config = layer_config

        self._decision = SimpleDecisionLayer(
            DecisionConfig(symbol=config.symbol, default_horizon_minutes=config.horizon_minutes)
        )
        self._execution = execution_agent
        self._feedback = SimpleFeedbackAgent(FeedbackConfig(symbol=config.symbol))

    def run_cycle(self) -> Optional[ExecutedTrade]:
        # 1. Run all layers
        layer_outputs = run_all_layers(self._layer_config)

        # 2. Ask the decision layer for a trade plan
        plan = self._decision.decide(layer_outputs)
        if plan is None:
            print("[Orchestrator] No trade plan generated for this cycle.")
            return None

        # 3. Execute the plan
        executed_trade = self._execution.execute(plan)

        # 4. Fetch a dummy price path to feed back
        #    In a later phase, this will come from real BTC-USD market data.
        price_index = pd.date_range(
            start=plan.timestamp,
            periods=2,
            freq=f"{plan.time_horizon_minutes}min",
        )
        price_path = pd.Series(
            [plan.entry_price, plan.entry_price],
            index=price_index,
        )

        self._feedback.update_from_trade(executed_trade, price_path)
        return executed_trade


