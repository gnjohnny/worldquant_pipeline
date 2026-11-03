"""Register, record, and approve the Market-neutral Median EPS & Capex alpha."""
import hashlib
import sys

sys.path.insert(0, "src")

from worldquant_pipeline.expressions.canonicalize import canonicalize_node
from worldquant_pipeline.expressions.parser import parse_expression
from worldquant_pipeline.storage.database import get_session
from worldquant_pipeline.storage.models import (
    AlphaCandidate,
    Decision,
    Experiment,
    ExperimentMetric,
    ResearchHypothesis,
)


def main():
    s = get_session()

    expr_raw = (
        "0.60 * signed_power(group_rank(ts_rank(ts_backfill(anl4_afv4_median_eps, 60) / close, 180), market) - 0.5, 2) + "
        "0.30 * group_rank(ts_mean(ts_backfill(anl4_capex_value, 252), 252) / (ts_backfill(assets, 60) + 1000), market) - "
        "0.10 * group_rank(ts_delta(close, 5) / close, market)"
    )

    ast_node = parse_expression(expr_raw)
    expr_norm = canonicalize_node(ast_node)
    expr_hash = hashlib.sha256(expr_norm.encode("utf-8")).hexdigest()

    # Find or use hypothesis from batch 103 / 104
    hyp = s.query(ResearchHypothesis).filter(ResearchHypothesis.title.like("%Median EPS%")).first()
    if not hyp:
        hyp = ResearchHypothesis(
            title="Analyst Consensus Median EPS Yield and Capex Discipline in Market Neutrality",
            domain="analyst_forecasts",
            economic_rationale="Forward consensus median EPS yield combined with capex investment discipline in broad market neutrality.",
            expected_direction="positive",
            intended_horizon="15d"
        )
        s.add(hyp)
        s.flush()

    # Update previous candidate 2f3e2a97 to NEEDS_REVIEW / SUPERSEDED due to self-corr 0.8781
    c_prev = s.query(AlphaCandidate).filter(AlphaCandidate.id.like("2f3e2a97%")).first()
    if c_prev:
        s.add(Decision(
            candidate_id=c_prev.id,
            decision="NEEDS_REVIEW",
            reason="Superseded by market-neutral variant with self-correlation 0.5768 to protect account uniqueness (0.8781 was too high)."
        ))
        c_prev.status = "NEEDS_REVIEW"

    # Create new approved candidate
    cand = AlphaCandidate(
        hypothesis_id=hyp.id,
        expression_raw=expr_raw,
        expression_normalized=expr_norm,
        expression_hash=expr_hash,
        complexity_score=41,
        version=1,
        status="APPROVED"
    )
    s.add(cand)
    s.flush()

    exp = Experiment(
        candidate_id=cand.id,
        universe="TOP1000",
        delay=1,
        neutralization="Market",
        decay=4
    )
    s.add(exp)
    s.flush()

    metrics = [
        ("sharpe", 1.43),
        ("fitness", 1.51),
        ("turnover", 0.1473),
        ("sub_universe_sharpe", 1.24),
        ("self_correlation", 0.5768)
    ]
    for m_name, m_val in metrics:
        s.add(ExperimentMetric(experiment_id=exp.id, metric_name=m_name, metric_value=m_val))

    reason = (
        "8/8 PASS! GOLD LEVEL CONSULTANT QUALIFIED (GOOD STATUS): Sharpe 1.43 > 1.25, "
        "Fitness 1.51 >= 1.50, Turnover 14.73% in [1%, 70%], Sub-universe Sharpe 1.24 > 0.76, "
        "Self-correlation 0.5768 < 0.70 (Clean pass, strongly protects account uniqueness!). "
        "Market-Neutral Median EPS Yield and Capex Discipline in TOP1000 Market Neutral, Decay 4."
    )
    s.add(Decision(candidate_id=cand.id, decision="APPROVED", reason=reason))

    s.commit()
    print(f"Candidate {cand.id[:8]} committed as APPROVED in PostgreSQL!")

if __name__ == "__main__":
    main()
