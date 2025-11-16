from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, Optional

from fastapi import FastAPI, Query

from btc_engine.orchestrator import BTCOrchestrator, OrchestratorConfig


app = FastAPI(
    title="Hermes BTC API",
    version="0.1.0",
    description="HTTP interface for the Hermes BTC orchestrator (dev-mode, simulation only).",
)


@app.get("/health")
def health() -> Dict[str, str]:
    """Simple liveness endpoint."""
    return {"status": "ok"}


@app.post("/btc/run_cycle")
def btc_run_cycle(
    horizon_minutes: int = Query(60, ge=1, le=24 * 60),
    env: str = Query("dev", description="Hermes environment: dev|uat|prod (dev only is implemented safely)"),
) -> Dict[str, Any]:
    """
    Run a single BTC-USD decision cycle via the BTCOrchestrator.

    Notes:
      - In 'dev' and 'uat' environments this uses simulated market data
        and a no-op execution agent (no external broker calls).
      - 'prod' currently raises NotImplementedError because IBKR integration
        is not yet wired in.
    """
    orchestrator = BTCOrchestrator(
        OrchestratorConfig(
            symbol="BTC-USD",
            horizon_minutes=horizon_minutes,
            env=env,
        )
    )
    executed_trade = orchestrator.run_cycle()

    if executed_trade is None:
        return {
            "trade_executed": False,
            "message": "No trade plan generated for this cycle.",
        }

    return {
        "trade_executed": True,
        "executed_trade": asdict(executed_trade),
    }


if __name__ == "__main__":
    # Local development helper:
    #   python -m api.main
    # Then visit: http://127.0.0.1:8000/docs
    import uvicorn

    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)


