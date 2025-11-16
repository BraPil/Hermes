# Hermes State Log — 2025-11-16

Date: 2025-11-16  
Repository: `C:\Hermes`  
Scope: End-to-end status of Hermes with BTC engine, MCP integrations, and API surface.

---

## 1. High-Level Project State

- **Core Hermes (multi-asset)**
  - Original pipeline for equities/ETFs/crypto (AAPL, MSFT, NVDA, TSLA, AMZN, SQQQ, UVXY, SPXU, etc.).
  - Data ingestion modules for fundamentals, market psychology, and social sentiment.
  - Scoring engine producing composite scores and CSV outputs in `outputs/`.
  - Extensive documentation suite (INDEX, README, SYSTEM_OVERVIEW, CONTEXT_ENGINEERING_STRATEGY, PHASE_1 docs).

- **New Hermes–BTC Engine (multi-agent skeleton)**
  - Dedicated BTC-USD engine implemented as `btc_engine` package.
  - Layers A–D implemented as pluggable classes:
    - Layer A: `HistoricalPerformanceLayer` (trend/SMA-based prototype).
    - Layer B: `LivePatternLayer` (short-term momentum prototype).
    - Layer C: `GeoPoliticalLayer` (stub).
    - Layer D: `SentimentLayer` (stub).
  - Decision layer, strategies library, execution agent, feedback agent, and orchestrator implemented.
  - New FastAPI HTTP API surface in `api/` around the BTC orchestrator.

- **Environment & tooling**
  - MCP integrations in Cursor:
    - Hugging Face MCP server (for models/datasets like algorithmic_trading, trading-bot datasets).
    - Postman/HTTP MCP (generic REST / OpenAPI client).
    - Supabase MCP (database + tools; already added to account).
    - GitHub integration (for repo management).
  - Plan for dev/UAT with QuantConnect and prod with IBKR, wired through shared interfaces (`MarketDataClient`, `ExecutionAgent`, `Orchestrator`).

---

## 2. Legacy Hermes Components (Multi-Asset Engine)

### 2.1 Key Directories and Files

- `main.py`
  - Original entrypoint.
  - Currently set up to:
    - Define a custom watchlist (SQQQ, UVXY, SPXU, RNA, DYN, MSFT, GOOGL, INTC, AMD, GLD, RGTI, QBTS, IONQ, QUBT, QMCO, BTC-USD).
    - Fetch fundamentals via `data_ingestion.fundamentals.fetch_stock_data`.
    - Compute scores via `analytics.scoring.calculate_score`.
    - Fetch VIX/SP500 and Fear & Greed via `data_ingestion.psycho`.
    - Run Reddit sentiment via `data_ingestion.social` (subject to rate limits and account issues).
    - Generate reports via `outputs.report_generator.generate_report`.
    - Run some Git LFS commands at the end.

- `data_ingestion/`
  - `fundamentals.py`: Yahoo Finance fundamentals ingestion (`fetch_stock_data`).
  - `psycho.py`: VIX/SP500 time series and Fear & Greed index (`fetch_vix_and_sp500_data`, `update_fear_greed_log`).
  - `social.py`: Reddit-based sentiment pipeline (TextBlob + transformers; uses PRAW and env vars for Reddit).
  - `test_social.py`: Tests for social sentiment logic.

- `analytics/`
  - `scoring.py`: Fundamental scoring logic (0–70 base score, later adjusted by Fear & Greed).

- `outputs/`
  - CSVs:
    - `fundamentals_data.csv`
    - `fundamentals_scored.csv`
    - `vix_sp500_data.csv`
    - `fear_greed_log.csv`
    - `social_sentiment_log.csv`
    - `weighted_score.csv`
  - Python:
    - `report_generator.py`: Terminal and CSV report logic.
    - `weighted_score.py`: Score normalization/combining logic.

- Documentation (selected):
  - `00_START_HERE.txt`: Intro and quick navigation.
  - `INDEX.md`: Documentation index.
  - `README.md`: Overall summary and quick start.
  - `DIRECTORY_ANALYSIS.md`: Explains each file and data flow.
  - `SYSTEM_OVERVIEW.md`: Architecture diagrams and data flows.
  - `CONTEXT_ENGINEERING_STRATEGY.md`: Multi-phase roadmap.
  - `PHASE_1_IMPLEMENTATION.md`, `PHASES_1_2_3_MASTER_PLAN.md`, `STATUS.md`: Implementation detail and phase status.

### 2.2 Known Constraints (Legacy)

- Reddit and Yahoo APIs can be rate-limited or temporarily blocked.
- `social.py` is tightly coupled to Reddit/PRAW and environment variables.
- Data sources are partially scraping-based (Yahoo via `yfinance`).
- No dedicated real-time exchange integration yet for BTC.

