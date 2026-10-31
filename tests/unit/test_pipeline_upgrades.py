"""Unit tests for the 5 pipeline upgrades:
1. Event input typing & validation (Gate G1)
2. Pre-simulation factor fingerprint & collision auditor (Gate G3+)
3. Advanced alpha recipes & convexity generators
4. Mathematical turnover proxy (Gate G2)
5. Quality gate runner pre-simulation evaluation
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from worldquant_pipeline.evaluation.fingerprint import FactorFingerprintAuditor
from worldquant_pipeline.evaluation.gates import QualityGateRunner
from worldquant_pipeline.evaluation.turnover_proxy import TurnoverProxyCalculator
from worldquant_pipeline.expressions.recipes import AlphaRecipeGenerator
from worldquant_pipeline.expressions.validator import ExpressionValidator
from worldquant_pipeline.storage.database import Base
from worldquant_pipeline.storage.models import AlphaCandidate, ResearchHypothesis


@pytest.fixture
def test_db_session():
    """Create an isolated in-memory SQLite database session for unit tests."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    try:
        yield session
    finally:
        session.close()


class TestPipelineUpgrades:
    """Test suite verifying all 5 workbench upgrades."""

    def test_upgrade1_event_input_rejection(self):
        """Verify Gate G1 catches event inputs inside ts_backfill."""
        validator = ExpressionValidator()

        # anl4_buy is an event field: should be rejected
        res_event = validator.validate_expression_string("ts_backfill(anl4_buy, 60)")
        assert res_event.is_valid is False
        assert any("Operator 'ts_backfill' does not support event inputs" in err for err in res_event.errors)

        # fnd6_fopo is continuous matrix field: should pass
        res_matrix = validator.validate_expression_string("ts_backfill(fnd6_fopo, 60)")
        assert res_matrix.is_valid is True
        assert len(res_matrix.errors) == 0

    def test_upgrade2_fingerprint_correlation_auditor(self, test_db_session: Session):
        """Verify Gate G3+ identifies self-correlation collision risks with approved alphas."""
        # Setup an existing approved candidate in the test database
        hypo = ResearchHypothesis(
            title="Approved Cashflow Alpha",
            domain="fundamental",
            economic_rationale="Quarterly cash flow yield predicts future excess returns.",
            expected_direction="POSITIVE",
            intended_horizon="10d",
            status="ACTIVE",
        )
        test_db_session.add(hypo)
        test_db_session.flush()

        approved_expr = (
            "0.85 * signed_power(group_rank(actual_cashflow_per_share_value_quarterly, subindustry) - 0.5, 2) - "
            "0.15 * group_rank(ts_delta(close, 3) / close, subindustry)"
        )
        approved_candidate = AlphaCandidate(
            hypothesis_id=hypo.id,
            expression_raw=approved_expr,
            expression_normalized=approved_expr,
            expression_hash="mock_hash_1",
            status="APPROVED",
        )
        test_db_session.add(approved_candidate)
        test_db_session.commit()

        # Audit a near-identical candidate with same primary field and same grouping
        new_expr_same_driver = (
            "0.80 * group_rank(actual_cashflow_per_share_value_quarterly, subindustry) - "
            "0.20 * group_rank(ts_delta(close, 5) / close, subindustry)"
        )
        res_high_risk = FactorFingerprintAuditor.audit_against_database(
            new_expr_same_driver, test_db_session
        )
        assert res_high_risk.risk_level == "HIGH"
        assert res_high_risk.most_similar_candidate_id == approved_candidate.id
        assert len(res_high_risk.warnings) > 0

        # Audit an orthogonal candidate using a completely unmined field
        orthogonal_expr = (
            "0.85 * signed_power(group_rank(pv13_custretsig_retsig, subindustry) - 0.5, 2) - "
            "0.15 * group_rank(ts_delta(close, 3) / close, subindustry)"
        )
        res_low_risk = FactorFingerprintAuditor.audit_against_database(
            orthogonal_expr, test_db_session
        )
        assert res_low_risk.risk_level == "LOW"

    def test_upgrade3_advanced_recipes_ast_validity(self):
        """Verify advanced non-linear recipe generators pass AST validation."""
        validator = ExpressionValidator()

        # 1. Multiplicative synergy
        e1 = AlphaRecipeGenerator.multiplicative_synergy("fnd6_fopo", "actual_sales_value_quarter")
        res1 = validator.validate_expression_string(e1)
        assert res1.is_valid is True, f"Errors: {res1.errors}"

        # 2. Z-Score blend
        e2 = AlphaRecipeGenerator.zscore_blend("actual_sales_value_quarter", "fnd6_fopo")
        res2 = validator.validate_expression_string(e2)
        assert res2.is_valid is True, f"Errors: {res2.errors}"

        # 3. Volatility-scaled signal
        e3 = AlphaRecipeGenerator.volatility_scaled_signal("fnd6_fopo", "parkinson_volatility_30")
        res3 = validator.validate_expression_string(e3)
        assert res3.is_valid is True, f"Errors: {res3.errors}"

        # 4. Vector orthogonal residual
        e4 = AlphaRecipeGenerator.vector_orthogonal_residual("actual_sales_value_quarter", "fnd6_fopo")
        res4 = validator.validate_expression_string(e4)
        assert res4.is_valid is True, f"Errors: {res4.errors}"

    def test_upgrade4_mathematical_turnover_proxy(self):
        """Verify Gate G2 correctly predicts turnover bounds."""
        # 1. Fast price reversal without decay: dangerous high turnover
        fast_expr = "group_rank(ts_delta(close, 1) / close, subindustry)"
        est_fast = TurnoverProxyCalculator.estimate(fast_expr, decay=1)
        assert est_fast.status == "HIGH_RISK"
        assert est_fast.is_safe is False
        assert est_fast.estimated_turnover > 0.50

        # 2. Balanced fundamental + smoothed reversal with decay 5: optimal turnover
        optimal_expr = (
            "0.85 * signed_power(group_rank(fnd6_fopo, subindustry) - 0.5, 2) - "
            "0.15 * group_rank(ts_delta(close, 3) / close, subindustry)"
        )
        est_optimal = TurnoverProxyCalculator.estimate(optimal_expr, decay=5)
        assert est_optimal.status == "OPTIMAL"
        assert est_optimal.is_safe is True
        assert 0.05 <= est_optimal.estimated_turnover <= 0.20

    def test_upgrade5_gate_runner_pre_simulation(self, test_db_session: Session):
        """Verify QualityGateRunner.evaluate_pre_simulation integrates G1, G2, and G3+."""
        runner = QualityGateRunner()

        # Expression with event input error
        bad_expr = "ts_backfill(anl4_buy, 60)"
        res_bad = runner.evaluate_pre_simulation(bad_expr, session=test_db_session)
        assert res_bad.passed is False
        assert res_bad.gate_details["G1_ast_validity"] is False

        # Safe orthogonal expression
        good_expr = (
            "0.85 * signed_power(group_rank(fnd6_fopo, subindustry) - 0.5, 2) - "
            "0.15 * group_rank(ts_delta(close, 3) / close, subindustry)"
        )
        res_good = runner.evaluate_pre_simulation(good_expr, session=test_db_session, decay=5)
        assert res_good.passed is True
        assert res_good.gate_details["G1_ast_validity"] is True
        assert res_good.gate_details["G2_turnover_proxy"] is True
        assert res_good.gate_details["G3_correlation_risk"] is True
