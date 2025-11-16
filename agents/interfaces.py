from __future__ import annotations


#Core interfaces for the Hermes multi-agent system.

#These provide a stable abstraction layer for:
#- (a) IngestionAgent
#- (b) OrchestrationAgent
#- (c) HistoricalPerformanceAgent
#- (d) TechnicalIndicatorAgent
#- (e) PsychoSocialAgent
#- (f) MacroEconomicAgent
#- (y) LearningEvaluationAgent
#- (z) PredictionAgent

#Concrete implementations can live in separate modules (e.g. agents/ingestion_yf.py)
#without changing the rest of the codebase.


from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


@dataclass
class Event:
    #Base event type flowing through the system.

    symbol: str
    ts: datetime
    source: str  # e.g. "YF_PRICE", "REDDIT", "NEWS", "MACRO"
    payload: Dict[str, Any]


@dataclass
class FeatureVector:
    #Model-ready features for a single symbol at a specific time.

    symbol: str
    ts: datetime
    features: Dict[str, float]
    meta: Optional[Dict[str, Any]] = None


@dataclass
class Prediction:
    #Prediction + metadata from the ML Prediction Agent (z).

    symbol: str
    ts: datetime
    horizon: str  # e.g. "1d", "1w", "1m"
    expected_return: float
    prob_up: float
    prob_down: float
    confidence: float
    model_id: str
    extra: Optional[Dict[str, Any]] = None


@dataclass
class Outcome:
    #Realized outcome for a prior prediction (used by Learning/Eval agent y).

    symbol: str
    ts_pred: datetime
    ts_outcome: datetime
    realized_return: float
    label: int
    prediction: Prediction


class Agent(ABC):
    #Base interface for all agents in the Hermes multi-agent system.

    @abstractmethod
    def handle_event(self, event: Event) -> None:
        #Ingest a single event.

    @abstractmethod
    def tick(self, as_of: datetime) -> None:
        #Periodic heartbeat to perform scheduled work.


class IngestionAgent(Agent):
    #Pulls raw data, normalizes it, and emits standardized events.

    @abstractmethod
    def register_symbol(self, symbol: str) -> None:
        #Register a symbol (stock, ETF, crypto) to ingest data for.

    @abstractmethod
    def start_streams(self) -> None:
        #Start all configured live/historical data streams.

    @abstractmethod
    def stop_streams(self) -> None:
        #Stop all running data streams.


class OrchestrationAgent(Agent):
    #Coordinates feature agents (c–f), prediction agent (z), and learning agent (y).
    
    @abstractmethod
    def get_symbol_state(self, symbol: str) -> Dict[str, Any]:
        #Return current orchestration state for a symbol.

    @abstractmethod
    def request_features(self, symbol: str, as_of: datetime) -> List[FeatureVector]:
        #Trigger feature computation and aggregate results.


class HistoricalPerformanceAgent(Agent):
    #Multi-horizon historical analysis (all, 12m, 4w, 7d, 24h).

    @abstractmethod
    def compute_features(
        self,
        symbol: str,
        as_of: datetime,
        horizons: Sequence[str] = ("all", "12m", "4w", "7d", "24h"),
    ) -> List[FeatureVector]:
        #Compute historical performance features.


class TechnicalIndicatorAgent(Agent):
    #Computes technical indicators (Bollinger, RSI, MACD, etc.).

    @abstractmethod
    def compute_features(self, symbol: str, as_of: datetime) -> FeatureVector:
        #Compute technical indicator features.


class PsychoSocialAgent(Agent):
    #Analyzes psycho-social context (sentiment, narratives, intensity).

    @abstractmethod
    def compute_features(self, symbol: str, as_of: datetime) -> FeatureVector:
        #Compute psycho-social features.

    @abstractmethod
    def get_recent_events(self, symbol: str, window: str = "7d") -> List[Event]:
        #Return recent psycho-social events for explainability.


