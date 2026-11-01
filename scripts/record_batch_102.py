"""Record simulation results for Batch 102."""
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
    c1 = s.query(AlphaCandidate).filter(AlphaCandidate.id.like("c7f04f6d%")).first()
    c2 = s.query(AlphaCandidate).filter(AlphaCandidate.id.like("2703848b%")).first()
    c3 = s.query(AlphaCandidate).filter(AlphaCandidate.id.like("8f22cc52%")).first()

    def record_cand(cand, sharpe, fitness, turnover, sub_sharpe, dec, reason):
        if not cand:
            print("Candidate not found!")
            return
        exp = Experiment(
            candidate_id=cand.id,
            universe="TOP3000",
            delay=1,
            neutralization="Market",
            decay=4
        )
        s.add(exp)
        s.flush()
        metrics = [
            ("sharpe", sharpe),
            ("fitness", fitness),
            ("turnover", turnover),
            ("sub_universe_sharpe", sub_sharpe)
        ]
        for name, val in metrics:
            s.add(ExperimentMetric(experiment_id=exp.id, metric_name=name, metric_value=val))
        s.add(Decision(candidate_id=cand.id, decision=dec, reason=reason))
        cand.status = dec

    record_cand(c1, 0.77, 0.31, 0.3481, 0.80, "REJECTED", "Sharpe 0.77 < 1.25, Fitness 0.31 < 1.0, weight concentration 16.67% on 1/25/2022")
    record_cand(c2, 0.14, 0.04, 0.2555, 0.09, "REJECTED", "Sharpe 0.14 < 1.25, Fitness 0.04 < 1.0, weight concentrated")
    record_cand(c3, -1.29, -0.63, 0.4506, -0.66, "REJECTED", "Sharpe -1.29 < 1.25, Fitness -0.63 < 1.0")

    s.commit()
    print("Batch 102 simulation records committed successfully!")

if __name__ == "__main__":
    main()
