"""
Hermes BTC Engine
=================

BTC-only multi-agent architecture:
  - LayerA: Historical performance learner
  - LayerB: Live pattern opportunity identifier
  - LayerC: Geo-political and macro pattern learner
  - LayerD: Sentiment and fear/greed learner
  - DecisionLayer: Combines A–D into trade signals
  - ExecutionAgent: Sends and verifies orders on a (future) paper account
  - FeedbackAgent: Compares predictions vs realised outcomes and closes the loop
  - Orchestrator: Coordinates all layers and agents

This package currently provides skeleton implementations and interfaces only.
Real models, data sources and broker connectivity will be wired in incrementally.
"""