---

## 3. Hermes–BTC Engine (New Multi-Agent Core)

### 3.1 Package Structure

- `btc_engine/__init__.py`
  - High-level description of BTC engine components and responsibilities.

- `btc_engine/interfaces.py`
  - Core dataclasses:
    - `LayerOutput`: timestamp, horizon, direction (-1/0/1), confidence [0,1], risk, extras.
    - `TradePlan`: timestamp, symbol, side (long/short), size, entry/SL/TP, horizon, metadata.
    - `ExecutedTrade`: broker_trade_id, plan, filled_price/size, status, fees, extras.
  - Abstract interfaces:
    - `BaseLayer`: `run() -> LayerOutput`.
    - `DecisionLayer`: `decide(layer_outputs: Dict[str, LayerOutput]) -> Optional[TradePlan]`.
    - `ExecutionAgent`: `execute(plan: TradePlan) -> ExecutedTrade`.
    - `FeedbackAgent`: `update_from_trade(executed_trade, price_path) -> None`.
    - `Orchestrator`: `run_cycle() -> Optional[ExecutedTrade]`.

### 3.2 Market Data

- `btc_engine/market_data.py`
  - `MarketDataClient` (ABC):
    - `get_recent_ohlcv(symbol, interval, limit) -> DataFrame` with OHLCV.
    - `get_latest_price(symbol) -> float`.
  - `SimulatedMarketDataClient`:
    - Generates a synthetic BTC random walk around an `anchor_price` using NumPy.
    - Used in `dev`/`uat` to avoid external dependencies.
  - Placeholders (not implemented yet, raise `NotImplementedError`):
    - `BinanceMarketDataClient`: future live exchange client.
    - `QuantConnectMarketDataClient`: for potential standalone UAT/harness.
    - `IBKRMarketDataClient`: for IBKR-based prod data via `ib_insync`.

### 3.3 Layers A–D

- `btc_engine/layers.py`
  - `LayerConfig`:
    - `symbol: str = "BTC-USD"`
    - `horizon_minutes: int = 60`
    - `market_data_client: Optional[MarketDataClient]`

  - **Layer A: `HistoricalPerformanceLayer`**
    - Uses `market_data_client.get_recent_ohlcv(symbol, "1h", 100)` if available.
    - Computes 20- and 50-period SMAs on closing prices.
    - Sets `direction`:
      - +1 if SMA(20) > SMA(50), -1 if SMA(20) < SMA(50), 0 if equal.
    - `confidence`: scaled by relative SMA distance, clipped to [0,1].
    - `risk`: recent std dev of returns.
    - If no market data or insufficient history, returns neutral with appropriate `extras["reason"]`.

  - **Layer B: `LivePatternLayer`**
    - Uses `get_recent_ohlcv(symbol, "5m", 50)`.
    - Computes short-term momentum: average of last few pct changes.
    - `direction`: sign of momentum; `confidence` scaled by magnitude; `risk` = std of recent returns.
    - Falls back to neutral if no client or insufficient history.

  - **Layer C: `GeoPoliticalLayer`** (stub)
    - Returns neutral `LayerOutput` with `extras["layer"] = "C"`.
    - To be extended with macro/regulatory event logic later.

  - **Layer D: `SentimentLayer`** (stub)
    - Returns neutral `LayerOutput` with `extras["layer"] = "D"`.
    - Will eventually ingest Crypto Fear & Greed, BTC sentiment models (e.g. TigerTrading/TradingBot), and on-chain proxies.

  - `run_all_layers(config: LayerConfig) -> Dict[str, LayerOutput]`
    - Convenience helper returning outputs for A, B, C, D.

### 3.4 Strategy Library

- `btc_engine/strategies.py`
  - `Strategy` (ABC):
    - `should_trade(layers: Dict[str, LayerOutput]) -> bool`.
    - `build_trade_plan(base_plan: TradePlan, layers: Dict[str, LayerOutput]) -> TradePlan`.
  - Concrete strategy shells (currently add metadata only, no change to direction/size):
    - `TrendFollowingStrategy` (`name="trend_following"`):
      - Intended to rely on Layers A (trend) & B (price action).
    - `MeanReversionStrategy` (`name="mean_reversion"`):
      - For future overbought/oversold and reversion logic.
    - `BreakoutStrategy` (`name="breakout"`):
      - For volatility expansion / range breakouts based on Layer B.
  - `default_strategies()`: returns dict with `"trend"`, `"mean_reversion"`, `"breakout"` mapped to instances.

### 3.5 Decision Layer

