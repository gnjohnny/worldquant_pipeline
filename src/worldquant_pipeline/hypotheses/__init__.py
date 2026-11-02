"""Hypothesis domain package."""
from worldquant_pipeline.hypotheses.cross_engine import (
    CrossDatasetCandidate,
    CrossDatasetEngine,
)
from worldquant_pipeline.hypotheses.importer import HypothesisImporter, IngestionReport
from worldquant_pipeline.hypotheses.prompts import generate_copilot_prompt
from worldquant_pipeline.hypotheses.schemas import (
    CandidateBatchInput,
    CandidateProposal,
    DecisionEnum,
    DecisionRecordInput,
    DirectionEnum,
    HypothesisProposal,
    SimulationMetricInput,
)

__all__ = [
    "CandidateBatchInput",
    "CandidateProposal",
    "CrossDatasetCandidate",
    "CrossDatasetEngine",
    "DecisionEnum",
    "DecisionRecordInput",
    "DirectionEnum",
    "HypothesisImporter",
    "HypothesisProposal",
    "IngestionReport",
    "SimulationMetricInput",
    "generate_copilot_prompt",
]
