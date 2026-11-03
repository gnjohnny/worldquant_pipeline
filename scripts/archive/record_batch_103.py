"""Record simulation results for Batch 103."""
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
    c1 = s.query(AlphaCandidate).filter(AlphaCandidate.id.like("f5e17f66%")).first()
    c2 = s.query(AlphaCandidate).filter(AlphaCandidate.id.like("366e49be%")).first()
    c3 = s.query(AlphaCandidate).filter(AlphaCandidate.id.like("00a36b43%")).first()

    def record_cand(cand, sharpe, fitness, turnover, sub_sharpe, self_corr, dec, reason, neut="Market", decay=4):
        if not cand:
            print("Candidate not found!")
            return
        exp = Experiment(
            candidate_id=cand.id,
            universe="TOP1000",
            delay=1,
            neutralization=neut,
            decay=decay
        )
        s.add(exp)
        s.flush()
        metrics = [
            ("sharpe", sharpe),
            ("fitness", fitness),
            ("turnover", turnover),
            ("sub_universe_sharpe", sub_sharpe)
        ]
        if self_corr is not None:
            metrics.append(("self_correlation", self_corr))
        for name, val in metrics:
            s.add(ExperimentMetric(experiment_id=exp.id, metric_name=name, metric_value=val))
        s.add(Decision(candidate_id=cand.id, decision=dec, reason=reason))
        cand.status = dec

    record_cand(c1, 1.09, 0.93, 0.1127, 1.29, None, "REJECTED", "Sharpe 1.09 < 1.25, Fitness 0.93 < 1.0", neut="Market", decay=4)
    record_cand(c2, 1.43, 1.51, 0.1473, 1.24, 0.5768, "NEEDS_REVIEW", "8/8 PASS! GOOD STATUS on platform: Sharpe 1.43 > 1.25, Fitness 1.51 >= 1.50, Turnover 14.73%, Self-corr 0.5768 < 0.70. Held for optimization to reach >= 1.80.", neut="Market", decay=4)
    record_cand(c3, 0.54, 0.40, 0.1346, 0.60, None, "REJECTED", "Sharpe 0.54 < 1.25, Fitness 0.40 < 1.0", neut="Market", decay=4)

    s.commit()
    print("Batch 103 simulation records committed successfully!")

if __name__ == "__main__":
    main()