- `btc_engine/decision.py`
  - `DecisionConfig`:
    - `symbol: str = "BTC-USD"`
    - `max_position_size: float = 1.0` (in BTC).
    - `default_horizon_minutes: int = 60`
    - `strategy_names: Optional[List[str]] = None` (filter active strategies).

  - `SimpleDecisionLayer(DecisionLayerBase)`:
    - Aggregates outputs from layers:
      - Uses each layer's `direction` and `confidence` as weights.
      - Computes aggregate direction sign and average confidence.
      - If total weight/confidence is zero, returns `None` (no trade).
    - Position sizing:
      - `size = max_position_size * aggregate_confidence`.
    - Builds a base `TradePlan`:
      - `side = "long"` or `"short"`.
      - `entry_price`, `stop_loss`, `take_profit` currently set to `0.0`.
      - `metadata` includes `agg_confidence` and `layers_used`.
    - Strategy application:
      - Filters strategies by `strategy.should_trade(layers)`.
      - Sequentially calls `strategy.build_trade_plan(plan, layers)` to refine/annotate.
      - Adds `metadata["strategies"]` list to the plan.

### 3.6 Execution & Feedback

- `btc_engine/execution.py`
  - `ExecutionConfig`:
    - `symbol: str = "BTC-USD"`
  - `NoOpExecutionAgent(ExecutionAgentBase)`:
    - Simulates execution:
      - Generates `broker_trade_id = "SIM-{counter}"`.
      - Uses `plan.entry_price` as `filled_price`.
      - Sets status `"filled"`, `fees=0.0`, `extras["simulated"]=True`.
  - `IBKRExecutionAgent(ExecutionAgentBase)` (stub):
    - Constructor and `execute` both raise `NotImplementedError`.
    - Reserved for future `ib_insync`-based IBKR integration.

- `btc_engine/feedback.py`
  - `FeedbackConfig(symbol="BTC-USD")`.
  - `SimpleFeedbackAgent(FeedbackAgentBase)`:
    - Computes basic diagnostics from a provided `price_path` series:
      - PnL, MAE, MFE depending on long/short side.
      - Prints a diagnostics dict to stdout.
    - In future, will write to DB and update models.

### 3.7 Orchestrator

- `btc_engine/orchestrator.py`
  - `OrchestratorConfig`:
    - `symbol: str = "BTC-USD"`
    - `horizon_minutes: int = 60`
    - `env: str = "dev"` (dev|uat|prod).

  - `BTCOrchestrator(OrchestratorBase)`:
    - Reads `env` (and `HERMES_ENV` env var) to decide wiring:
      - `dev`:
        - `md_client = SimulatedMarketDataClient()`
        - `execution_agent = NoOpExecutionAgent`
      - `uat`:
        - For now, same as `dev` (placeholders for QuantConnect harness).
      - `prod`:
        - `md_client = IBKRMarketDataClient()` (NotImplemented).
        - `execution_agent = IBKRExecutionAgent` (NotImplemented).
    - Creates `LayerConfig` with `market_data_client`.
    - Instantiates:
      - `SimpleDecisionLayer(DecisionConfig(...))`
      - `execution_agent`
      - `SimpleFeedbackAgent(FeedbackConfig(...))`
    - `run_cycle()`:
      - Runs all layers.
      - Generates `TradePlan` via `decision.decide`.
      - If no plan: prints "[Orchestrator] No trade plan generated for this cycle." and returns `None`.
      - Else:
        - Executes plan via `execution_agent.execute`.
        - Constructs a dummy flat price path for now (no external data).
        - Calls `feedback.update_from_trade(executed_trade, price_path)`.
        - Returns `ExecutedTrade`.

### 3.8 BTC Entry Point

- `btc_main.py`
  - Reads `HERMES_ENV` env var (default "dev").
  - Instantiates `BTCOrchestrator(OrchestratorConfig(symbol="BTC-USD", horizon_minutes=60, env=env))`.
  - Runs one cycle via `run_cycle()`.
  - Output (as of now) shows feedback diagnostics such as:
    - `[Feedback] Trade diagnostics: {...}` or "No trade plan" depending on simulated signals.

---

## 4. FastAPI HTTP API Surface

- `api/__init__.py`
  - Documents purpose: HTTP interface for BTC orchestrator.

- `api/main.py`
  - Uses FastAPI to expose:
    - `GET /health`:
      - Returns `{"status": "ok"}`.
    - `POST /btc/run_cycle`:
      - Query parameters:
        - `horizon_minutes: int` (default 60, 1–1440).
        - `env: str` (default "dev").
      - Internally:
        - Creates `BTCOrchestrator` with given horizon/env.
        - Calls `run_cycle()`.
      - Response:
        - If no trade:
          - `{"trade_executed": false, "message": "No trade plan generated for this cycle."}`
        - If trade:
          - `{"trade_executed": true, "executed_trade": { ... asdict(ExecutedTrade) ... }}`
  - Can be run locally with:
    - `python -m api.main`
    - And explored via `http://127.0.0.1:8000/docs`.

