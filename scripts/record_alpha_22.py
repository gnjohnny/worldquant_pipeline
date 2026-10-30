import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from worldquant_pipeline.expressions.canonicalize import canonicalize_expression, compute_expression_hash
from worldquant_pipeline.expressions.validator import ExpressionValidator
from worldquant_pipeline.storage.database import get_session
from worldquant_pipeline.storage.models import (
    AlphaCandidate,
    Decision,
    Experiment,
    ExperimentMetric,
)

raw_expr = (
    "0.60 * signed_power(group_rank(ts_backfill(implied_volatility_call_1080 / parkinson_volatility_180, 60), sector) - 0.5, 2) "
    "+ 0.30 * group_rank(ts_mean(ts_backfill(fn_oth_income_loss_fx_transaction_and_tax_translation_adj_q, 252), 252) / (ts_backfill(assets, 60) + 1000), sector) "
    "- 0.10 * group_rank(ts_delta(close, 5) / close, sector)"
)

with get_session() as session:
    parent = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("5239a25c")).first()
    if not parent:
        print("Parent candidate 5239a25c not found!")
        sys.exit(1)

    val = ExpressionValidator().validate_expression_string(raw_expr)
    if not val.is_valid:
        print("Validation errors:", val.errors)
        sys.exit(1)

    canonical = canonicalize_expression(raw_expr)
    expr_hash = compute_expression_hash(canonical)

    child = session.query(AlphaCandidate).filter_by(expression_hash=expr_hash).first()
    if not child:
        child = AlphaCandidate(
            hypothesis_id=parent.hypothesis_id,
            parent_candidate_id=parent.id,
            expression_raw=raw_expr,
            expression_normalized=canonical,
            expression_hash=expr_hash,
            complexity_score=val.node_count,
            version=2,
            status="APPROVED",
        )
        session.add(child)
        session.flush()
    else:
        child.status = "APPROVED"

    exp = Experiment(
        candidate_id=child.id,
        status="COMPLETED",
        universe="TOP1000",
        delay=1,
        decay=5,
        neutralization="Sector",
        truncation=0.0100,
    )
    session.add(exp)
    session.flush()

    metrics = {
        "sharpe": 1.77,
        "fitness": 1.85,
        "turnover": 0.1119,
        "sub_universe_sharpe": 1.65,
        "self_correlation": 0.6311,
    }
    for k, v in metrics.items():
        session.add(ExperimentMetric(experiment_id=exp.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))

    dec = Decision(
        candidate_id=child.id,
        decision="APPROVED",
        reason="8/8 PASS! GOLD LEVEL CONSULTANT QUALIFIED (EXCELLENT STATUS): Sharpe 1.77 > 1.25, Fitness 1.85 >= 1.80 (EXCELLENT), Turnover 11.19% in [1%, 70%], Sub-universe Sharpe 1.65 > 0.94, Self-correlation 0.6311 < 0.70. 3-Year LEAP Call IV (1080d) & Quarterly FX Translation in TOP1000 Sector Neutral.",
        reviewer="HUMAN_RESEARCHER",
    )
    session.add(dec)

    session.commit()
    print(f"Candidate {child.id} successfully APPROVED and recorded as Alpha 22 in PostgreSQL.")
