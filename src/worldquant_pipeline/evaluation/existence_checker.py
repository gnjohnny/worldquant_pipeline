"""Comprehensive Candidate Existence, Duplicate, and Portfolio Collision Checker.

Audits candidate expressions across the entire PostgreSQL research memory across ALL statuses:
1. Exact Match: Raw string, canonical AST normalization, and SHA-256 hash.
2. Factor Driver Overlap: Checks if the primary non-price driver fields already exist
   in the approved/submitted/validated portfolio (preventing platform self-correlation collisions >= 0.70).
3. Negative Knowledge History: Identifies if similar expressions were previously tested and rejected,
   surfacing prior experiment metrics and failure reasons.
4. Pre-Simulation Verdict: Strictly classifies candidates as SAFE_VIRGIN_ALPHA,
   EXACT_DUPLICATE, HIGH_PORTFOLIO_COLLISION, or PREVIOUSLY_FAILED.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import ClassVar

from sqlalchemy.orm import Session

from worldquant_pipeline.evaluation.fingerprint import FactorFingerprintAuditor
from worldquant_pipeline.expressions.canonicalize import (
    canonicalize_expression,
    compute_expression_hash,
)
from worldquant_pipeline.storage.models import (
    AlphaCandidate,
)


class ExistenceVerdict(str, Enum):
    """Safety classification for candidate generation and pre-simulation check."""
    SAFE_VIRGIN_ALPHA = "SAFE_VIRGIN_ALPHA"
    EXACT_DUPLICATE = "EXACT_DUPLICATE"
    HIGH_PORTFOLIO_COLLISION = "HIGH_PORTFOLIO_COLLISION"
    PREVIOUSLY_FAILED = "PREVIOUSLY_FAILED"


@dataclass
class MatchingCandidateInfo:
    """Detailed summary of a matching candidate in the database."""
    candidate_id: str
    status: str
    expression_raw: str
    expression_normalized: str
    created_at: datetime | None
    match_type: str  # "EXACT_HASH", "EXACT_RAW", "CANONICAL", "PRIMARY_FIELD", "FACTOR_SIMILARITY"
    similarity_score: float = 1.0
    sharpe: float | None = None
    fitness: float | None = None
    turnover: float | None = None
    subuniverse_sharpe: float | None = None
    self_correlation: float | None = None
    last_decision: str | None = None
    last_decision_reason: str | None = None


@dataclass
class ExistenceCheckResult:
    """Comprehensive result of checking an expression against the research database."""
    expression_raw: str
    canonical_expression: str
    expression_hash: str
    primary_fields: set[str] = field(default_factory=set)
    all_fields: set[str] = field(default_factory=set)
    is_exact_duplicate: bool = False
    verdict: ExistenceVerdict = ExistenceVerdict.SAFE_VIRGIN_ALPHA
    exact_match: MatchingCandidateInfo | None = None
    portfolio_collisions: list[MatchingCandidateInfo] = field(default_factory=list)
    past_failures: list[MatchingCandidateInfo] = field(default_factory=list)
    max_risk_score: float = 0.0
    warnings: list[str] = field(default_factory=list)
    recommendation: str = ""

    @property
    def is_safe_to_simulate(self) -> bool:
        """Return True only if expression is completely safe and original."""
        return self.verdict == ExistenceVerdict.SAFE_VIRGIN_ALPHA


class AlphaExistenceChecker:
    """Audits expressions against PostgreSQL database to prevent duplicates and portfolio collisions."""

    BENCHMARK_PRICE_FIELDS: ClassVar[set[str]] = {
        "close", "open", "high", "low", "volume", "vwap", "returns",
        "subindustry", "industry", "sector", "market", "adv20", "cap",
    }

    PORTFOLIO_ACTIVE_STATUSES: ClassVar[set[str]] = {"APPROVED", "VALIDATED", "SUBMITTED", "NEEDS_REVIEW"}
    FAILURE_STATUSES: ClassVar[set[str]] = {"REJECTED", "NEEDS_REVISION", "SUPERSEDED"}

    @classmethod
    def fast_extract_fields(cls, expr_str: str) -> tuple[set[str], set[str]]:
        """Fast regex-based field extraction without slow recursive AST traversal."""
        import re
        tokens = set(re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", expr_str.lower()))
        # Extract local intermediate variables assigned on the LHS of '=' (e.g. 'var = expr;')
        local_vars = set(re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*=", expr_str.lower()))
        known_keywords = {"driver", "cauchy", "gaussian", "normal", "uniform", "range", "filter"}
        known_ops = {
            "group_rank", "group_zscore", "group_neutralize", "group_mean", "group_scale",
            "group_median", "group_std_dev", "group_stddev", "group_max", "group_min", "group_sum",
            "ts_decay_linear", "ts_decay_exp_window", "ts_mean", "ts_rank", "ts_delta",
            "ts_delay", "ts_std_dev", "ts_stddev", "ts_argmax", "ts_argmin", "ts_backfill", "ts_corr",
            "ts_kurtosis", "ts_covariance", "ts_regression", "ts_product", "ts_sum",
            "signed_power", "rank", "abs", "max", "min", "scale", "trade_when", "log",
            "exp", "sqrt", "clamp", "decay_linear", "normalize", "zscore", "bucket", "densify",
            "quantile", "tanh", "sigmoid", "ts_skewness", "ts_moment", "ts_av_diff",
        }
        all_fields = {
            t for t in tokens
            if t not in known_ops and t not in local_vars and t not in known_keywords
        }
        primary_fields = {t for t in all_fields if t not in cls.BENCHMARK_PRICE_FIELDS}
        return all_fields, primary_fields

    @classmethod
    def extract_driver_fields(cls, expr_str: str) -> tuple[set[str], set[str]]:
        """Extract all fields and non-price primary driver fields from an expression."""
        return cls.fast_extract_fields(expr_str)

    @classmethod
    def _build_candidate_info(
        cls,
        cand: AlphaCandidate,
        match_type: str,
        similarity_score: float = 1.0,
    ) -> MatchingCandidateInfo:
        """Construct a MatchingCandidateInfo object from an AlphaCandidate row."""
        sharpe: float | None = None
        fitness: float | None = None
        turnover: float | None = None
        subuniverse_sharpe: float | None = None
        self_corr: float | None = None
        last_decision: str | None = None
        last_reason: str | None = None

        # Fetch latest metrics from experiments
        if cand.experiments:
            latest_exp = cand.experiments[-1]
            for m in latest_exp.metrics:
                m_name = m.metric_name.lower()
                if m_name == "sharpe":
                    sharpe = m.metric_value
                elif m_name == "fitness":
                    fitness = m.metric_value
                elif m_name == "turnover":
                    turnover = m.metric_value
                elif "subuniverse" in m_name or "sub_universe" in m_name:
                    subuniverse_sharpe = m.metric_value
                elif "self_correlation" in m_name or "self_corr" in m_name:
                    self_corr = m.metric_value

        if cand.decisions:
            latest_dec = cand.decisions[-1]
            last_decision = latest_dec.decision
            last_reason = latest_dec.reason

        return MatchingCandidateInfo(
            candidate_id=cand.id,
            status=cand.status,
            expression_raw=cand.expression_raw,
            expression_normalized=cand.expression_normalized or "",
            created_at=cand.created_at,
            match_type=match_type,
            similarity_score=similarity_score,
            sharpe=sharpe,
            fitness=fitness,
            turnover=turnover,
            subuniverse_sharpe=subuniverse_sharpe,
            self_correlation=self_corr,
            last_decision=last_decision,
            last_decision_reason=last_reason,
        )

    @classmethod
    def check_expression(
        cls,
        expr_str: str,
        session: Session,
        correlation_cutoff: float = 0.50,
    ) -> ExistenceCheckResult:
        """Check if an expression or its factor drivers already exist in the database."""
        raw_clean = expr_str.strip()
        try:
            canonical = canonicalize_expression(raw_clean)
        except Exception:  # noqa: BLE001
            canonical = raw_clean
        expr_hash = compute_expression_hash(canonical)

        all_fields, primary_fields = cls.extract_driver_fields(raw_clean)

        result = ExistenceCheckResult(
            expression_raw=raw_clean,
            canonical_expression=canonical,
            expression_hash=expr_hash,
            primary_fields=primary_fields,
            all_fields=all_fields,
        )

        # 1. Exact Duplicate Search (Hash or Raw String)
        exact_db = (
            session.query(AlphaCandidate)
            .filter(
                (AlphaCandidate.expression_hash == expr_hash)
                | (AlphaCandidate.expression_raw == raw_clean)
                | (AlphaCandidate.expression_normalized == canonical)
            )
            .first()
        )

        if exact_db:
            result.is_exact_duplicate = True
            result.verdict = ExistenceVerdict.EXACT_DUPLICATE
            result.exact_match = cls._build_candidate_info(exact_db, match_type="EXACT_HASH", similarity_score=1.0)
            result.warnings.append(
                f"EXACT DUPLICATE: Candidate already exists in database as ID '{exact_db.id[:8]}' "
                f"with status '{exact_db.status}'."
            )
            result.recommendation = (
                f"Do NOT simulate. Expression is already logged as {exact_db.status} "
                f"(Candidate ID: {exact_db.id[:8]})."
            )
            return result

        # 2. Fast SQL-filtered search for factor overlap & portfolio collisions
        from sqlalchemy import or_

        portfolio_candidates: list[AlphaCandidate] = []
        rejected_candidates: list[AlphaCandidate] = []

        if primary_fields:
            conditions = [AlphaCandidate.expression_raw.ilike(f"%{pf}%") for pf in primary_fields]
            matching_db_cands = session.query(AlphaCandidate).filter(or_(*conditions)).all()
            for cand in matching_db_cands:
                if cand.status in cls.PORTFOLIO_ACTIVE_STATUSES:
                    portfolio_candidates.append(cand)
                elif cand.status in cls.FAILURE_STATUSES:
                    rejected_candidates.append(cand)
        else:
            # Price only alpha - query active portfolio
            portfolio_candidates = (
                session.query(AlphaCandidate)
                .filter(AlphaCandidate.status.in_(cls.PORTFOLIO_ACTIVE_STATUSES))
                .limit(40)
                .all()
            )

        # Audit against matching portfolio candidates
        audit_res = FactorFingerprintAuditor.audit_against_candidates(raw_clean, portfolio_candidates)
        result.max_risk_score = audit_res.max_risk_score

        # Check primary field collisions in portfolio
        for cand in portfolio_candidates:
            _cand_all, cand_primary = cls.extract_driver_fields(cand.expression_raw)
            shared = primary_fields.intersection(cand_primary)
            if shared:
                overlap_ratio = len(shared) / max(len(primary_fields), 1)
                sim_score = round(max(audit_res.max_risk_score, 0.50 + 0.35 * overlap_ratio), 3)
                info = cls._build_candidate_info(cand, match_type="PRIMARY_FIELD", similarity_score=sim_score)
                result.portfolio_collisions.append(info)

        # Check past rejected history
        for cand in rejected_candidates:
            _cand_all, cand_primary = cls.extract_driver_fields(cand.expression_raw)
            shared = primary_fields.intersection(cand_primary)
            if shared:
                info = cls._build_candidate_info(cand, match_type="PRIMARY_FIELD", similarity_score=0.85)
                result.past_failures.append(info)

        # Sort matches
        result.portfolio_collisions.sort(key=lambda x: x.similarity_score, reverse=True)
        result.past_failures.sort(key=lambda x: x.created_at or datetime.min, reverse=True)

        # 3. Formulate Verdict
        if result.portfolio_collisions:
            top_collision = result.portfolio_collisions[0]
            if top_collision.similarity_score >= correlation_cutoff or audit_res.risk_level == "HIGH":
                result.verdict = ExistenceVerdict.HIGH_PORTFOLIO_COLLISION
                result.warnings.append(
                    f"PORTFOLIO COLLISION WARNING: Shares primary driver field(s) {', '.join(sorted(primary_fields))} "
                    f"with {top_collision.status} candidate '{top_collision.candidate_id[:8]}' "
                    f"(Similarity: {top_collision.similarity_score:.1%})."
                )
                result.warnings.append(
                    "High probability of self-correlation collision (>= 0.70) on WorldQuant BRAIN platform!"
                )
                result.recommendation = (
                    f"REJECT CANDIDATE: Target a different, unmined dataset. Driver fields "
                    f"{', '.join(sorted(primary_fields))} are already active in your portfolio."
                )
                return result

        if result.past_failures and len(result.past_failures) >= 3:
            result.verdict = ExistenceVerdict.PREVIOUSLY_FAILED
            result.warnings.append(
                f"NEGATIVE KNOWLEDGE: Factor based on {', '.join(sorted(primary_fields))} was tested "
                f"{len(result.past_failures)} times in past batches and repeatedly rejected."
            )
            result.recommendation = (
                "CAUTION: Repeatedly failed in past backtests. Pivot to a virgin economic rationale."
            )
            return result

        # 4. Safe Virgin Alpha
        result.verdict = ExistenceVerdict.SAFE_VIRGIN_ALPHA
        result.recommendation = (
            "SAFE TO MINE: No exact duplicates, no primary field overlap with submitted portfolio, "
            "and clean orthogonal factor fingerprint."
        )
        return result