---

## 5. Environment & Dependencies

- `requirements.txt` (current highlights)
  - Core:
    - `praw==7.7.1`
    - `textblob==0.17.1`
    - `pandas==2.1.4`
    - `python-dotenv==1.0.0`
    - `transformers==4.36.2`
    - `torch==2.1.2`
  - New additions:
    - `fastapi==0.115.0`
    - `uvicorn[standard]==0.30.0`
  - Implicit dependencies (used but originally not in requirements; they may already be installed from earlier instructions):
    - `yfinance`, `selenium`, `webdriver-manager`, `beautifulsoup4`, `tabulate`.

---

## 6. MCP, A2A, and External Systems Overview

### 6.1 MCP Servers / Integrations

- **Hugging Face MCP**
  - Configured in Cursor MCP settings with:
    - `"hf-mcp-server": { "url": "https://huggingface.co/mcp?login" }`
  - Purpose:
    - Search and inspect models/datasets/Spaces on Hugging Face directly from the IDE.
    - Examples leveraged:
      - [ParallelLLC/algorithmic_trading](https://huggingface.co/ParallelLLC/algorithmic_trading)
      - [TigerTrading/TradingBot](https://huggingface.co/TigerTrading/TradingBot)
      - [tuandunghcmut/bfcl-multi_turn_func_doc__trading_bot](https://huggingface.co/datasets/tuandunghcmut/bfcl-multi_turn_func_doc__trading_bot)
      - [bazarbroker/trading-bots](https://huggingface.co/datasets/bazarbroker/trading-bots)
      - [kapr/trading-bot-backtesting](https://huggingface.co/datasets/kapr/trading-bot-backtesting)
      - [Maksym-Lysyi/Meta-Llama-3.1-8B-Instruct-bnb-4bit-building_winning_algorithmic_trading_systems-HF](https://huggingface.co/Maksym-Lysyi/Meta-Llama-3.1-8B-Instruct-bnb-4bit-building_winning_algorithmic_trading_systems-HF)

- **Postman / HTTP MCP**
  - Installed as a generic HTTP/OpenAPI MCP client.
  - Purpose:
    - Call REST APIs from the assistant (brokers, data vendors, Hermes FastAPI).
    - Useful for testing `/btc/run_cycle` and future FastAPI endpoints.

- **Supabase MCP**
  - Already set up at the account level.
  - Purpose:
    - Directly query Supabase projects/DB from the assistant.
    - Planned usage:
      - Persist and query Hermes trades, signals, and backtests.

- **GitHub integration**
  - Already connected in Cursor.
  - Purpose:
    - Commit, push, and manage PRs for `C:\Hermes`.

### 6.2 Planned External Systems (Not Yet Wired in Code)

- **QuantConnect (Lean engine)**
  - Role:
    - Dev/UAT for strategies and signals.
    - Run BTC strategies as Lean algorithms that call Hermes for signals.

- **Interactive Brokers (IBKR)**
  - Role:
    - Production broker for BTC or BTC-related instruments via `ib_insync`.
  - To be implemented via:
    - `IBKRMarketDataClient` (real-time/historical data).
    - `IBKRExecutionAgent` (order placement, monitoring, and reconciliation).

---

## 7. Current Behavior Snapshot

- Running `python btc_main.py` in `C:\Hermes`:
  - Uses `HERMES_ENV` (default "dev") → simulated BTC data, no-op execution.
  - Often generates a `TradePlan` and `ExecutedTrade` from simulated signals.
  - Feedback prints trade diagnostics with zero or minimal PnL due to dummy price path.

- Running the API:
  - `python -m api.main` → launches FastAPI app on port 8000.
  - `POST /btc/run_cycle?horizon_minutes=60&env=dev`:
    - Triggers the same orchestrator logic via HTTP.

---

## 8. Summary

Hermes now has:

- A legacy multi-asset analysis engine with fundamentals, psycho, and Reddit sentiment.
- A new, modular Hermes–BTC engine with:
  - Well-defined interfaces for layers, decision, execution, feedback, and orchestrator.
  - Prototypical SMA/momentum-based Layers A & B using a simulated market data client.
  - Strategy abstraction for trend/mean-reversion/breakout.
  - Environment-aware orchestrator that distinguishes dev/uat/prod wiring.
  - A FastAPI HTTP layer for external A2A integration.
- MCP integrations (Hugging Face, HTTP/Postman, Supabase) + GitHub for repository management.

This file is the canonical snapshot of the system as of **2025-11-16**, and should be updated when significant architectural changes are made.


