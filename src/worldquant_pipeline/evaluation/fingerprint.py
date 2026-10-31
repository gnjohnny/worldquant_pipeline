"""Pre-simulation Factor Fingerprint & Self-Correlation Collision Auditor (Gate G3+)."""
from dataclasses import dataclass, field
from typing import ClassVar

from sqlalchemy.orm import Session

from worldquant_pipeline.expressions.ast_nodes import (
    BinaryOperationNode,
    ExpressionNode,
    FieldNode,
    FunctionCallNode,
    KeywordArgNode,
    LiteralNode,
    TernaryNode,
    UnaryOperationNode,
)
from worldquant_pipeline.expressions.parser import parse_expression
from worldquant_pipeline.storage.models import AlphaCandidate


@dataclass
class FactorFingerprint:
    """Deconstructed factor fingerprint of an alpha candidate expression."""
    fields: set[str] = field(default_factory=set)
    primary_fields: set[str] = field(default_factory=set)
    operators: set[str] = field(default_factory=set)
    groupings: set[str] = field(default_factory=set)
    has_price_reversal: bool = False


@dataclass
class FingerprintComparison:
    """Comparison metrics between an expression and an existing alpha candidate."""
    candidate_id: str
    status: str
    expression_raw: str
    jaccard_similarity: float
    overlapping_fields: set[str]
    same_grouping: bool
    estimated_correlation_risk: float


@dataclass
class FingerprintAuditResult:
    """Result of pre-simulation correlation and factor overlap audit."""
    expression: str
    risk_level: str  # "LOW", "MEDIUM", "HIGH"
    max_risk_score: float
    most_similar_candidate_id: str | None
    most_similar_status: str | None
    overlapping_fields: set[str] = field(default_factory=set)
    comparisons: list[FingerprintComparison] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


