"""Unit tests for AlphaExistenceChecker and duplicate detection."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from worldquant_pipeline.evaluation.existence_checker import (
    AlphaExistenceChecker,
    ExistenceVerdict,
)
from worldquant_pipeline.expressions.canonicalize import (
    canonicalize_expression,
    compute_expression_hash,
)
from worldquant_pipeline.storage.database import Base
from worldquant_pipeline.storage.models import (
    AlphaCandidate,
    ResearchHypothesis,
)


@pytest.fixture
def db_session():
    """In-memory SQLite session for testing existence checking."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    yield session
    session.close()


def test_exact_duplicate_detection(db_session):
    hypo = ResearchHypothesis(
        title="Test Hypo",
        domain="test",
        economic_rationale="test",
        expected_direction="positive",
        intended_horizon="5d",
    )
    db_session.add(hypo)
    db_session.flush()

    raw_expr = "0.70 * group_rank(close, subindustry) + 0.30 * group_rank(volume, subindustry)"
    canon = canonicalize_expression(raw_expr)
    ehash = compute_expression_hash(canon)

    cand = AlphaCandidate(
        hypothesis_id=hypo.id,
        expression_raw=raw_expr,
        expression_normalized=canon,
        expression_hash=ehash,
        status="APPROVED",
    )
    db_session.add(cand)
    db_session.commit()

    # Check exact expression
    res = AlphaExistenceChecker.check_expression(raw_expr, db_session)
    assert res.is_exact_duplicate is True
    assert res.verdict == ExistenceVerdict.EXACT_DUPLICATE
    assert res.exact_match is not None
    assert res.exact_match.candidate_id == cand.id
    assert res.exact_match.status == "APPROVED"


def test_portfolio_collision_detection(db_session):
    hypo = ResearchHypothesis(
        title="Test Hypo",
        domain="test",
        economic_rationale="test",
        expected_direction="positive",
        intended_horizon="5d",
    )
    db_session.add(hypo)
    db_session.flush()

    # Active alpha using a specific primary driver field
    cand = AlphaCandidate(
        hypothesis_id=hypo.id,
        expression_raw="group_rank(actual_sales_value_quarterly, subindustry)",
        expression_normalized="group_rank(actual_sales_value_quarterly, subindustry)",
        expression_hash="hash123",
        status="VALIDATED",
    )
    db_session.add(cand)
    db_session.commit()

    # Different formula, but sharing the primary driver field with active portfolio alpha
    test_expr = "ts_decay_linear(actual_sales_value_quarterly, 10)"
    res = AlphaExistenceChecker.check_expression(test_expr, db_session)

    assert res.is_exact_duplicate is False
    assert res.verdict == ExistenceVerdict.HIGH_PORTFOLIO_COLLISION
    assert len(res.portfolio_collisions) >= 1
    assert res.portfolio_collisions[0].candidate_id == cand.id
    assert res.portfolio_collisions[0].status == "VALIDATED"


def test_virgin_alpha_safe_verdict(db_session):
    hypo = ResearchHypothesis(
        title="Test Hypo",
        domain="test",
        economic_rationale="test",
        expected_direction="positive",
        intended_horizon="5d",
    )
    db_session.add(hypo)
    db_session.flush()

    cand = AlphaCandidate(
        hypothesis_id=hypo.id,
        expression_raw="group_rank(close, subindustry)",
        expression_normalized="group_rank(close, subindustry)",
        expression_hash="hash456",
        status="APPROVED",
    )
    db_session.add(cand)
    db_session.commit()

    # Truly virgin unmined expression
    test_expr = "group_rank(ts_rank(call_breakeven_60, 20), market)"
    res = AlphaExistenceChecker.check_expression(test_expr, db_session)

    assert res.is_exact_duplicate is False
    assert res.verdict == ExistenceVerdict.SAFE_VIRGIN_ALPHA
    assert res.is_safe_to_simulate is True
    assert len(res.portfolio_collisions) == 0
