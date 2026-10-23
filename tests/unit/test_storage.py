"""Unit tests for SQLAlchemy research memory models."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from worldquant_pipeline.storage.database import Base
from worldquant_pipeline.storage.models import (
    AlphaCandidate,
    DataField,
    Decision,
    Experiment,
    ExperimentMetric,
    ResearchHypothesis,
)


@pytest.fixture
def db_session():
    """In-memory SQLite session for testing model relationships and constraints."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    yield session
    session.close()


def test_research_memory_lifecycle(db_session):
    # 1. Create Data Field
    field = DataField(
        field_key="close",
        category="price_volume",
        description="Daily closing price",
        timing_delay=1,
        unit="USD",
        region="USA",
        permitted_use=True,
    )
    db_session.add(field)

    # 2. Create Hypothesis
    hypo = ResearchHypothesis(
        title="Short-term Momentum",
        domain="momentum",
        economic_rationale="Stocks with positive short-term returns continue upward due to attention.",
        expected_direction="positive",
        intended_horizon="5d",
        confounders=["earnings_announcements", "sector_drift"],
        falsification_test="Returns reverse over subsequent 20 days.",
    )
    db_session.add(hypo)
    db_session.commit()

    assert hypo.id is not None
    assert hypo.status == "ACTIVE"

    # 3. Create Alpha Candidate
    candidate = AlphaCandidate(
        hypothesis_id=hypo.id,
        expression_raw="ts_rank(close, 10)",
        expression_normalized="ts_rank(close, 10)",
        expression_hash="mock_hash_12345",
        complexity_score=2,
        version=1,
        status="VALIDATED",
    )
    db_session.add(candidate)
    db_session.commit()

    assert candidate.id is not None
    assert len(hypo.candidates) == 1

    # 4. Create Experiment & Metrics
    exp = Experiment(
        candidate_id=candidate.id,
        universe="TOP3000",
        delay=1,
        neutralization="SUBINDUSTRY",
        decay=4,
    )
    db_session.add(exp)
    db_session.commit()

    metric_sharpe = ExperimentMetric(
        experiment_id=exp.id,
        metric_name="sharpe",
        metric_value=1.850000,
        source="BRAIN_PLATFORM",
    )
    metric_turnover = ExperimentMetric(
        experiment_id=exp.id,
        metric_name="turnover",
        metric_value=0.220000,
        source="BRAIN_PLATFORM",
    )
    db_session.add_all([metric_sharpe, metric_turnover])
    db_session.commit()

    assert len(exp.metrics) == 2

    # 5. Record Decision
    decision = Decision(
        candidate_id=candidate.id,
        decision="APPROVED",
        reason="Consistent Sharpe > 1.5 with turnover < 30%. Passed subperiod checks.",
        reviewer="HUMAN_RESEARCHER",
    )
    db_session.add(decision)
    db_session.commit()

    assert len(candidate.decisions) == 1
    assert candidate.decisions[0].decision == "APPROVED"
