#Proof-of-concept runner for Hermes Phase 2 agents.

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

print("DEBUG ROOT", ROOT)
print("DEBUG sys.path[0]", sys.path[0])

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


def run_poc(as_of: datetime) -> list[dict]:
    historical_agent = YFinanceHistoricalPerformanceAgent()
    technical_agent = YFinanceTechnicalIndicatorAgent()

    results: list[dict] = []
    for symbol in WATCHLIST:
        hist_features = historical_agent.compute_features(symbol, as_of)
        tech_feature = technical_agent.compute_features(symbol, as_of)

        results.append(
            {
                "symbol": symbol,
                "timestamp": as_of.isoformat(),
                "historical": [fv.features for fv in hist_features],
                "technical": tech_feature.features,
            }
        )
    return results


def main() -> None:
    as_of = datetime.utcnow()
    results = run_poc(as_of)
    outputs_dir = ROOT / "outputs"
    outputs_dir.mkdir(exist_ok=True)
    out_file = outputs_dir / f"features_snapshot_{as_of:%Y%m%d_%H%M%S}.json"
    out_file.write_text(json.dumps(results, indent=2))

    print(f"[PoC] Feature snapshot written to {out_file}")
    for entry in results:
        print(
            f"{entry['symbol']}: "
            f"hist horizons={len(entry['historical'])}, "
            f"tech keys={len(entry['technical'])}"
        )


if __name__ == "__main__":
    main()

