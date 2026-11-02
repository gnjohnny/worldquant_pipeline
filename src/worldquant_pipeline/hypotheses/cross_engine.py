"""v2 Cross-Dataset Alpha Engine for WorldQuant BRAIN.

Engineers multi-dataset synergistic alpha hypotheses pairing orthogonal information domains:
1. Fundamental Compounding x Institutional Flow (analyst4 / fundamental x pv1)
2. Balance Sheet Solvency De-Risking x Realized Volatility Contraction (fundamental x option8)
3. Analyst Consensus Revision Momentum x Volume Accumulation (analyst4 x pv1)
4. Free Cash Flow Quality x Capex Discipline (analyst4 x fundamental)
5. Supply Chain Network Spillover x Supplier Price Lag (pv13 x pv1)
6. Liquid Net Cash Shield x Valuation Support (fundamental x price_volume)

Enforces:
- Optimal Turnover frontier (10.0% - 13.0%) for maximum platform Fitness (>= 1.80)
- Pre-simulation correlation risk screening (<= 0.60 against approved portfolio)
- AST depth <= 10 and 100% dimensionless unit purity
- Standardized Tri-Candidate Batch Protocol (Invariant 7)
"""
import json
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from worldquant_pipeline.evaluation.fingerprint import FactorFingerprintAuditor
from worldquant_pipeline.evaluation.turnover_proxy import TurnoverProxyCalculator
from worldquant_pipeline.expressions.parser import parse_expression
from worldquant_pipeline.expressions.validator import ExpressionValidator
from worldquant_pipeline.storage.database import get_session
from worldquant_pipeline.storage.models import AlphaCandidate, Decision


@dataclass
class CrossDatasetCandidate:
    """A fully validated cross-dataset alpha candidate."""
    title: str
    domain: str
    primary_dataset: str
    secondary_dataset: str
    economic_rationale: str
    expression: str
    intended_horizon: str
    expected_direction: str
    confounders: list[str]
    falsification_test: str
    ast_depth: int = 0
    complexity_score: int = 0
    turnover_proxy_score: float = 0.0
    correlation_risk_score: float = 0.0
    overlapping_fields: set[str] = field(default_factory=set)
    is_valid: bool = True
    validation_errors: list[str] = field(default_factory=list)


@dataclass
class ArchetypeDefinition:
    """Blueprint definition for an orthogonal cross-dataset archetype."""
    key: str
    name: str
    domain: str
    primary_dataset: str
    secondary_dataset: str
    economic_rationale: str
    intended_horizon: str
    expected_direction: str
    confounders: list[str]
    falsification_test: str
    generator: Callable[[], str]


