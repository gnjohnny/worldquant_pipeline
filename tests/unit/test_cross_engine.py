"""Unit tests for the v2 Cross-Dataset Alpha Engine."""
import json
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from worldquant_pipeline.hypotheses.cross_engine import (
    CrossDatasetCandidate,
    CrossDatasetEngine,
)
from worldquant_pipeline.hypotheses.importer import HypothesisImporter
from worldquant_pipeline.storage.database import Base
from worldquant_pipeline.storage.models import AlphaCandidate, ResearchHypothesis


@pytest.fixture
def memory_db_session():
    """Create an in-memory SQLite database session for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    try:
        yield session
    finally:
        session.close()


class TestCrossDatasetEngine:
    """Test suite verifying cross-dataset alpha generation, AST purity, and correlation screening."""

    def test_archetypes_registry_completeness(self):
        """Verify all archetypes are registered and generate valid AST expressions."""
        engine = CrossDatasetEngine()
        assert len(engine.archetypes) >= 5

        for key, arch in engine.archetypes.items():
            assert arch.key == key
            assert arch.primary_dataset != arch.secondary_dataset or arch.primary_dataset in {"analyst4", "fundamental"}
            expr = arch.generator()
            assert isinstance(expr, str)
            assert len(expr) > 20

    def test_single_candidate_generation_and_gate_g1(self, memory_db_session: Session):
        """Verify generated candidates pass Gate G1 AST depth <= 10 and complexity <= 30."""
        engine = CrossDatasetEngine(db_session=memory_db_session)
        cand = engine.generate_candidate("cashflow_liquidity_synergy", session=memory_db_session)

        assert isinstance(cand, CrossDatasetCandidate)
        assert cand.is_valid is True
        assert cand.ast_depth <= 10
        assert cand.complexity_score <= 40
        assert len(cand.validation_errors) == 0
        assert cand.primary_dataset == "analyst4"
        assert cand.secondary_dataset == "pv1"

    def test_tri_candidate_batch_protocol(self, memory_db_session: Session):
        """Verify generate_tri_candidate_batch yields exactly 3 orthogonal candidates (Invariant 7)."""
        engine = CrossDatasetEngine(db_session=memory_db_session)
        batch_dict, candidates = engine.generate_tri_candidate_batch(session=memory_db_session)

        assert len(candidates) == 3
        assert len(batch_dict["hypotheses"]) == 3

        # Verify all candidates have valid expressions and low complexity
        for c in candidates:
            assert c.is_valid is True
            assert c.ast_depth <= 10
            assert c.complexity_score <= 40

    def test_correlation_screening_against_approved_portfolio(self, memory_db_session: Session):
        """Verify pre-simulation correlation screening detects collisions and respects max_risk threshold."""
        # Insert a simulated approved candidate in memory DB
        hypo = ResearchHypothesis(
            title="Approved Cashflow Alpha",
            domain="fundamental",
            economic_rationale="Quarterly cash flow yield predicts future excess returns.",
            expected_direction="POSITIVE",
            intended_horizon="10d",
            status="ACTIVE",
        )
        memory_db_session.add(hypo)
        memory_db_session.flush()

        cand_approved = AlphaCandidate(
            hypothesis_id=hypo.id,
            expression_raw="0.70 * group_rank(actual_cashflow_per_share_value_quarterly / close, subindustry) - 0.30 * group_rank(ts_delta(close, 5) / close, subindustry)",
            expression_normalized="norm_expr_test",
            expression_hash="hash_test_123",
            complexity_score=15,
            version=1,
            status="APPROVED",
        )
        memory_db_session.add(cand_approved)
        memory_db_session.commit()

        engine = CrossDatasetEngine(db_session=memory_db_session)

        # Audit cashflow candidate (which shares actual_cashflow_per_share_value_quarterly)
        cand = engine.generate_candidate("cashflow_liquidity_synergy", session=memory_db_session, max_correlation_risk=0.50)
        # Should flag correlation risk > 0.50 due to shared primary field in subindustry
        assert cand.correlation_risk_score > 0.50
        assert cand.is_valid is False
        assert any("Correlation risk" in err for err in cand.validation_errors)

        # Audit solvency candidate (which shares no primary fields with approved cashflow alpha)
        solv_cand = engine.generate_candidate("solvency_volatility_contraction", session=memory_db_session, max_correlation_risk=0.50)
        assert solv_cand.correlation_risk_score <= 0.40
        assert solv_cand.is_valid is True

    def test_export_and_importer_compatibility(self, memory_db_session: Session, tmp_path: Path):
        """Verify exported JSON batch can be imported and registered by HypothesisImporter."""
        engine = CrossDatasetEngine(db_session=memory_db_session)
        target_file = tmp_path / "test_batch_v2.json"

        path, candidates = engine.export_batch_json(filepath=target_file, session=memory_db_session)
        assert path.exists()
        assert len(candidates) == 3

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "hypotheses" in data
        assert len(data["hypotheses"]) == 3

        # Test ingestion via HypothesisImporter
        importer = HypothesisImporter(session=memory_db_session)
        report = importer.ingest_data(data)
        assert report.valid_candidates == 3
        assert report.syntax_errors == 0
        assert report.duplicates == 0
