"""Record Candidate 1 (APPROVED) and Candidate 3 (REJECTED) from Batch 104 in PostgreSQL."""
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
    c1 = s.query(AlphaCandidate).filter(AlphaCandidate.id.like("08b9c51d%")).first()
    c3 = s.query(AlphaCandidate).filter(AlphaCandidate.id.like("955c30ab%")).first()

    if c1:
        exp1 = Experiment(
            candidate_id=c1.id,
            universe="TOP1000",
            delay=1,
            neutralization="Sector",
            decay=4
        )
        s.add(exp1)
        s.flush()
        metrics1 = [
            ("sharpe", 1.60),
            ("fitness", 1.50),
            ("turnover", 0.1476),
            ("sub_universe_sharpe", 1.23),
            ("self_correlation", 0.6246)
        ]
        for m_name, m_val in metrics1:
            s.add(ExperimentMetric(experiment_id=exp1.id, metric_name=m_name, metric_value=m_val))
        
        reason1 = (
            "8/8 PASS! GOLD LEVEL CONSULTANT QUALIFIED (GOOD STATUS): Sharpe 1.60 > 1.25, "
            "Fitness 1.50 >= 1.50, Turnover 14.76% in [1%, 70%], Sub-universe Sharpe 1.23 > 0.85, "
            "Self-correlation 0.6246 < 0.70 (Clean pass, low correlation, protects uniqueness!). "
            "Operating Cash Flow Yield from Analyst Estimates and Capex Discipline in TOP1000 Sector Neutral, Decay 4."
        )
        s.add(Decision(candidate_id=c1.id, decision="APPROVED", reason=reason1))
        c1.status = "APPROVED"
        print("Candidate 1 (08b9c51d) committed as APPROVED in PostgreSQL!")

    if c3:
        exp3 = Experiment(
            candidate_id=c3.id,
            universe="TOP1000",
            delay=1,
            neutralization="Market",
            decay=4
        )
        s.add(exp3)
        s.flush()
        metrics3 = [
            ("sharpe", 1.77),
            ("fitness", 1.36),
            ("turnover", 0.2685),
            ("sub_universe_sharpe", 1.27),
            ("self_correlation", 0.8953)
        ]
        for m_name, m_val in metrics3:
            s.add(ExperimentMetric(experiment_id=exp3.id, metric_name=m_name, metric_value=m_val))
        
        reason3 = "7 PASS / 1 FAIL: Self-correlation 0.8953 > 0.70 and Sharpe 1.77 not better by 10%+ against colliding alpha."
        s.add(Decision(candidate_id=c3.id, decision="REJECTED", reason=reason3))
        c3.status = "REJECTED"
        print("Candidate 3 (955c30ab) committed as REJECTED in PostgreSQL!")

    s.commit()
    print("Batch 104 results recorded successfully!")

if __name__ == "__main__":
    main()
