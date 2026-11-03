"""Record simulation results and decisions for Batch 109 in PostgreSQL."""
import sys

sys.path.insert(0, "src")
from worldquant_pipeline.storage.database import get_session
from worldquant_pipeline.storage.models import (
    AlphaCandidate,
    Decision,
    Experiment,
    ExperimentMetric,
)


def record_batch_109():
    session = get_session()

    # Candidate 1: 02637423
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.like("02637423%")).first()
    if c1:
        c1.status = "REJECTED"
        exp1 = Experiment(
            candidate_id=c1.id,
            universe="TOP1000",
            neutralization="Sector",
            decay=4,
            truncation=0.01,
        )
        session.add(exp1)
        session.flush()
        session.add_all([
            ExperimentMetric(experiment_id=exp1.id, metric_name="sharpe", metric_value=1.18),
            ExperimentMetric(experiment_id=exp1.id, metric_name="fitness", metric_value=1.00),
            ExperimentMetric(experiment_id=exp1.id, metric_name="turnover", metric_value=0.1448),
            ExperimentMetric(experiment_id=exp1.id, metric_name="subuniverse_sharpe", metric_value=0.95),
        ])
        session.add(Decision(
            candidate_id=c1.id,
            decision="REJECTED",
            reason="Sharpe 1.18 < 1.25 cutoff, Fitness 1.00 < 1.50 approval cutoff.",
        ))

    # Candidate 2: c5cd79fe
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.like("c5cd79fe%")).first()
    if c2:
        c2.status = "REJECTED"
        exp2 = Experiment(
            candidate_id=c2.id,
            universe="TOP1000",
            neutralization="Sector",
            decay=4,
            truncation=0.01,
        )
        session.add(exp2)
        session.flush()
        session.add_all([
            ExperimentMetric(experiment_id=exp2.id, metric_name="sharpe", metric_value=0.97),
            ExperimentMetric(experiment_id=exp2.id, metric_name="fitness", metric_value=0.65),
            ExperimentMetric(experiment_id=exp2.id, metric_name="turnover", metric_value=0.1575),
            ExperimentMetric(experiment_id=exp2.id, metric_name="subuniverse_sharpe", metric_value=0.81),
        ])
        session.add(Decision(
            candidate_id=c2.id,
            decision="REJECTED",
            reason="Sharpe 0.97 < 1.25 cutoff, Fitness 0.65 < 1.0 cutoff.",
        ))

    # Candidate 3: 469370bc
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.like("469370bc%")).first()
    if c3:
        c3.status = "REJECTED"
        exp3 = Experiment(
            candidate_id=c3.id,
            universe="TOP1000",
            neutralization="Sector",
            decay=4,
            truncation=0.01,
        )
        session.add(exp3)
        session.flush()
        session.add_all([
            ExperimentMetric(experiment_id=exp3.id, metric_name="sharpe", metric_value=0.73),
            ExperimentMetric(experiment_id=exp3.id, metric_name="fitness", metric_value=0.43),
            ExperimentMetric(experiment_id=exp3.id, metric_name="turnover", metric_value=0.1539),
            ExperimentMetric(experiment_id=exp3.id, metric_name="subuniverse_sharpe", metric_value=0.64),
        ])
        session.add(Decision(
            candidate_id=c3.id,
            decision="REJECTED",
            reason="Sharpe 0.73 < 1.25 cutoff, Fitness 0.43 < 1.0 cutoff.",
        ))

    session.commit()
    print("Batch 109 results and decisions recorded successfully in PostgreSQL!")


if __name__ == "__main__":
    record_batch_109()