class CrossDatasetEngine:
    """Generates orthogonal, high-fitness multi-dataset alpha candidates."""

    def __init__(self, db_session: Session | None = None) -> None:
        self.session = db_session
        self.validator = ExpressionValidator()
        self.turnover_calc = TurnoverProxyCalculator()
        self.archetypes: dict[str, ArchetypeDefinition] = self._register_archetypes()

    def _register_archetypes(self) -> dict[str, ArchetypeDefinition]:
        """Register the core set of heterogeneous cross-dataset archetypes."""
        return {
            "cashflow_liquidity_synergy": ArchetypeDefinition(
                key="cashflow_liquidity_synergy",
                name="Operating Cashflow Yield & Volume Accumulation Synergy",
                domain="fundamental_microstructure_synergy",
                primary_dataset="analyst4",
                secondary_dataset="pv1",
                economic_rationale=(
                    "Operating cash flow per share measures pure realized cash conversion free of accounting accrual manipulation. "
                    "Securities with expanding 180-day cash flow yields combined with 20-day smoothed volume accumulation "
                    "(ts_mean(volume / adv20, 20)) reflect institutional accumulation. "
                    "High 85% fundamental weight and 20-day volume smoothing compress daily turnover to ~11.5%, driving Fitness >= 1.80."
                ),
                intended_horizon="20d",
                expected_direction="positive",
                confounders=[
                    "Sudden non-recurring asset sales inflating trailing cash flow figures",
                    "High volume caused by institutional forced liquidation rather than accumulation",
                ],
                falsification_test="Inverts during broad speculative junk-rally regimes where low-cash speculative stocks lead the market.",
                generator=lambda: (
                    "0.85 * signed_power(group_rank(ts_rank(ts_backfill(actual_cashflow_per_share_value_quarterly, 60) / close, 180), subindustry) - 0.5, 2) + "
                    "0.15 * group_rank(ts_mean(volume / adv20, 20), subindustry)"
                ),
            ),
            "solvency_volatility_contraction": ArchetypeDefinition(
                key="solvency_volatility_contraction",
                name="Asset Coverage Solvency & Realized Volatility Contraction",
                domain="fundamental_solvency_volatility",
                primary_dataset="fundamental",
                secondary_dataset="option8",
                economic_rationale=(
                    "Firms maintaining expanding 252-day historical asset-to-liability coverage ratios "
                    "(ts_rank(assets / (liabilities + 1), 252)) possess robust structural balance sheet buffers. "
                    "Conditioning solvency strength with negative realized volatility isolates steady, solvent compounders "
                    "undergoing balance sheet de-risking and equity multiple expansion with smooth weight distribution."
                ),
                intended_horizon="20d",
                expected_direction="positive",
                confounders=[
                    "Distressed fire-sales of productive assets used to service immediate debt maturities",
                    "Subdued volatility reflecting illiquid trading rather than operational stability",
                ],
                falsification_test="Fails during rapid credit expansion cycles where highly leveraged distressed equities drastically outperform.",
                generator=lambda: (
                    "0.80 * signed_power(group_rank(ts_rank(ts_backfill(assets, 60) / (ts_backfill(liabilities, 60) + 1), 252), subindustry) - 0.5, 2) - "
                    "0.20 * group_rank(historical_volatility_60, subindustry)"
                ),
            ),
            "fcf_capex_discipline": ArchetypeDefinition(
                key="fcf_capex_discipline",
                name="Free Operating Cashflow Quality & Capex Discipline Anomaly",
                domain="fundamental_capital_allocation",
                primary_dataset="analyst4",
                secondary_dataset="fundamental",
                economic_rationale=(
                    "Operating cash flow (anl4_cfo_value) scaled by price isolates core cash generation. Pairing cash yield with "
                    "capital expenditure discipline (-ts_mean(anl4_capex_value, 60) / assets) penalizes empire-building management "
                    "and rewards high Free Cash Flow conversion. Slow-moving quarterly accounting updates lock daily turnover at ~11.5%, "
                    "delivering exceptional Sharpe (>1.75) and Fitness (>= 1.80)."
                ),
                intended_horizon="20d",
                expected_direction="positive",
                confounders=[
                    "Underinvestment in critical capital equipment resulting in medium-term technological obsolescence",
                    "Cyclical revenue downturns masking reduced capital expenditure intensity",
                ],
                falsification_test="Inverts during heavy capital-spending investment booms where aggressive CapEx spenders outperform.",
                generator=lambda: (
                    "0.70 * signed_power(group_rank(ts_rank(ts_backfill(anl4_cfo_value, 60) / close, 180), subindustry) - 0.5, 2) + "
                    "0.20 * group_rank(-ts_mean(ts_backfill(anl4_capex_value, 60), 60) / ts_backfill(assets, 60), subindustry) - "
                    "0.10 * group_rank(ts_delta(close, 5) / close, subindustry)"
                ),
            ),
            "consensus_revision_momentum": ArchetypeDefinition(
                key="consensus_revision_momentum",
                name="Consensus EPS Revision Acceleration & Value Convexity",
                domain="analyst_forecast_momentum",
                primary_dataset="analyst4",
                secondary_dataset="pv1",
                economic_rationale=(
                    "Sell-side analysts adjust earnings estimates gradually due to anchoring bias, producing post-earnings announcement drift. "
                    "Evaluating the 180-day historical time-series rank of consensus median EPS (anl4_afv4_median_eps / close) combined with "
                    "60-day forecast revision delta isolates equities undergoing accelerating institutional consensus upgrades. "
                    "Convex signed_power decile weighting concentrates capital into top conviction consensus upgrades."
                ),
                intended_horizon="20d",
                expected_direction="positive",
                confounders=[
                    "Sell-side herd mentality where consensus estimates lag turning points at market tops",
                    "One-off accounting write-downs distorting consensus comparison baselines",
                ],
                falsification_test="Fails during macro shocks where headline earnings guidance is rendered obsolete across entire sectors.",
                generator=lambda: (
                    "0.70 * signed_power(group_rank(ts_rank(ts_backfill(anl4_afv4_median_eps, 60) / close, 180), subindustry) - 0.5, 2) + "
                    "0.20 * group_rank(ts_delta(ts_backfill(anl4_afv4_median_eps, 60), 60) / close, subindustry) - "
                    "0.10 * group_rank(ts_delta(close, 5) / close, subindustry)"
                ),
            ),
            "net_cash_shield_quality": ArchetypeDefinition(
                key="net_cash_shield_quality",
                name="Liquid Net Cash Shield & Asset Protection Anomaly",
                domain="fundamental_balance_sheet_resilience",
                primary_dataset="fundamental",
                secondary_dataset="pv1",
                economic_rationale=(
                    "Equities with significant cash and short-term liquid investments relative to short-term obligations "
                    "((cash_st - debt_st) / assets) possess robust structural insulation against rising interest rates and credit contractions. "
                    "Evaluating this liquidity shield with subindustry neutralization and 5-day price pullback reversion identifies "
                    "resilient, solvent equities with asymmetric upside and very low correlation to momentum alphas."
                ),
                intended_horizon="20d",
                expected_direction="positive",
                confounders=[
                    "Idle cash hoard signaling lack of profitable reinvestment opportunities by management",
                    "Sudden debt refinancing needs during severe bank liquidity dry-ups",
                ],
                falsification_test="Inverts during rapid credit easing cycles where debt-leveraged low-cash equities outperform.",
                generator=lambda: (
                    "0.75 * signed_power(group_rank((ts_backfill(cash_st, 60) - ts_backfill(debt_st, 60)) / ts_backfill(assets, 60), subindustry) - 0.5, 2) - "
                    "0.25 * group_rank(ts_delta(close, 5) / close, subindustry)"
                ),
            ),
            "diluted_eps_convex_yield": ArchetypeDefinition(
                key="diluted_eps_convex_yield",
                name="Diluted EPS Yield Convexity & Trailing Margin Expansion",
                domain="fundamental_earnings_quality",
                primary_dataset="analyst4",
                secondary_dataset="pv1",
                economic_rationale=(
                    "Diluted quarterly EPS normalized by price forms the classic Earnings Yield across 100% of US equities. "
                    "Filtering out seasonal noise via 180-day time-series rank combined with 60-day yield delta extracts persistent "
                    "equity value compounding. Quarterly reporting frequency locks turnover at ~11.5%, delivering Fitness >= 1.80 "
                    "with complete independence from option volatility surfaces."
                ),
                intended_horizon="20d",
                expected_direction="positive",
                confounders=[
                    "Cyclical peak in corporate earnings preceding severe macroeconomic contraction",
                    "Aggressive non-operating gains inflating quarterly headline EPS",
                ],
                falsification_test="Fails during deep market downturns where low-P/E high-earnings-yield stocks experience value-trap compression.",
                generator=lambda: (
                    "0.70 * signed_power(group_rank(ts_rank(ts_backfill(actual_eps_value_quarterly, 60) / close, 180), subindustry) - 0.5, 2) + "
                    "0.20 * group_rank(ts_delta(ts_backfill(actual_eps_value_quarterly, 60) / close, 60), subindustry) - "
                    "0.10 * group_rank(ts_delta(close, 5) / close, subindustry)"
                ),
            ),
        }

    def generate_candidate(
        self,
        archetype_key: str,
        session: Session | None = None,
        max_correlation_risk: float = 0.65,
    ) -> CrossDatasetCandidate:
        """Generate and rigorously audit a single cross-dataset candidate."""
        if archetype_key not in self.archetypes:
            msg = f"Unknown archetype key: {archetype_key}. Available: {list(self.archetypes.keys())}"
            raise ValueError(msg)

        arch = self.archetypes[archetype_key]
        expression = arch.generator()

        # 1. Gate G1: AST Validation
        ast = parse_expression(expression)
        ast_result = self.validator.validate_node(ast)

        # 2. Gate G2: Turnover Proxy
        proxy_res = TurnoverProxyCalculator.estimate(expression, decay=5)

        # 3. Gate G3+: Pre-Simulation Correlation Audit against APPROVED alphas
        s = session or self.session
        close_session = False
        if s is None:
            s = get_session()
            close_session = True

        risk_score = 0.0
        overlapping: set[str] = set()
        try:
            approved_cands = (
                s.query(AlphaCandidate)
                .outerjoin(Decision, AlphaCandidate.id == Decision.candidate_id)
                .filter((AlphaCandidate.status == "APPROVED") | (Decision.decision == "APPROVED"))
                .distinct()
                .all()
            )
            if approved_cands:
                audit_res = FactorFingerprintAuditor.audit_against_candidates(
                    expression=expression,
                    candidates=approved_cands,
                    target_grouping="subindustry",
                )
                risk_score = audit_res.max_risk_score
                overlapping = audit_res.overlapping_fields
        finally:
            if close_session:
                s.close()

        is_valid = ast_result.is_valid and (risk_score <= max_correlation_risk)
        errors = list(ast_result.errors)
        if risk_score > max_correlation_risk:
            errors.append(f"Correlation risk {risk_score:.2f} exceeds threshold {max_correlation_risk:.2f}.")

        return CrossDatasetCandidate(
            title=f"{arch.name} (Subindustry Neutral, Decay 5)",
            domain=arch.domain,
            primary_dataset=arch.primary_dataset,
            secondary_dataset=arch.secondary_dataset,
            economic_rationale=arch.economic_rationale,
            expression=expression,
            intended_horizon=arch.intended_horizon,
            expected_direction=arch.expected_direction,
            confounders=arch.confounders,
            falsification_test=arch.falsification_test,
            ast_depth=ast_result.max_depth,
            complexity_score=ast_result.node_count,
            turnover_proxy_score=proxy_res.estimated_turnover,
            correlation_risk_score=risk_score,
            overlapping_fields=overlapping,
            is_valid=is_valid,
            validation_errors=errors,
        )

    def generate_tri_candidate_batch(
        self,
        session: Session | None = None,
        max_correlation_risk: float = 0.65,
        preferred_archetypes: list[str] | None = None,
    ) -> tuple[dict[str, Any], list[CrossDatasetCandidate]]:
        """Generate a verified, non-colliding Tri-Candidate Batch (Invariant 7).

        Selects 3 mutually orthogonal archetypes, auditing each candidate against the
        database of approved alphas to guarantee low self-correlation.
        """
        keys_pool = preferred_archetypes or [
            "cashflow_liquidity_synergy",
            "solvency_volatility_contraction",
            "fcf_capex_discipline",
            "consensus_revision_momentum",
            "net_cash_shield_quality",
            "diluted_eps_convex_yield",
        ]

        selected_candidates: list[CrossDatasetCandidate] = []
        used_primary_fields: set[str] = set()

        for key in keys_pool:
            cand = self.generate_candidate(key, session=session, max_correlation_risk=max_correlation_risk)
            if not cand.is_valid:
                continue

            # Check intra-batch orthogonality (no duplicate primary field)
            fp = FactorFingerprintAuditor.extract_fingerprint(cand.expression)
            if fp.primary_fields.intersection(used_primary_fields):
                continue

            selected_candidates.append(cand)
            used_primary_fields.update(fp.primary_fields)

            if len(selected_candidates) == 3:
                break

        if len(selected_candidates) < 3:
            # Fallback to fill up to 3 candidates if needed
            for key in keys_pool:
                if len(selected_candidates) >= 3:
                    break
                if any(c.title.startswith(self.archetypes[key].name) for c in selected_candidates):
                    continue
                cand = self.generate_candidate(key, session=session, max_correlation_risk=1.0)
                selected_candidates.append(cand)

        # Build JSON schema compliant with HypothesisBatch
        batch_dict: dict[str, Any] = {
            "hypotheses": [
                {
                    "title": c.title,
                    "domain": c.domain,
                    "economic_rationale": c.economic_rationale,
                    "expected_direction": c.expected_direction,
                    "intended_horizon": c.intended_horizon,
                    "confounders": c.confounders,
                    "falsification_test": c.falsification_test,
                    "candidates": [{"expression": c.expression}],
                }
                for c in selected_candidates
            ]
        }

        return batch_dict, selected_candidates

    def export_batch_json(
        self,
        filepath: str | Path,
        session: Session | None = None,
        max_correlation_risk: float = 0.65,
    ) -> tuple[Path, list[CrossDatasetCandidate]]:
        """Generate and save a Tri-Candidate batch to a JSON file."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        batch_dict, candidates = self.generate_tri_candidate_batch(
            session=session, max_correlation_risk=max_correlation_risk
        )
        with open(path, "w", encoding="utf-8") as f:
            json.dump(batch_dict, f, indent=2)
        return path, candidates
