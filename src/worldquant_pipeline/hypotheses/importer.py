"""Batch JSON ingestion and validation for candidate alphas."""
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session

from worldquant_pipeline.exceptions import (
    ASTSyntaxError,
    WorldQuantPipelineError,
)
from worldquant_pipeline.expressions.canonicalize import (
    canonicalize_expression,
    compute_expression_hash,
)
from worldquant_pipeline.expressions.validator import ExpressionValidator
from worldquant_pipeline.hypotheses.schemas import CandidateBatchInput
from worldquant_pipeline.storage.models import AlphaCandidate, ResearchHypothesis


@dataclass
class IngestionReport:
    """Summary of batch ingestion results."""
    total_hypotheses: int = 0
    total_candidates: int = 0
    valid_candidates: int = 0
    duplicates: int = 0
    syntax_errors: int = 0
    registered_candidates: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, str]] = field(default_factory=list)


class HypothesisImporter:
    """Validates and registers candidate hypotheses and expressions into PostgreSQL."""

    def __init__(
        self,
        session: Session,
        validator: ExpressionValidator | None = None,
    ) -> None:
        self.session = session
        self.validator = validator or ExpressionValidator()

    def ingest_data(self, data: dict) -> IngestionReport:
        """Parse raw dictionary, validate schema, validate ASTs, and register candidates."""
        batch = CandidateBatchInput.model_validate(data)
        report = IngestionReport()
        report.total_hypotheses = len(batch.hypotheses)

        for hypo_proposal in batch.hypotheses:
            # 1. Create Hypothesis in database
            hypothesis = ResearchHypothesis(
                title=hypo_proposal.title,
                domain=hypo_proposal.domain,
                economic_rationale=hypo_proposal.economic_rationale,
                expected_direction=hypo_proposal.expected_direction.value,
                intended_horizon=hypo_proposal.intended_horizon,
                confounders=hypo_proposal.confounders,
                falsification_test=hypo_proposal.falsification_test,
                status="ACTIVE",
            )
            self.session.add(hypothesis)
            self.session.flush()  # Populates hypothesis.id

            for cand_proposal in hypo_proposal.candidates:
                report.total_candidates += 1
                expr_raw = cand_proposal.expression.strip()

                # 2. Gate G1: Deterministic AST Syntax & Whitelist Validation
                try:
                    validation_res = self.validator.validate_expression_string(expr_raw)
                    if not validation_res.is_valid:
                        report.syntax_errors += 1
                        report.errors.append({
                            "expression": expr_raw,
                            "reason": "; ".join(validation_res.errors),
                        })
                        continue
                except ASTSyntaxError as e:
                    report.syntax_errors += 1
                    report.errors.append({
                        "expression": expr_raw,
                        "reason": f"Syntax Error: {e}",
                    })
                    continue
                except WorldQuantPipelineError as e:
                    report.syntax_errors += 1
                    report.errors.append({
                        "expression": expr_raw,
                        "reason": str(e),
                    })
                    continue

                # 3. Canonicalize & Compute SHA-256 Hash
                canonical_expr = canonicalize_expression(expr_raw)
                expr_hash = compute_expression_hash(canonical_expr)

                # 4. Gate G3: Deduplication check
                existing = (
                    self.session.query(AlphaCandidate)
                    .filter_by(expression_hash=expr_hash)
                    .first()
                )
                if existing:
                    report.duplicates += 1
                    report.errors.append({
                        "expression": expr_raw,
                        "reason": f"Duplicate of existing candidate ID: {existing.id}",
                    })
                    continue

                # 5. Register Valid Candidate
                candidate = AlphaCandidate(
                    hypothesis_id=hypothesis.id,
                    expression_raw=expr_raw,
                    expression_normalized=canonical_expr,
                    expression_hash=expr_hash,
                    complexity_score=validation_res.node_count,
                    version=1,
                    status="VALIDATED",
                )
                self.session.add(candidate)
                self.session.flush()

                report.valid_candidates += 1
                report.registered_candidates.append({
                    "id": candidate.id,
                    "expression": expr_raw,
                    "canonical": canonical_expr,
                    "complexity": candidate.complexity_score,
                })

        self.session.commit()
        return report
