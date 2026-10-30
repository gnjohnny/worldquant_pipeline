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
    "0.60 * signed_power(group_rank(ts_rank(ts_backfill(adj_net_income_avg, 60) / close, 180), industry) - 0.5, 2) "
    "+ 0.30 * group_rank(ts_mean(ts_backfill(fn_oth_income_loss_fx_transaction_and_tax_translation_adj_q, 252), 252) / (ts_backfill(assets, 60) + 1000), industry) "
    "- 0.10 * group_rank(ts_delta(close, 5) / close, industry)"
)

with get_session() as session:
    parent = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("5a99ec00")).first()
    if not parent:
        print("Parent candidate 5a99ec00 not found!")
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
        universe="TOP2000",
        delay=1,
        decay=5,
        neutralization="Market",
        truncation=0.0100,
    )
    session.add(exp)
    session.flush()

    metrics = {
        "sharpe": 1.58,
        "fitness": 1.64,
        "turnover": 0.1223,
        "sub_universe_sharpe": 1.42,
        "self_correlation": 0.5958,
    }
    for k, v in metrics.items():
        session.add(ExperimentMetric(experiment_id=exp.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))

    dec = Decision(
        candidate_id=child.id,
        decision="APPROVED",
        reason="8/8 PASS! GOLD LEVEL CONSULTANT QUALIFIED: Sharpe 1.58 > 1.25, Fitness 1.64 >= 1.50 (GOOD), Turnover 12.23% in [1%, 70%], Sub-universe Sharpe 1.42 > 0.84, Self-correlation 0.5958 < 0.70 (DECORRELATED BREAKTHROUGH!). Consensus Forward Net Income Yield & Quarterly Audited FX Translation in TOP2000 Market Neutral.",
        reviewer="HUMAN_RESEARCHER",
    )
    session.add(dec)

    session.commit()
    print(f"Candidate {child.id} successfully APPROVED and recorded as Alpha 21 in PostgreSQL.")
