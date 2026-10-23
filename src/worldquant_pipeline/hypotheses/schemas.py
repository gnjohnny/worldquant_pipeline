"""Pydantic schemas for structured hypotheses and candidate alpha expressions."""
from enum import Enum

from pydantic import BaseModel, Field


class DirectionEnum(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"


class DecisionEnum(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    NEEDS_REVISION = "NEEDS_REVISION"


class CandidateProposal(BaseModel):
    """An individual candidate expression proposal within a hypothesis."""
    expression: str = Field(..., description="Alpha expression in WorldQuant BRAIN DSL")
    rationale: str | None = Field(default=None, description="Specific variation rationale")
    expected_direction: DirectionEnum = Field(
        default=DirectionEnum.POSITIVE, description="Expected correlation with forward returns"
    )


class HypothesisProposal(BaseModel):
    """A structured economic hypothesis proposing a small family of candidate expressions."""
    title: str = Field(..., description="Short descriptive title of the hypothesis")
    domain: str = Field(..., description="Research domain (e.g. momentum, liquidity, analyst)")
    economic_rationale: str = Field(..., description="Falsifiable economic or behavioral mechanism")
    expected_direction: DirectionEnum = Field(..., description="Overall expected direction")
    intended_horizon: str = Field(..., description="Target holding horizon (e.g. 1d, 5d, 20d)")
    confounders: list[str] = Field(default_factory=list, description="Known risk confounders")
    falsification_test: str | None = Field(default=None, description="Test that would disprove the idea")
    candidates: list[CandidateProposal] = Field(
        ..., min_length=1, description="Family of related candidate expressions"
    )


class CandidateBatchInput(BaseModel):
    """Batch payload containing one or more hypothesis proposals."""
    hypotheses: list[HypothesisProposal] = Field(..., min_length=1)


class SimulationMetricInput(BaseModel):
    """Platform simulation metrics returned by WorldQuant BRAIN."""
    sharpe: float = Field(..., description="Information ratio / Sharpe ratio")
    turnover: float = Field(..., description="Daily portfolio turnover fraction (0.0 to 1.0+)")
    fitness: float | None = Field(default=None, description="WorldQuant BRAIN fitness score")
    returns: float | None = Field(default=None, description="Annualized or total return")
    drawdown: float | None = Field(default=None, description="Maximum drawdown fraction")
    margin: float | None = Field(default=None, description="Average profit margin per dollar traded")


class DecisionRecordInput(BaseModel):
    """Audit record for a manual or platform-informed alpha decision."""
    decision: DecisionEnum = Field(..., description="Decision verdict")
    reason: str = Field(..., min_length=5, description="Mandatory detailed reason for the decision")
    reviewer: str = Field(default="HUMAN_RESEARCHER", description="Name/role of reviewer")