class MacroEconomicAgent(Agent):
    #Tracks macro/sector context and regime flags.

    @abstractmethod
    def compute_features(self, symbol: str, as_of: datetime) -> FeatureVector:
        #Compute macro/sector features.

    @abstractmethod
    def current_regime(self) -> Dict[str, Any]:
        #Return current global macro regime state.


class LearningEvaluationAgent(Agent):
    #Backtesting, evaluation, and model suggestion agent.

    @abstractmethod
    def record_prediction_and_outcome(self, outcome: Outcome) -> None:
        #Record a prediction vs outcome pair.

    @abstractmethod
    def run_backtest(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        config_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        #Run a walk-forward backtest.

    @abstractmethod
    def suggest_model_configs(self, top_k: int = 3) -> List[Dict[str, Any]]:
        #Suggest new model configurations.

    @abstractmethod
    def select_production_model(self) -> str:
        #Return the model_id to use in production.


class PredictionAgent(Agent):
    #Consumes features, produces predictions, and handles training/versioning.

    @abstractmethod
    def predict(self, features: FeatureVector) -> Prediction:
        #Produce a prediction for the given feature vector.

    @abstractmethod
    def batch_predict(self, features_list: List[FeatureVector]) -> List[Prediction]:
        #Produce predictions for a batch of feature vectors.

    @abstractmethod
    def train(
        self,
        symbol: str,
        training_data: Iterable[Tuple[FeatureVector, Outcome]],
        config: Dict[str, Any],
    ) -> str:
        #Train or fine-tune a model; return model_id.

    @abstractmethod
    def set_active_model(self, model_id: str) -> None:
        #Set the active model used for real-time predictions.

    @abstractmethod
    def get_active_model(self) -> str:
        #Return the current active model_id.

from __future__ import annotations


#Core interfaces for the Hermes multi‑agent system.

#These provide a stable abstraction layer for:
#- (a) IngestionAgent
#- (b) OrchestrationAgent
#- (c) HistoricalPerformanceAgent
#- (d) TechnicalIndicatorAgent
#- (e) PsychoSocialAgent
#- (f) MacroEconomicAgent
#- (y) LearningEvaluationAgent
#- (z) PredictionAgent

#Concrete implementations can live in separate modules (e.g. agents/ingestion_yf.py)
#without changing the rest of the codebase.

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Core data types (events, features, predictions)
# ---------------------------------------------------------------------------


@dataclass
class Event:
    #Base event type flowing through the system.

    #Subclasses or payloads should add domain‑specific fields
    #(e.g. price bar, news item, Reddit post).

    #All events must be time‑stamped and symbol‑scoped.

    symbol: str
    ts: datetime
    source: str  # e.g. "YF_PRICE", "REDDIT", "NEWS", "MACRO"
    payload: Dict[str, Any]


@dataclass
class FeatureVector:
    #Model‑ready features for a single symbol at a specific time.

    #This is the canonical representation of inputs to prediction models.

    symbol: str
    ts: datetime
    features: Dict[str, float]  # flat numeric features for model input
    meta: Optional[Dict[str, Any]] = None  # optional extra info (regime tags, etc.)


@dataclass
class Prediction:
    #Prediction + metadata from the ML Prediction Agent (z).

    #The exact semantics of expected_return / prob_up / prob_down are left
    #to the concrete implementation, but must be self‑consistent.

    symbol: str
    ts: datetime
    horizon: str  # e.g. "1d", "1w", "1m"
    expected_return: float
    prob_up: float
    prob_down: float
    confidence: float
    model_id: str  # which model/variant produced this
    extra: Optional[Dict[str, Any]] = None


@dataclass
class Outcome:
    #Realized outcome for a prior prediction (used by Learning/Eval agent y).

    #This is the atomic item used for backtesting and model evaluation.

    symbol: str
    ts_pred: datetime  # when we predicted
    ts_outcome: datetime  # when we measure outcome
    realized_return: float
    label: int  # e.g. 1 for up, 0 for down
    prediction: Prediction


# ---------------------------------------------------------------------------
# Base agent protocol
# ---------------------------------------------------------------------------


class Agent(ABC):
    #Base interface for all agents in the Hermes multi‑agent system.
    #Agents communicate via Event / FeatureVector / Prediction objects and
    #are orchestrated by higher‑level components.
    

    @abstractmethod
    def handle_event(self, event: Event) -> None:
        #Ingest a single event (from ingestion, other agents, or backtester).
        #Implementations should be idempotent and fast; any heavy work can be
        #deferred to `tick` or background tasks.

    @abstractmethod
    def tick(self, as_of: datetime) -> None:
        #Periodic heartbeat; perform scheduled work (e.g. compute features,
        #flush buffers, emit messages).
        #`as_of` is the logical time for which the agent should update its state.


# ---------------------------------------------------------------------------
# (a) Ingestion Agent / Pipeline
# ---------------------------------------------------------------------------


class IngestionAgent(Agent):
    #Ingestion agent responsible for pulling raw data, normalizing it,
    #and emitting standardized Event objects onto the internal bus.
    

    @abstractmethod
    def register_symbol(self, symbol: str) -> None:
        #Register a symbol (stock, ETF, crypto) to ingest data for.

    @abstractmethod
    def start_streams(self) -> None:
        #Start all configured live / historical data streams.

    @abstractmethod
    def stop_streams(self) -> None:
        #Stop all running data streams and clean up resources.


# ---------------------------------------------------------------------------
# (b) Orchestration Agent (front‑end coordinator)
# ---------------------------------------------------------------------------


class OrchestrationAgent(Agent):
    #Per‑symbol orchestration agent that coordinates feature agents (c–f),
    #the ML Prediction Agent (z), and the Learning/Eval Agent (y).

    #Responsibilities:
    #- Maintain real‑time state per symbol.
    #- Decide when to request updates from c/d/e/f.
    #- Aggregate features and route to z.
    #- Receive predictions from z and forward outcomes to y.
    

    @abstractmethod
    def get_symbol_state(self, symbol: str) -> Dict[str, Any]:
        #Return current orchestration state for a symbol
        #(regime, last prediction, risk flags, etc.).

    @abstractmethod
    def request_features(self, symbol: str, as_of: datetime) -> List[FeatureVector]:
        #Trigger feature computation from c/d/e/f for the given symbol and time,
        #and return aggregated feature vectors for downstream use by z.


# ---------------------------------------------------------------------------
# (c) Historical Performance Analyst
# ---------------------------------------------------------------------------


class HistoricalPerformanceAgent(Agent):
    #Agent responsible for multi‑horizon historical performance analysis
    #for a single symbol (all‑time, 12m, 4w, 7d, 24h).

    #Produces:
    #- Return / volatility / drawdown metrics.
    #- Regime classification (trend, mean‑reversion, range‑bound).
    #- Time‑horizon‑specific FeatureVectors.
    

    @abstractmethod
    def compute_features(
        self,
        symbol: str,
        as_of: datetime,
        horizons: Sequence[str] = ("all", "12m", "4w", "7d", "24h"),
    ) -> List[FeatureVector]:
        #Compute historical performance features for the given symbol and horizons.


# ---------------------------------------------------------------------------
# (d) Technical Indicator Agent
# ---------------------------------------------------------------------------


class TechnicalIndicatorAgent(Agent):
    #Agent that computes technical indicators (Bollinger Bands, RSI, MACD,
    #support/resistance, trend measures) for a symbol.
    

    @abstractmethod
    def compute_features(self, symbol: str, as_of: datetime) -> FeatureVector:
        #Compute technical indicator features for the symbol at time `as_of`.


# ---------------------------------------------------------------------------
# (e) Psycho‑Social Agent
# ---------------------------------------------------------------------------


class PsychoSocialAgent(Agent):
    #Agent that analyzes psycho‑social context for a symbol.

    #Inputs:
    #- Reddit posts/comments
    #- News headlines/summaries
    #- Social/media sentiment

    #Outputs:
    #- Sentiment scores (short/long term).
    #- Narrative/topic features.
    #- Engagement and intensity metrics.
    

    @abstractmethod
    def compute_features(self, symbol: str, as_of: datetime) -> FeatureVector:
        #Compute psycho‑social features for the symbol at time `as_of`.

    @abstractmethod
    def get_recent_events(self, symbol: str, window: str = "7d") -> List[Event]:
        
        #Return recent psycho‑social events used to compute features
        #(for explainability and debugging).
        


# ---------------------------------------------------------------------------
# (f) Political/Economic (Macro) Agent
# ---------------------------------------------------------------------------


class MacroEconomicAgent(Agent):
    #Agent that tracks political and macroeconomic context.

    #Inputs:
    #- Macro data (inflation, rates, GDP…)
    #- Sector‑level indicators
    #- Regulatory and geopolitical events

    #Outputs:
    #- Macro regime labels (risk‑on/off, uncertainty).
    #- Sector risk scores.
    #- Event flags (FED_DAY, EARNINGS_WEEK, etc.).
    

    @abstractmethod
    def compute_features(self, symbol: str, as_of: datetime) -> FeatureVector:
        #Compute macro/sector features relevant to a given symbol at time `as_of`.

    @abstractmethod
    def current_regime(self) -> Dict[str, Any]:
        #Return the current global macro regime and key indicators.


# ---------------------------------------------------------------------------
# (y) Learning & Evaluation Agent (Backtesting / AB‑testing brain)
# ---------------------------------------------------------------------------


class LearningEvaluationAgent(Agent):
    #Agent responsible for:
    #- Backtesting (walk‑forward) on historical data.
    #- Evaluating predictions vs outcomes.
    #- Proposing new model configs / hyperparameters.
    #- Running A/B tests and selecting best‑performing models.
    

    @abstractmethod
    def record_prediction_and_outcome(self, outcome: Outcome) -> None:
        #Record a prediction vs outcome pair for later analysis.

    @abstractmethod
    def run_backtest(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        config_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        #Run a walk‑forward backtest for the given symbol and date range.
        #Returns:
        #    A dictionary of evaluation metrics (Sharpe, drawdown, hit rate, etc.).

    @abstractmethod
    def suggest_model_configs(self, top_k: int = 3) -> List[Dict[str, Any]]:
        #Propose new or improved model configurations for the ML Prediction Agent (z)
        #based on historical performance and current regime.

    @abstractmethod
    def select_production_model(self) -> str:
        #Return the model_id of the configuration that should be considered
        #'production' for real‑time predictions.


# ---------------------------------------------------------------------------
# (z) ML Prediction Agent (Back‑end model brain)
# ---------------------------------------------------------------------------


class PredictionAgent(Agent):
    #Agent that consumes feature vectors (from c/d/e/f), plus orchestration state (b),
    #and produces probabilistic forecasts and suggested actions.
    #It must also support training and model versioning to integrate with
    #the Learning & Evaluation Agent (y).
    

    @abstractmethod
    def predict(self, features: FeatureVector) -> Prediction:
        #Produce a prediction for the given feature vector.

    @abstractmethod
    def batch_predict(self, features_list: List[FeatureVector]) -> List[Prediction]:
        #Produce predictions for a batch of feature vectors.

    @abstractmethod
    def train(
        self,
        symbol: str,
        training_data: Iterable[Tuple[FeatureVector, Outcome]],
        config: Dict[str, Any],
    ) -> str:
        
        #Train (or fine‑tune) a model for a given symbol and configuration.

        #Returns:
        #    model_id: Identifier for the trained model variant.
        

    @abstractmethod
    def set_active_model(self, model_id: str) -> None:
        #Set the active model used for real‑time predictions.

    @abstractmethod
    def get_active_model(self) -> str:
        #Return the current active model_id.


