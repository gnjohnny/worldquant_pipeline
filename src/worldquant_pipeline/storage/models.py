"""SQLAlchemy 2.0 declarative models for research memory."""
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from worldquant_pipeline.storage.database import Base


def generate_uuid() -> str:
    """Generate a stable UUID string."""
    return str(uuid.uuid4())


# Use JSONB on PostgreSQL, standard JSON elsewhere (e.g. SQLite tests)
JsonType = JSON().with_variant(JSONB, "postgresql")


class ResearchHypothesis(Base):
    """Stores the scientific hypothesis, economic rationale, and intended direction."""

    __tablename__ = "research_hypotheses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(100), nullable=False)
    economic_rationale: Mapped[str] = mapped_column(Text, nullable=False)
    expected_direction: Mapped[str] = mapped_column(String(20), nullable=False)
    intended_horizon: Mapped[str] = mapped_column(String(50), nullable=False)
    confounders: Mapped[Any | None] = mapped_column(JsonType, nullable=True)
    falsification_test: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    candidates: Mapped[list["AlphaCandidate"]] = relationship(
        "AlphaCandidate", back_populates="hypothesis", cascade="all, delete-orphan"
    )


class DataField(Base):
    """Catalog of approved BRAIN data fields, timing conventions, and availability."""

    __tablename__ = "data_fields"

    field_key: Mapped[str] = mapped_column(String(100), primary_key=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    timing_delay: Mapped[int] = mapped_column(Integer, default=1)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    region: Mapped[str] = mapped_column(String(50), default="USA")
    permitted_use: Mapped[bool] = mapped_column(Boolean, default=True)


class AlphaCandidate(Base):
    """Stores individual alpha expressions, version lineage, and status."""

    __tablename__ = "alpha_candidates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    hypothesis_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("research_hypotheses.id", ondelete="CASCADE"), nullable=False
    )
    expression_raw: Mapped[str] = mapped_column(Text, nullable=False)
    expression_normalized: Mapped[str] = mapped_column(Text, nullable=False)
    expression_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    complexity_score: Mapped[int] = mapped_column(Integer, default=1)
    version: Mapped[int] = mapped_column(Integer, default=1)
    parent_candidate_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("alpha_candidates.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(50), default="PROPOSED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    hypothesis: Mapped["ResearchHypothesis"] = relationship("ResearchHypothesis", back_populates="candidates")
    experiments: Mapped[list["Experiment"]] = relationship(
        "Experiment", back_populates="candidate", cascade="all, delete-orphan"
    )
    decisions: Mapped[list["Decision"]] = relationship(
        "Decision", back_populates="candidate", cascade="all, delete-orphan"
    )


class Experiment(Base):
    """Records the exact simulation run parameters and timestamps."""

    __tablename__ = "experiments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    candidate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("alpha_candidates.id", ondelete="CASCADE"), nullable=False
    )
    universe: Mapped[str] = mapped_column(String(50), default="TOP3000")
    delay: Mapped[int] = mapped_column(Integer, default=1)
    neutralization: Mapped[str] = mapped_column(String(50), default="SUBINDUSTRY")
    decay: Mapped[int] = mapped_column(Integer, default=4)
    truncation: Mapped[float] = mapped_column(Numeric(6, 4), default=0.0100)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="COMPLETED")

    # Relationships
    candidate: Mapped["AlphaCandidate"] = relationship("AlphaCandidate", back_populates="experiments")
    metrics: Mapped[list["ExperimentMetric"]] = relationship(
        "ExperimentMetric", back_populates="experiment", cascade="all, delete-orphan"
    )


class ExperimentMetric(Base):
    """Stores individual simulation metrics returned from WorldQuant BRAIN."""

    __tablename__ = "experiment_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    experiment_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False
    )
    metric_name: Mapped[str] = mapped_column(String(50), nullable=False)
    metric_value: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="BRAIN_PLATFORM")
    context_json: Mapped[Any | None] = mapped_column(JsonType, nullable=True)

    # Relationships
    experiment: Mapped["Experiment"] = relationship("Experiment", back_populates="metrics")


class Decision(Base):
    """Auditable log of research decisions (APPROVED, REJECTED, NEEDS_REVISION)."""

    __tablename__ = "decisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    candidate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("alpha_candidates.id", ondelete="CASCADE"), nullable=False
    )
    decision: Mapped[str] = mapped_column(String(50), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    reviewer: Mapped[str] = mapped_column(String(100), default="HUMAN_RESEARCHER")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    candidate: Mapped["AlphaCandidate"] = relationship("AlphaCandidate", back_populates="decisions")
