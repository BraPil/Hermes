#PoC entry point that exercises Historical + Technical agents.

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.historical import YFinanceHistoricalPerformanceAgent
from agents.technical import YFinanceTechnicalIndicatorAgent

WATCHLIST = [
    "SQQQ",
    "UVXY",
    "SPXU",
    "RNA",
    "DYN",
    "MSFT",
    "GOOGL",
    "INTC",
    "AMD",
    "GLD",
    "RGTI",
    "QBTS",
    "IONQ",
    "QUBT",
    "QMCO",
    "BTC-USD",
]


def run_one(as_of: datetime) -> list[dict]:
    hist = YFinanceHistoricalPerformanceAgent()
    tech = YFinanceTechnicalIndicatorAgent()
    results: list[dict] = []
    for symbol in WATCHLIST:
        hv = hist.compute_features(symbol, as_of)
        tv = tech.compute_features(symbol, as_of)
        results.append(
            {
                "symbol": symbol,
                "timestamp": as_of.isoformat(),
                "historical": [fv.features for fv in hv],
                "technical": tv.features,
            }
        )
    return results


def main() -> None:
    now = datetime.utcnow()
    results = run_one(now)
    out_dir = ROOT / "outputs"
    out_dir.mkdir(exist_ok=True)
    path = out_dir / f"run_agents_poc_{now:%Y%m%d_%H%M%S}.json"
    path.write_text(json.dumps(results, indent=2))
    print(f"Saved {path}")


if __name__ == "__main__":
    main()