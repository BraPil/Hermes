"""
Hermes API package
==================

FastAPI application exposing a simple HTTP interface to the BTC orchestrator.

Initial endpoints are deliberately minimal and simulation-only:
  - GET /health          → basic liveness check
  - POST /btc/run_cycle  → run a single BTC-USD decision cycle in 'dev' mode

Future versions will:
  - Add endpoints for querying signals, trades and performance
  - Support different environments (uat/prod) once IBKR and QC are wired in
"""


