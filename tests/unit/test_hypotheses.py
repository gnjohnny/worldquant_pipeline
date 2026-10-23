"""Unit tests for hypothesis schemas, prompt generation, importer, and quality gates."""
import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from worldquant_pipeline.evaluation.gates import QualityGateRunner
from worldquant_pipeline.hypotheses.importer import HypothesisImporter
from worldquant_pipeline.hypotheses.prompts import generate_copilot_prompt
from worldquant_pipeline.hypotheses.schemas import (
    DirectionEnum,
    HypothesisProposal,
)
from worldquant_pipeline.storage.database import Base


@pytest.fixture
def db_session():
    """In-memory SQLite session for testing importer."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    yield session
    session.close()


class TestHypothesisSchemas:
    def test_valid_hypothesis_schema(self):
        payload = {
            "title": "Short-term Reversal",
            "domain": "price_volume",
            "economic_rationale": "Liquidity demand creates transient price overshoots.",
            "expected_direction": "negative",
            "intended_horizon": "1d",
            "confounders": ["earnings_surprises"],
            "candidates": [
                {
                    "expression": "-ts_delta(close, 1)",
                    "rationale": "1-day price delta reversal",
                    "expected_direction": "negative",
                }
            ],
        }
        hypo = HypothesisProposal.model_validate(payload)
        assert hypo.title == "Short-term Reversal"
        assert hypo.expected_direction == DirectionEnum.NEGATIVE
        assert len(hypo.candidates) == 1

    def test_empty_candidates_fails(self):
        payload = {
            "title": "Invalid Hypothesis",
            "domain": "price_volume",
            "economic_rationale": "Missing candidates.",
            "expected_direction": "positive",
            "intended_horizon": "5d",
            "candidates": [],
        }
        with pytest.raises(ValidationError):
            HypothesisProposal.model_validate(payload)


class TestPromptGeneration:
    def test_prompt_contains_catalog(self):
        text = generate_copilot_prompt(domain="momentum")
        assert "Research Task: WorldQuant BRAIN Alpha Hypotheses" in text
        assert "momentum" in text
        assert "ts_rank" in text
        assert "close" in text
        assert "Required JSON Output Schema" in text


class TestHypothesisImporter:
    def test_importer_registers_valid_and_catches_invalid(self, db_session):
        data = {
            "hypotheses": [
                {
                    "title": "Momentum vs Reversal",
                    "domain": "price_volume",
                    "economic_rationale": "Testing short lookbacks.",
                    "expected_direction": "positive",
                    "intended_horizon": "5d",
                    "candidates": [
                        {"expression": "ts_rank(close, 10)"},
                        {"expression": "ts_rank(close, 10)"},  # Duplicate
                        {"expression": "ts_rank(unknown_token_xyz, 10)"},  # Unknown field
                    ],
                }
            ]
        }
        importer = HypothesisImporter(db_session)
        report = importer.ingest_data(data)

        assert report.total_candidates == 3
        assert report.valid_candidates == 1
        assert report.duplicates == 1
        assert report.syntax_errors == 1
        assert len(report.registered_candidates) == 1
        assert len(report.errors) == 2


class TestQualityGates:
    def test_passing_metrics(self):
        runner = QualityGateRunner()
        metrics = {"sharpe": 1.65, "turnover": 0.25, "fitness": 1.40}
        res = runner.evaluate_metrics(metrics)
        assert res.passed is True
        assert len(res.failures) == 0

    def test_failing_sharpe_and_turnover(self):
        runner = QualityGateRunner()
        metrics = {"sharpe": 0.85, "turnover": 0.85}  # Low Sharpe, high turnover
        res = runner.evaluate_metrics(metrics)
        assert res.passed is False
        assert len(res.failures) >= 2
