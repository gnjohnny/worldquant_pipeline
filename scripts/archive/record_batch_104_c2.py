"""Record approved Candidate 2 from Batch 104 in PostgreSQL."""
import sys

sys.path.insert(0, "src")
from worldquant_pipeline.storage.database import get_session
from worldquant_pipeline.storage.models import (
    AlphaCandidate,
    Decision,
    Experiment,
    ExperimentMetric,
)


def main():
    s = get_session()
    cand = s.query(AlphaCandidate).filter(AlphaCandidate.id.like("2f3e2a97%")).first()
    if not cand:
        print("Candidate 2f3e2a97 not found!")
        return

    exp = Experiment(
        candidate_id=cand.id,
        universe="TOP1000",
        delay=1,
        neutralization="Sector",
        decay=4
    )
    s.add(exp)
    s.flush()

    metrics = [
        ("sharpe", 1.72),
        ("fitness", 1.58),
        ("turnover", 0.1542),
        ("sub_universe_sharpe", 1.43),
        ("self_correlation", 0.8781)
    ]
    for m_name, m_val in metrics:
        s.add(ExperimentMetric(experiment_id=exp.id, metric_name=m_name, metric_value=m_val))

    reason = (
        "8/8 PASS! GOLD LEVEL CONSULTANT QUALIFIED (GOOD STATUS): Sharpe 1.72 > 1.25, "
        "Fitness 1.58 >= 1.50, Turnover 15.42% in [1%, 70%], Sub-universe Sharpe 1.43 > 0.91, "
        "Self-correlation 0.8781 (Passed platform 10%+ Sharpe dominance rule). "
        "Intra-Subindustry Median EPS Valuation & Revision Momentum Synergy in TOP1000 Sector Neutral, Decay 4."
    )
    s.add(Decision(candidate_id=cand.id, decision="APPROVED", reason=reason))
    cand.status = "APPROVED"

    s.commit()
    print("Candidate 2 (2f3e2a97) committed as APPROVED in PostgreSQL research memory!")

if __name__ == "__main__":
    main()
