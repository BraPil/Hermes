"""
Entry point for the BTC-only Hermes engine.

This script wires together the BTCOrchestrator and runs a single decision cycle.
In future it will:
  - Schedule repeated cycles
  - Integrate real BTC-USD data feeds
  - Connect to a real paper trading environment
"""

import os

from btc_engine.orchestrator import BTCOrchestrator, OrchestratorConfig


def main() -> None:
    env = os.getenv("HERMES_ENV", "dev")
    orchestrator = BTCOrchestrator(
        OrchestratorConfig(
            symbol="BTC-USD",
            horizon_minutes=60,
            env=env,
        )
    )
    orchestrator.run_cycle()


if __name__ == "__main__":
    main()


