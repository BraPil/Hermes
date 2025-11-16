# Hermes Restart Protocol (BTC-Focused) — 2025-11-16

Purpose: Provide a concise checklist and index so that, after any restart or context loss, we can quickly restore full awareness of the current Hermes state — especially the Hermes–BTC engine — and resume work without re-discovery.

This file is meant to be **stable and updated over time**, while dated state logs (e.g. `hermes_state_log_2025_11_16.md`) capture point-in-time snapshots.

---

## 0. One-Page TL;DR

1. **Repo**: `C:\Hermes` (this is the canonical, consolidated repository).
2. **Entry points**:
   - Legacy multi-asset pipeline: `python main.py`
   - BTC orchestrator (local script): `python btc_main.py`
   - BTC API (FastAPI): `python -m api.main` → `http://127.0.0.1:8000/docs`
3. **BTC environment switch**:
   - `HERMES_ENV=dev|uat|prod` (dev is fully safe; prod wiring is stubbed).
4. **Key new package**: `btc_engine` (layers A–D, strategies, decision, execution, feedback, orchestrator).
5. **State snapshot docs**:
   - Latest: `hermes_state_log_2025_11_16.md` (full architecture + context as of that date).

---

## 1. Files to Read First After a Restart

When you reopen the project, read/skim these in order to rebuild context quickly:

1. `00_START_HERE.txt`
   - Legacy Hermes overview and navigation.
2. `INDEX.md`
   - Documentation index.
3. `hermes_state_log_2025_11_16.md`
   - Detailed snapshot of the current BTC engine, MCP/A2A integrations, and architecture.
4. `HERMES_RESTART_PROTOCOL.md` (this file)
   - The protocol and checklists you’re reading now.

If focusing on BTC only:

5. `btc_engine/interfaces.py` (interfaces)
6. `btc_engine/layers.py` (Layer A–D implementations)
7. `btc_engine/orchestrator.py` (environment wiring)
8. `api/main.py` (HTTP API surface)

---

## 2. Minimal Environment Rebuild Checklist

Assuming the repo is cloned but the environment is fresh or has been reset:

1. **Clone / pull the repo**
   - `git clone <repo-url> C:\Hermes` (or `git pull` if it already exists).

2. **Create and activate Python environment** (if not already)
   - Example (virtualenv or venv; adapt to your setup):
     - `python -m venv .venv`
     - `.\.venv\Scripts\activate` (Windows)

3. **Install dependencies**
   - From `C:\Hermes`:
     - `pip install -r requirements.txt`

4. **(Legacy Hermes only) `.env` and outputs**
   - `.env` file for Reddit (optional / legacy, may be skipped if Reddit is not used).
   - Ensure `outputs/` directory exists (it already does in this repo).

5. **Run basic smoke tests**
   - `python btc_main.py` (should run with simulated BTC data in `dev` mode).
   - `python -m api.main` and hit `GET /health` and `POST /btc/run_cycle` in a browser or Postman.

If all succeed, the environment is essentially restored.

---

## 3. BTC Engine Index (Where Things Live)

- **Architecture & interfaces**
  - `btc_engine/interfaces.py`
    - `LayerOutput`, `TradePlan`, `ExecutedTrade`.
    - `BaseLayer`, `DecisionLayer`, `ExecutionAgent`, `FeedbackAgent`, `Orchestrator`.

- **Market data**
  - `btc_engine/market_data.py`
    - `MarketDataClient` (abstract).
    - `SimulatedMarketDataClient` (used in dev/uat).
    - `BinanceMarketDataClient`, `QuantConnectMarketDataClient`, `IBKRMarketDataClient` (placeholders).

- **Layers A–D**
  - `btc_engine/layers.py`
    - `HistoricalPerformanceLayer` (Layer A).
    - `LivePatternLayer` (Layer B).
    - `GeoPoliticalLayer` (Layer C, stub).
    - `SentimentLayer` (Layer D, stub).
    - `LayerConfig`, `run_all_layers`.

- **Strategies**
  - `btc_engine/strategies.py`
    - `Strategy` base class.
    - `TrendFollowingStrategy`, `MeanReversionStrategy`, `BreakoutStrategy`.
    - `default_strategies()` registry.

- **Decision logic**
  - `btc_engine/decision.py`
    - `DecisionConfig`.
    - `SimpleDecisionLayer`: aggregates layer outputs and calls strategies.