class FactorFingerprintAuditor:
    """Audits candidate expressions against historical and approved alphas to prevent self-correlation collisions."""

    BENCHMARK_PRICE_FIELDS: ClassVar[set[str]] = {"close", "open", "high", "low", "volume", "vwap", "returns"}

    @classmethod
    def extract_fingerprint(cls, expr_str: str) -> FactorFingerprint:
        """Parse expression AST and extract fields, operators, and structural characteristics."""
        try:
            node = parse_expression(expr_str)
        except Exception:  # noqa: BLE001
            return FactorFingerprint()

        fields: set[str] = set()
        operators: set[str] = set()
        groupings: set[str] = set()
        has_reversal = False

        def traverse(curr: ExpressionNode | None) -> None:
            nonlocal has_reversal
            if curr is None:
                return

            if isinstance(curr, FieldNode):
                name = curr.name.lower()
                fields.add(name)
                if name in {"subindustry", "industry", "sector", "market"}:
                    groupings.add(name)

            elif isinstance(curr, FunctionCallNode):
                op = curr.name.lower()
                operators.add(op)
                if op == "group_rank" and len(curr.args) > 1:
                    arg1 = curr.args[1]
                    if isinstance(arg1, FieldNode):
                        groupings.add(arg1.name.lower())
                    elif isinstance(arg1, LiteralNode) and isinstance(arg1.value, str):
                        groupings.add(arg1.value.lower())

                # Detect price reversal overlay
                if op in {"ts_delta", "returns"}:
                    for a in curr.args:
                        if isinstance(a, FieldNode) and a.name.lower() in {"close", "returns"}:
                            has_reversal = True

                for a in curr.args:
                    traverse(a)

            elif isinstance(curr, KeywordArgNode):
                traverse(curr.value)

            elif isinstance(curr, UnaryOperationNode):
                traverse(curr.operand)

            elif isinstance(curr, BinaryOperationNode):
                traverse(curr.left)
                traverse(curr.right)

            elif isinstance(curr, TernaryNode):
                traverse(curr.condition)
                traverse(curr.true_expr)
                traverse(curr.false_expr)

        traverse(node)

        # Non-price informational drivers
        primary_fields = {f for f in fields if f not in cls.BENCHMARK_PRICE_FIELDS and f not in groupings}

        return FactorFingerprint(
            fields=fields,
            primary_fields=primary_fields,
            operators=operators,
            groupings=groupings,
            has_price_reversal=has_reversal,
        )

    @classmethod
    def audit_against_candidates(
        cls,
        expression: str,
        candidates: list[AlphaCandidate],
        target_grouping: str | None = None,
    ) -> FingerprintAuditResult:
        """Compare expression against a list of candidates and evaluate correlation risk."""
        fp_new = cls.extract_fingerprint(expression)
        effective_groupings = set(fp_new.groupings)
        if target_grouping:
            effective_groupings.add(target_grouping.lower())

        comparisons: list[FingerprintComparison] = []
        max_risk = 0.0
        most_similar_id: str | None = None
        most_similar_status: str | None = None
        all_overlapping: set[str] = set()

        for cand in candidates:
            # We compare against APPROVED and NEEDS_REVIEW/VALIDATED alphas
            fp_old = cls.extract_fingerprint(cand.expression_raw)

            # 1. Primary field overlap (most informative)
            shared_primary = fp_new.primary_fields.intersection(fp_old.primary_fields)
            shared_all = fp_new.fields.intersection(fp_old.fields)
            all_overlapping.update(shared_all)

            if not fp_new.fields or not fp_old.fields:
                continue

            jaccard_all = len(shared_all) / len(fp_new.fields.union(fp_old.fields))

            # 2. Grouping alignment
            same_group = bool(effective_groupings.intersection(fp_old.groupings))

            # 3. Calculate estimated self-correlation risk score
            # High risk if sharing identical primary alpha driver and identical grouping
            risk_score = 0.0
            if shared_primary:
                primary_weight = len(shared_primary) / max(len(fp_new.primary_fields), 1)
                risk_score += 0.55 * primary_weight

                # Same grouping adds severe collinearity
                if same_group:
                    risk_score += 0.25

                # Both have price reversal overlay
                if fp_new.has_price_reversal and fp_old.has_price_reversal:
                    risk_score += 0.10
            else:
                # Share generic price fields only
                risk_score = jaccard_all * 0.20

            risk_score = min(round(risk_score, 4), 1.0)

            comp = FingerprintComparison(
                candidate_id=cand.id,
                status=cand.status,
                expression_raw=cand.expression_raw,
                jaccard_similarity=round(jaccard_all, 3),
                overlapping_fields=shared_all,
                same_grouping=same_group,
                estimated_correlation_risk=risk_score,
            )
            comparisons.append(comp)

            if risk_score > max_risk:
                max_risk = risk_score
                most_similar_id = cand.id
                most_similar_status = cand.status

        # Sort comparisons by risk descending
        comparisons.sort(key=lambda x: x.estimated_correlation_risk, reverse=True)

        # Risk classification
        if max_risk >= 0.70:
            risk_level = "HIGH"
        elif max_risk >= 0.45:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        warnings: list[str] = []
        recommendations: list[str] = []

        if risk_level == "HIGH":
            warnings.append(
                f"Gate G3+ Alert: High self-correlation collision risk ({max_risk:.1%}) with {most_similar_status} "
                f"candidate '{most_similar_id[:8] if most_similar_id else 'unknown'}'. "
                f"Shares core driver field(s): {', '.join(sorted(fp_new.primary_fields))}."
            )
            recommendations.append("Switch neutralization domain (e.g. from SECTOR to SUBINDUSTRY, or INDUSTRY).")
            recommendations.append("Alter simulation decay horizon (e.g. test decay=6 or decay=8 instead of decay=4).")
            recommendations.append("Blend with an unmined orthogonal domain (e.g. PV13 customer spillover or OPTION8 VRP).")
        elif risk_level == "MEDIUM":
            warnings.append(
                f"Gate G3+ Notice: Moderate factor overlap ({max_risk:.1%}) detected with candidate "
                f"'{most_similar_id[:8] if most_similar_id else 'unknown'}'."
            )
            recommendations.append("Verify sub-universe Sharpe and ensure lookback or factor weighting is differentiated.")

        return FingerprintAuditResult(
            expression=expression,
            risk_level=risk_level,
            max_risk_score=max_risk,
            most_similar_candidate_id=most_similar_id,
            most_similar_status=most_similar_status,
            overlapping_fields=all_overlapping,
            comparisons=comparisons[:5],  # top 5 closest
            warnings=warnings,
            recommendations=recommendations,
        )

    @classmethod
    def audit_against_database(
        cls,
        expression: str,
        session: Session,
        target_grouping: str | None = None,
    ) -> FingerprintAuditResult:
        """Query APPROVED and evaluated candidates from database and perform pre-simulation audit."""
        candidates = (
            session.query(AlphaCandidate)
            .filter(AlphaCandidate.status.in_(["APPROVED", "NEEDS_REVIEW", "VALIDATED"]))
            .all()
        )
        return cls.audit_against_candidates(expression, candidates, target_grouping=target_grouping)