- **Execution & feedback**
  - `btc_engine/execution.py`
    - `ExecutionConfig`.
    - `NoOpExecutionAgent` (simulated).
    - `IBKRExecutionAgent` (placeholder).
  - `btc_engine/feedback.py`
    - `FeedbackConfig`.
    - `SimpleFeedbackAgent` (prints diagnostics).

- **Orchestrator / entrypoint**
  - `btc_engine/orchestrator.py`
    - `OrchestratorConfig`.
    - `BTCOrchestrator`:
      - Chooses `MarketDataClient` and `ExecutionAgent` based on `env`.
  - `btc_main.py`
    - Reads `HERMES_ENV` and runs one orchestrator cycle.

---

## 4. API / A2A Index

- **FastAPI app**
  - File: `api/main.py`
  - App: `app = FastAPI(...)`
  - Endpoints:
    - `GET /health` → `{ "status": "ok" }`
    - `POST /btc/run_cycle?horizon_minutes=&env=` → runs `BTCOrchestrator.run_cycle()`.

- **Local dev commands**
  - From `C:\Hermes`:
    - Run API:
      - `python -m api.main`
    - View docs:
      - `http://127.0.0.1:8000/docs`
    - Call via curl/Postman:
      - `POST http://127.0.0.1:8000/btc/run_cycle?horizon_minutes=60&env=dev`

---

## 5. MCP / External Integration Index

These are configured in Cursor/Cloud settings, not in the repo, but are essential context for restarts:

- **Hugging Face MCP**
  - Purpose:
    - Rapid exploration of models, datasets, and Spaces relevant to algorithmic trading.
  - Example relevant resources:
    - `ParallelLLC/algorithmic_trading` (FinRL + Alpaca system).
    - `TigerTrading/TradingBot` (trading sentiment model).
    - `tuandunghcmut/bfcl-multi_turn_func_doc__trading_bot` (multi-turn function docs dataset).

- **Postman/HTTP MCP**
  - Purpose:
    - Generic HTTP/OpenAPI client tools to talk to:
      - Hermes FastAPI.
      - Future broker/data APIs.

- **Supabase MCP**
  - Purpose:
    - DB and project access for logging and analysis.
  - Future:
    - Store Hermes trades, signals, backtests and query them via MCP.

- **GitHub integration**
  - Purpose:
    - Manage the `C:\Hermes` repository (commits, pushes, PRs).

---

## 6. Restart Scenarios & What To Check

### 6.1 “Hard” Restart (New Machine / Environment)

1. **Clone repo** → `C:\Hermes`.
2. **Create venv / install requirements**.
3. **Run `python btc_main.py`**:
   - If it executes without import errors and prints feedback diagnostics, BTC engine is alive in dev mode.
4. **Run API** → `python -m api.main` and check `/health`.
5. **Optionally restore Supabase env**:
   - Ensure any environment variables or configs for Supabase are available (if/when DB integration is done).

### 6.2 “Soft” Restart (Cursor / MCP context lost)

1. Open `HERMES_RESTART_PROTOCOL.md` and `hermes_state_log_2025_11_16.md`.
2. Confirm MCP settings in Cursor:
   - Hugging Face MCP, Postman/HTTP MCP, Supabase MCP, GitHub integrations.
3. Re-open key code files for BTC engine:
   - `btc_engine/interfaces.py`, `layers.py`, `decision.py`, `execution.py`, `feedback.py`, `orchestrator.py`.
4. Run quick smoke:
   - `python btc_main.py` or `POST /btc/run_cycle` via Postman MCP.

---

## 7. Git Workflow (For Future Changes)

1. **Before coding**
   - `git pull` to ensure up-to-date.

2. **During coding**
   - Keep changes focused (e.g., add a new strategy, wire IBKRMarketDataClient).

3. **After changes**
   - `python -m api.main` (optional) and quick endpoint checks.
   - `python btc_main.py` to ensure orchestrator still runs.
   - `git status` to verify changed files.

4. **Commit & push**
   - `git add .`
   - `git commit -m "Describe the change (e.g., Add new BTC strategy X)"`
   - `git push`

This ensures that any significant milestone has a corresponding Git commit that can be checked out after a restart.

---

## 8. How To Use This Protocol Going Forward

- After each major architectural shift (new broker integration, new RL layer, major strategy library change):
  1. Update `hermes_state_log_<date>.md` with a fresh snapshot.
  2. Update this `HERMES_RESTART_PROTOCOL.md` if:
     - Entry points change.
     - New critical packages are added.
     - MCP/A2A patterns change (e.g., new API surface, new DB).

- When returning to the project after a break:
  - Start with this file + the latest `hermes_state_log_*` to reconstruct context in minutes instead of hours.


